-- Enable logical replication for Debezium
ALTER SYSTEM SET wal_level = 'logical';
ALTER SYSTEM SET max_wal_senders = 4;
ALTER SYSTEM SET max_replication_slots = 4;