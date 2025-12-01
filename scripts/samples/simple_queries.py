#!/usr/bin/env python3
"""
Simple Retail Data Queries

Basic examples of querying the Contoso database.
These queries demonstrate how to connect and retrieve data.

Usage:
    python scripts/samples/simple_queries.py
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_connection():
    """Create and return database connection."""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        port=os.getenv('DB_PORT')
    )


def print_header(title):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def query_1_table_counts():
    """Example 1: Get row counts for all tables."""
    print_header("Query 1: Table Row Counts")

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT
            table_name,
            (SELECT COUNT(*) FROM contiso. || table_name) as row_count
        FROM information_schema.tables
        WHERE table_schema = 'contiso'
        ORDER BY table_name;
    """

    # Simpler approach - query each table individually
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'contiso'
        ORDER BY table_name;
    """)

    tables = cursor.fetchall()

    print(f"\nFound {len(tables)} tables:\n")
    for table in tables:
        table_name = table['table_name']
        cursor.execute(f"SELECT COUNT(*) as count FROM contiso.{table_name};")
        count = cursor.fetchone()['count']
        print(f"  {table_name:30} {count:>15,} rows")

    cursor.close()
    conn.close()


def query_2_sample_customers():
    """Example 2: Get sample customer data."""
    print_header("Query 2: Sample Customer Data (First 5)")

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT *
        FROM contiso.dimcustomer
        LIMIT 5;
    """

    cursor.execute(query)
    customers = cursor.fetchall()

    for i, customer in enumerate(customers, 1):
        print(f"\nCustomer {i}:")
        for key, value in customer.items():
            print(f"  {key}: {value}")

    cursor.close()
    conn.close()


def query_3_sample_products():
    """Example 3: Get sample product data."""
    print_header("Query 3: Sample Product Data (First 5)")

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT *
        FROM contiso.dimproduct
        LIMIT 5;
    """

    cursor.execute(query)
    products = cursor.fetchall()

    for i, product in enumerate(products, 1):
        print(f"\nProduct {i}:")
        for key, value in product.items():
            print(f"  {key}: {value}")

    cursor.close()
    conn.close()


def query_4_stores_by_country():
    """Example 4: Count stores by country."""
    print_header("Query 4: Stores by Country")

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT
            g."RegionCountryName" as country,
            COUNT(*) as store_count
        FROM contiso.dimstore s
        LEFT JOIN contiso.dimgeography g ON s."GeographyKey" = g."GeographyKey"
        WHERE g."RegionCountryName" IS NOT NULL
        GROUP BY g."RegionCountryName"
        ORDER BY store_count DESC;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    print(f"\nStores by Country:\n")
    for row in results:
        print(f"  {row['country']:30} {row['store_count']:>5} stores")

    cursor.close()
    conn.close()


def query_5_product_categories():
    """Example 5: Get product categories."""
    print_header("Query 5: Product Categories")

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT *
        FROM contiso.dimproductcategory
        ORDER BY "ProductCategoryName";
    """

    cursor.execute(query)
    results = cursor.fetchall()

    print(f"\nAvailable Product Categories:\n")
    for row in results:
        print(f"  [{row['ProductCategoryKey']}] {row['ProductCategoryName']}")

    cursor.close()
    conn.close()


def query_6_date_range():
    """Example 6: Get date range of sales data."""
    print_header("Query 6: Sales Data Date Range")

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT
            MIN("CalendarYear") as earliest_year,
            MAX("CalendarYear") as latest_year,
            COUNT(DISTINCT "CalendarYear") as num_years
        FROM contiso.dimdate;
    """

    cursor.execute(query)
    result = cursor.fetchone()

    print(f"\nDate Range:")
    print(f"  Earliest Year: {result['earliest_year']}")
    print(f"  Latest Year: {result['latest_year']}")
    print(f"  Total Years: {result['num_years']}")

    cursor.close()
    conn.close()


def main():
    """Run all sample queries."""
    print("\n" + "=" * 70)
    print("  CONTOSO DATABASE - SIMPLE QUERY EXAMPLES")
    print("=" * 70)

    try:
        # Run all example queries
        query_1_table_counts()
        query_2_sample_customers()
        query_3_sample_products()
        query_4_stores_by_country()
        query_5_product_categories()
        query_6_date_range()

        print("\n" + "=" * 70)
        print("  ✅ All queries completed successfully!")
        print("=" * 70)
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
