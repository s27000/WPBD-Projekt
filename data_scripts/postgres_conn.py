import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_conn_cursor():
    CONN = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=5432,
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

    return CONN, CONN.cursor()
