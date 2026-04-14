import json
import os
from datetime import datetime
from kafka import KafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPICS = [
    "dbserver1.public.klienci",
    "dbserver1.public.albumy",
    "dbserver1.public.zamowienia",
]

OP_LABELS = {
    "c": "INSERT",
    "u": "UPDATE",
    "d": "DELETE",
    "r": "READ (snapshot)",
}


def create_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        *TOPICS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="debezium-cdc-consumer",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda raw: json.loads(raw.decode("utf-8")) if raw else None,
        key_deserializer=lambda raw: json.loads(raw.decode("utf-8")) if raw else None,
    )


def print_message(topic: str, key, value) -> None:
    if value is None:
        print(f"\n[{datetime.now().isoformat(timespec='milliseconds')}][{topic}] TOMBSTONE | key={key}")
        return

    op_code = value.get("__op", "?")
    table = value.get("__table", topic.split(".")[-1])
    op_label = OP_LABELS.get(op_code, f"UNKNOWN ({op_code})")

    record = {k: v for k, v in value.items() if not k.startswith("__")}

    print(f"\n[{datetime.now().isoformat(timespec='milliseconds')}] [{table}] {op_label}")
    print(f"  key   : {key}")
    print(f"  record: {json.dumps(record, ensure_ascii=False, indent=4)}")


def main() -> None:
    print(f"[INFO] Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"[INFO] Subscribing to topics: {TOPICS}")
    print(f"[INFO] Waiting for messages... (Ctrl+C to stop)\n")

    consumer = create_consumer()

    os.makedirs("/consumer_flag", exist_ok=True)
    with open("/consumer_flag/ready", "w") as f:
        f.write("ready")
    print("[INFO] Flaga gotowości kafka-consumera ustawiona")

    try:
        for msg in consumer:
            print_message(msg.topic, msg.key, msg.value)
            print("-" * 80)
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Stopped by user.")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
