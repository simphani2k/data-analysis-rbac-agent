#!/usr/bin/env python3
"""
Simple Database Connection Test

Quick test to verify database connectivity and show available data.
"""

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
    """Test PostgreSQL connection and show database contents."""
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    print(f"Host: {DB_HOST}")
    print(f"Database: {DB_NAME}")
    print(f"User: {DB_USER}")
    print("=" * 60)

    try:
        with psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            connect_timeout=10
        ) as conn:
            print("\n✅ Connection successful!")

            with conn.cursor() as cur:
                # Get PostgreSQL version
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                print(f"\n📊 PostgreSQL version: {version[:60]}...")

                # Get all schemas
                cur.execute("""
                    SELECT schema_name
                    FROM information_schema.schemata
                    WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
                    ORDER BY schema_name;
                """)
                schemas = cur.fetchall()

                print(f"\n📁 Available schemas: {len(schemas)}")
                for schema in schemas:
                    print(f"   - {schema[0]}")

                # Check contiso schema specifically
                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'contiso'
                    ORDER BY table_name;
                """)
                tables = cur.fetchall()

                if tables:
                    print(f"\n📊 Tables in 'contiso' schema: {len(tables)}")
                    print("\nSample table data:")

                    # Show row counts for key tables
                    key_tables = ['dimcustomer', 'dimproduct', 'dimstore',
                                  'factsales', 'factonlinesales', 'factinventory']

                    for table in key_tables:
                        try:
                            cur.execute(f"SELECT COUNT(*) FROM contiso.{table};")
                            count = cur.fetchone()[0]
                            print(f"   ✅ {table}: {count:,} rows")
                        except Exception:
                            pass
                else:
                    print("\n⚠️  No tables found in 'contiso' schema")

                print("\n" + "=" * 60)
                print("✅ TEST PASSED - Database is accessible")
                print("=" * 60)

    except OperationalError as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("   1. Verify RDS endpoint is correct")
        print("   2. Check security group allows inbound on port 5432")
        print("   3. Verify database credentials in .env file")
        print("   4. Ensure your IP is whitelisted in security group")
    except Exception as e:
        print(f"\n⚠️ Unexpected error: {e}")


if __name__ == "__main__":
    test_connection()