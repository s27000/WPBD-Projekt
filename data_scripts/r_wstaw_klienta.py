import postgres_conn as pg_conn

def main():
    print("--- DODAWANIE NOWEGO KLIENTA ---")
    id_klienta = input("ID Klienta: ")
    imie = input("Imię: ")
    nazwisko = input("Nazwisko: ")
    telefon = input("Telefon: ")
    email = input("Email: ")

    conn, cursor = pg_conn.get_conn_cursor()
    try:
        query = """
            INSERT INTO klienci ("idKlienta", "imie", "nazwisko", "telefon", "email") 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (id_klienta, imie, nazwisko, telefon, email))
        conn.commit()
        print(f"[OK] Klient '{imie} {nazwisko}' został dodany.")
    except Exception as e:
        print(f"[BŁĄD] {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()