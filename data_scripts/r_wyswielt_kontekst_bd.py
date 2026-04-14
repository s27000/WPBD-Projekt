import pandas as pd
import os

import postgres_conn as pg_conn

def clear_screen():
    os.system('cls')

def display_table(conn, table_name):
    try:
        df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
        print(f"\n--- Tabela: {table_name} ---")
        if df.empty:
            print("[INFO] Tabela jest pusta.")
        else:
            print(df.to_string(index=False))
    except Exception as e:
        print(f"[BŁĄD] Nie można odczytać tabeli {table_name}: {e}")

def main():
    conn, cursor = pg_conn.get_conn_cursor()

    table_map = {
        "1": "klienci",
        "2": "albumy",
        "3": "zamowienia"
    }

    while True:
        print("\n" + "="*30)
        print("MENU PRZEGLĄDANIA TABEL")
        print("="*30)
        print("1 - Tabela z klientami")
        print("2 - Tabela z albumami")
        print("3 - Tabela zamówień")
        print("a - Wszystkie tabele")
        print("q - Wyjście")
        
        choice = input("\nWybierz opcję: ").lower()

        if choice == 'q':
            print("Zamykanie...")
            break
        
        os.system('cls')

        if choice in table_map:
            display_table(conn, table_map[choice])
        elif choice == 'a':
            for name in table_map.values():
                display_table(conn, name)
        else:
            print("Nieprawidłowa opcja, spróbuj ponownie.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()