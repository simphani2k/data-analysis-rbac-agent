import os
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")

def test_connection():
    """Test PostgreSQL connection and print version."""
    try:
        with psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        ) as conn:
            print("✅ Connection successful!")

            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print("PostgreSQL version:", version)

    except OperationalError as e:
        print("❌ Connection failed:", e)
    except Exception as e:
        print("⚠️ Unexpected error:", e)

if __name__ == "__main__":
    test_connection()