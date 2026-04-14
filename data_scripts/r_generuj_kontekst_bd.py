import pandas as pd
import os

import postgres_conn as pg_conn

# STAŁE WARTOŚCI
DB_CONTEXT_DIR = './data'
CSV_FILES = {
    "albumy.csv": "albumy",
    "klienci.csv": "klienci",
    "zamowienia.csv": "zamowienia"
}

## Połączenie z DB PostgreSQL
CONN, CURSOR = pg_conn.get_conn_cursor()

# TWORZENIE TABELI NA PODSTAWIE PLIKU CSV
def create_table_from_csv(csv_file, table_name):
    df = pd.read_csv(csv_file)
    headers = df.columns.tolist()
    columns_list = []

    # Jeżeli, pole zaczyna się od id -> KLUCZ GŁÓWNY TYPU INTEGER
    # w przeciwnym wypadku -> TEXT
    for h in headers:
        if h.lower().startswith('id'):
            columns_list.append(f'"{h}" INTEGER PRIMARY KEY')
        else:
            columns_list.append(f'"{h}" TEXT')

    columns = ', '.join(columns_list)
    create_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns});'
    CURSOR.execute(create_query)
    
    # dla Debezium
    CURSOR.execute(f'ALTER TABLE {table_name} REPLICA IDENTITY FULL;')
    print(f"[INFO] Stworzono nową tabelę: {table_name}")

# WSTAWIANIE DANYCH Z PLIKU CSV DO TABELI
def insert_data_from_csv(csv_file, table_name):
    df = pd.read_csv(csv_file)
    headers = df.columns.tolist()
    columns = ', '.join([f'"{h}"' for h in headers])
    placeholders = ', '.join(['%s'] * len(headers))
    insert_query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
    for _, row in df.iterrows():
        CURSOR.execute(insert_query, row.tolist())
    print(f"[INFO] Uzupełnianich danych w tabeli {table_name}...")


def main():
    for csv_file, table_name in CSV_FILES.items():
        csv_path = os.path.join(DB_CONTEXT_DIR, csv_file)
        create_table_from_csv(csv_path, table_name)
        insert_data_from_csv(csv_path, table_name)

    CONN.commit()
    CURSOR.close()
    CONN.close()
    print(f"[INFO] Wszystkie dane zostały pomyślnie załadowane!")

if __name__ == "__main__":
    main()