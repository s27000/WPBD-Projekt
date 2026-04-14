import postgres_conn as pg_conn

def main():
    print("--- DODAWANIE NOWEGO ZAMÓWIENIA ---")
    id_zamowienia = input("ID Zamówienia: ")
    klient_id = input("ID Klienta: ")
    album_id = input("ID Albumu: ")
    adres = input("Adres dostawy: ")
    data_zlozenia = input("Data złożenia (YYYY-MM-DD): ")

    conn, cursor = pg_conn.get_conn_cursor()
    try:
        query = """
            INSERT INTO zamowienia ("idZamowienia", "KlientId", "AlbumId", "adresDostawy", "dataZlozeniaZamowienia") 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (id_zamowienia, klient_id, album_id, adres, data_zlozenia))
        conn.commit()
        print(f"[OK] Zamówienie nr {id_zamowienia} zostało dodane.")
    except Exception as e:
        print(f"[BŁĄD] {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()