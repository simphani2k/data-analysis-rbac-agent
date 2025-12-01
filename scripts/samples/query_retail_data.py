#!/usr/bin/env python3
"""
Sample Retail Data Analysis Queries

This script demonstrates various queries for analyzing the Contoso retail dataset.
Use these examples as a starting point for your data analysis needs.

Usage:
    python scripts/samples/query_retail_data.py
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()


class RetailDataAnalyzer:
    """Query and analyze Contoso retail data."""

    def __init__(self):
        """Initialize database connection."""
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            port=os.getenv('DB_PORT')
        )

    def execute_query(self, query: str, params=None):
        """Execute query and return results as list of dictionaries."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def get_sales_summary(self):
        """Get overall sales summary."""
        query = """
            SELECT
                COUNT(DISTINCT "SalesKey") as total_transactions,
                SUM(CAST("SalesAmount" AS NUMERIC)) as total_sales,
                AVG(CAST("SalesAmount" AS NUMERIC)) as avg_transaction_value,
                MIN("DateKey") as earliest_sale,
                MAX("DateKey") as latest_sale
            FROM contiso.factsales;
        """
        return self.execute_query(query)[0]

    def get_top_products(self, limit=10):
        """Get top selling products by revenue."""
        query = """
            SELECT
                p.productname,
                p.productcategoryname,
                COUNT(DISTINCT s.saleskey) as num_transactions,
                SUM(s.salesquantity) as total_quantity_sold,
                SUM(s.salesamount) as total_revenue,
                AVG(s.salesamount) as avg_sale_amount
            FROM contiso.factsales s
            JOIN contiso.dimproduct p ON s.productkey = p.productkey
            GROUP BY p.productname, p.productcategoryname
            ORDER BY total_revenue DESC
            LIMIT %s;
        """
        return self.execute_query(query, (limit,))

    def get_sales_by_channel(self):
        """Get sales breakdown by channel."""
        query = """
            SELECT
                c.channelname,
                COUNT(DISTINCT s.saleskey) as num_transactions,
                SUM(s.salesamount) as total_revenue,
                AVG(s.salesamount) as avg_transaction_value
            FROM contiso.factsales s
            JOIN contiso.dimchannel c ON s.channelkey = c.channelkey
            GROUP BY c.channelname
            ORDER BY total_revenue DESC;
        """
        return self.execute_query(query)

    def get_sales_by_store(self, limit=10):
        """Get top performing stores."""
        query = """
            SELECT
                st.storename,
                st.storetype,
                g.cityname,
                g.regioncountryname,
                COUNT(DISTINCT s.saleskey) as num_transactions,
                SUM(s.salesamount) as total_revenue
            FROM contiso.factsales s
            JOIN contiso.dimstore st ON s.storekey = st.storekey
            LEFT JOIN contiso.dimgeography g ON st.geographykey = g.geographykey
            GROUP BY st.storename, st.storetype, g.cityname, g.regioncountryname
            ORDER BY total_revenue DESC
            LIMIT %s;
        """
        return self.execute_query(query, (limit,))

    def get_customer_demographics(self):
        """Get customer demographics summary."""
        query = """
            SELECT
                gender,
                COUNT(*) as customer_count,
                AVG(yearlyincome) as avg_income,
                AVG(totalchildren) as avg_children
            FROM contiso.dimcustomer
            WHERE gender IS NOT NULL
            GROUP BY gender
            ORDER BY customer_count DESC;
        """
        return self.execute_query(query)

    def get_online_vs_store_sales(self):
        """Compare online vs in-store sales."""
        query_store = """
            SELECT
                'Store Sales' as channel,
                COUNT(DISTINCT saleskey) as transactions,
                SUM(salesamount) as revenue
            FROM contiso.factsales;
        """

        query_online = """
            SELECT
                'Online Sales' as channel,
                COUNT(DISTINCT onlinesaleskey) as transactions,
                SUM(salesamount) as revenue
            FROM contiso.factonlinesales;
        """

        store_sales = self.execute_query(query_store)
        online_sales = self.execute_query(query_online)

        return store_sales + online_sales

    def get_monthly_sales_trend(self, year=None):
        """Get monthly sales trend for a specific year or all years."""
        if year:
            query = """
                SELECT
                    d.calendaryear,
                    d.calendarmonth,
                    d.monthlabel,
                    COUNT(DISTINCT s.saleskey) as transactions,
                    SUM(s.salesamount) as revenue
                FROM contiso.factsales s
                JOIN contiso.dimdate d ON s.datekey = d.datekey
                WHERE d.calendaryear = %s
                GROUP BY d.calendaryear, d.calendarmonth, d.monthlabel
                ORDER BY d.calendarmonth;
            """
            return self.execute_query(query, (year,))
        else:
            query = """
                SELECT
                    d.calendaryear,
                    d.calendarmonth,
                    d.monthlabel,
                    COUNT(DISTINCT s.saleskey) as transactions,
                    SUM(s.salesamount) as revenue
                FROM contiso.factsales s
                JOIN contiso.dimdate d ON s.datekey = d.datekey
                GROUP BY d.calendaryear, d.calendarmonth, d.monthlabel
                ORDER BY d.calendaryear, d.calendarmonth;
            """
            return self.execute_query(query)

    def get_inventory_status(self, product_name=None):
        """Get current inventory status."""
        if product_name:
            query = """
                SELECT
                    p.productname,
                    st.storename,
                    i.onhandquantity,
                    i.onsalesquantity,
                    d.fulldatealternatekey as inventory_date
                FROM contiso.factinventory i
                JOIN contiso.dimproduct p ON i.productkey = p.productkey
                JOIN contiso.dimstore st ON i.storekey = st.storekey
                JOIN contiso.dimdate d ON i.datekey = d.datekey
                WHERE p.productname ILIKE %s
                AND i.datekey = (SELECT MAX(datekey) FROM contiso.factinventory)
                ORDER BY i.onhandquantity DESC
                LIMIT 20;
            """
            return self.execute_query(query, (f'%{product_name}%',))
        else:
            query = """
                SELECT
                    p.productname,
                    SUM(i.onhandquantity) as total_on_hand,
                    SUM(i.onsalesquantity) as total_on_sales,
                    COUNT(DISTINCT i.storekey) as num_stores
                FROM contiso.factinventory i
                JOIN contiso.dimproduct p ON i.productkey = p.productkey
                WHERE i.datekey = (SELECT MAX(datekey) FROM contiso.factinventory)
                GROUP BY p.productname
                ORDER BY total_on_hand DESC
                LIMIT 20;
            """
            return self.execute_query(query)

    def close(self):
        """Close database connection."""
        self.conn.close()


def print_section(title):
    """Print section header."""
    print("\n" + "=" * 70)
    print(title.center(70))
    print("=" * 70)


def print_results(results, title=None):
    """Print query results in a formatted way."""
    if title:
        print(f"\n{title}")
        print("-" * 70)

    if not results:
        print("No results found.")
        return

    for row in results:
        for key, value in row.items():
            if isinstance(value, float):
                print(f"  {key}: ${value:,.2f}" if 'amount' in key.lower() or 'revenue' in key.lower() or 'income' in key.lower() else f"  {key}: {value:,.2f}")
            elif isinstance(value, int):
                print(f"  {key}: {value:,}")
            else:
                print(f"  {key}: {value}")
        print()


def main():
    """Run sample queries and display results."""
    print_section("CONTOSO RETAIL DATA ANALYSIS")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    analyzer = RetailDataAnalyzer()

    try:
        # 1. Overall Sales Summary
        print_section("1. OVERALL SALES SUMMARY")
        summary = analyzer.get_sales_summary()
        print_results([summary])

        # 2. Top Products
        print_section("2. TOP 10 PRODUCTS BY REVENUE")
        top_products = analyzer.get_top_products(10)
        print_results(top_products)

        # 3. Sales by Channel
        print_section("3. SALES BY CHANNEL")
        channel_sales = analyzer.get_sales_by_channel()
        print_results(channel_sales)

        # 4. Top Stores
        print_section("4. TOP 10 PERFORMING STORES")
        top_stores = analyzer.get_sales_by_store(10)
        print_results(top_stores)

        # 5. Customer Demographics
        print_section("5. CUSTOMER DEMOGRAPHICS")
        demographics = analyzer.get_customer_demographics()
        print_results(demographics)

        # 6. Online vs Store Sales
        print_section("6. ONLINE VS IN-STORE SALES")
        comparison = analyzer.get_online_vs_store_sales()
        print_results(comparison)

        # 7. Inventory Status
        print_section("7. TOP 20 PRODUCTS BY INVENTORY")
        inventory = analyzer.get_inventory_status()
        print_results(inventory)

        print_section("ANALYSIS COMPLETE")
        print("✅ All queries executed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")

    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
