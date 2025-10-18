#!/usr/bin/env python3
"""
RDS Connection Test Script for Contoso Database

This script tests connectivity to the AWS RDS PostgreSQL instance
and verifies the Contoso database schema.

Usage:
    python scripts/test_rds_connection.py

Prerequisites:
    - AWS credentials configured (via ~/.aws/credentials or environment)
    - .env file with RDS connection parameters
    - psycopg2-binary installed: pip install psycopg2-binary
    - boto3 installed: pip install boto3
"""

import os
import sys
from typing import Dict, List, Optional
import psycopg2
from psycopg2 import OperationalError, DatabaseError
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Load environment variables from .env file
load_dotenv()


class RDSConnectionTester:
    """Test RDS PostgreSQL database connectivity and schema."""

    def __init__(self):
        """Initialize with connection parameters from environment."""
        self.host = os.getenv('RDS_HOST')
        self.port = os.getenv('RDS_PORT', '5432')
        self.database = os.getenv('RDS_DATABASE')
        self.user = os.getenv('RDS_USER')
        self.password = os.getenv('RDS_PASSWORD')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')

        self.connection = None
        self.cursor = None

    def validate_config(self) -> bool:
        """Validate that all required configuration is present."""
        print("=" * 60)
        print("CONFIGURATION VALIDATION")
        print("=" * 60)

        required_vars = ['RDS_HOST', 'RDS_DATABASE', 'RDS_USER', 'RDS_PASSWORD']
        missing_vars = []

        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
                print(f"❌ {var}: NOT SET")
            else:
                # Mask password
                display_value = value if var != 'RDS_PASSWORD' else '*' * 8
                print(f"✅ {var}: {display_value}")

        print(f"✅ RDS_PORT: {self.port}")
        print(f"✅ AWS_REGION: {self.aws_region}")

        if missing_vars:
            print(f"\n❌ Missing required variables: {', '.join(missing_vars)}")
            print("Please create a .env file with the required configuration.")
            print("See .env.example for reference.")
            return False

        print("\n✅ All required configuration present")
        return True

    def test_aws_credentials(self) -> bool:
        """Test AWS credentials and permissions."""
        print("\n" + "=" * 60)
        print("AWS CREDENTIALS TEST")
        print("=" * 60)

        try:
            # Create STS client to verify credentials
            sts = boto3.client('sts', region_name=self.aws_region)
            identity = sts.get_caller_identity()

            print(f"✅ AWS credentials valid")
            print(f"   Account: {identity['Account']}")
            print(f"   User ARN: {identity['Arn']}")
            print(f"   Region: {self.aws_region}")
            return True

        except ClientError as e:
            print(f"❌ AWS credentials error: {e}")
            print("   Please configure AWS credentials:")
            print("   - Run: aws configure")
            print("   - Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
            return False
        except Exception as e:
            print(f"⚠️  AWS credentials check failed: {e}")
            print("   Continuing anyway - may not be required for RDS")
            return True

    def test_connection(self) -> bool:
        """Test basic database connection."""
        print("\n" + "=" * 60)
        print("DATABASE CONNECTION TEST")
        print("=" * 60)

        try:
            print(f"Connecting to: {self.host}:{self.port}/{self.database}")
            print(f"User: {self.user}")

            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                connect_timeout=10
            )

            self.cursor = self.connection.cursor()

            # Test connection with a simple query
            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()[0]

            print(f"\n✅ Connection successful!")
            print(f"   PostgreSQL version: {version[:50]}...")
            return True

        except OperationalError as e:
            print(f"\n❌ Connection failed: {e}")
            print("\nTroubleshooting tips:")
            print("   1. Verify RDS endpoint is correct")
            print("   2. Check security group allows inbound on port 5432")
            print("   3. Verify database credentials")
            print("   4. Ensure VPC/network connectivity")
            return False

        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return False

    def verify_schema(self) -> bool:
        """Verify database schema and tables."""
        print("\n" + "=" * 60)
        print("SCHEMA VERIFICATION")
        print("=" * 60)

        if not self.cursor:
            print("❌ No active database connection")
            return False

        try:
            # Get list of tables
            self.cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)

            tables = [row[0] for row in self.cursor.fetchall()]

            if not tables:
                print("⚠️  No tables found in database")
                print("   Database exists but is empty")
                return True

            print(f"\n✅ Found {len(tables)} tables:")
            for table in tables:
                # Get row count for each table
                self.cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = self.cursor.fetchone()[0]
                print(f"   - {table}: {count:,} rows")

            return True

        except DatabaseError as e:
            print(f"❌ Schema verification error: {e}")
            return False

    def test_query_execution(self) -> bool:
        """Test executing a sample query."""
        print("\n" + "=" * 60)
        print("QUERY EXECUTION TEST")
        print("=" * 60)

        if not self.cursor:
            print("❌ No active database connection")
            return False

        try:
            # Try to query from a Contoso dimension table if it exists
            self.cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name LIKE 'dim%'
                LIMIT 1;
            """)

            result = self.cursor.fetchone()

            if result:
                table_name = result[0]
                print(f"Testing query on table: {table_name}")

                # Get first 5 rows
                self.cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                rows = self.cursor.fetchall()

                # Get column names
                column_names = [desc[0] for desc in self.cursor.description]

                print(f"\n✅ Query executed successfully")
                print(f"   Retrieved {len(rows)} rows")
                print(f"   Columns: {', '.join(column_names[:5])}...")

            else:
                # Just test a basic query
                self.cursor.execute("SELECT 1 as test;")
                result = self.cursor.fetchone()
                print(f"✅ Basic query executed successfully: {result}")

            return True

        except DatabaseError as e:
            print(f"❌ Query execution error: {e}")
            return False

    def get_connection_info(self) -> Dict[str, str]:
        """Return connection parameters for documentation."""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'region': self.aws_region
        }

    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("\n✅ Connection closed")

    def run_all_tests(self) -> bool:
        """Run all connection tests."""
        print("\n" + "=" * 60)
        print("RDS CONNECTION TESTER - CONTOSO DATABASE")
        print("=" * 60)

        all_passed = True

        # Step 1: Validate configuration
        if not self.validate_config():
            return False

        # Step 2: Test AWS credentials (optional)
        self.test_aws_credentials()

        # Step 3: Test database connection
        if not self.test_connection():
            return False

        # Step 4: Verify schema
        if not self.verify_schema():
            all_passed = False

        # Step 5: Test query execution
        if not self.test_query_execution():
            all_passed = False

        # Close connection
        self.close()

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        if all_passed:
            print("✅ All tests passed!")
            print("\nConnection parameters:")
            info = self.get_connection_info()
            for key, value in info.items():
                print(f"   {key}: {value}")
        else:
            print("⚠️  Some tests failed - see details above")

        return all_passed


def main():
    """Main entry point."""
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found!")
        print("Please create a .env file with RDS connection parameters.")
        print("See .env.example for reference.")
        sys.exit(1)

    # Run tests
    tester = RDSConnectionTester()
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
