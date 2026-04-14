import postgres_conn as pg_conn

def main():
    print("--- DODAWANIE NOWEGO ALBUMU ---")
    id_albumu = input("ID Albumu: ")
    tytul = input("Tytuł: ")
    wykonawca = input("Wykonawca: ")
    gatunek = input("Gatunek: ")
    wytwornia = input("Wytwórnia: ")
    data_wydania = input("Data wydania (YYYY-MM-DD): ")
    cena = input("Cena: ")

    conn, cursor = pg_conn.get_conn_cursor()
    try:
        query = """
            INSERT INTO albumy ("idAlbumu", "tytul", "wykonawca", "gatunek", "wytwornia", "dataWydania", "cena") 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (id_albumu, tytul, wykonawca, gatunek, wytwornia, data_wydania, cena))
        conn.commit()
        print(f"[OK] Album '{tytul}' został dodany.")
    except Exception as e:
        print(f"[BŁĄD] {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()