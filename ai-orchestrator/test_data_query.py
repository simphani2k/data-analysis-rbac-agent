#!/usr/bin/env python3
"""
Test script for AI Data Query Service

Tests the natural language to SQL conversion and query execution.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.ai_query_service import AIQueryService
from services.database_service import DatabaseService


def print_section(title):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_database_connection():
    """Test 1: Verify database connection."""
    print_section("Test 1: Database Connection")

    try:
        db_service = DatabaseService()
        result = db_service.execute_query("SELECT 1 as test;")

        if result['success']:
            print("✅ Database connection successful")
            return True
        else:
            print(f"❌ Database connection failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_simple_query():
    """Test 2: Execute a simple query."""
    print_section("Test 2: Simple Query Execution")

    try:
        db_service = DatabaseService()
        query = 'SELECT * FROM contiso.dimproductcategory LIMIT 5;'
        result = db_service.execute_query(query)

        if result['success']:
            print(f"✅ Query executed successfully")
            print(f"   Rows returned: {result['row_count']}")
            print(f"\nSample data:")
            for row in result['data'][:3]:
                print(f"   {row}")
            return True
        else:
            print(f"❌ Query failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_ai_sql_generation():
    """Test 3: AI SQL generation."""
    print_section("Test 3: AI SQL Generation")

    test_questions = [
        "What product categories are available?",
        "Show me the top 5 products",
        "How many stores are there by country?",
    ]

    try:
        ai_service = AIQueryService()

        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Question: {question}")
            result = ai_service.generate_sql_from_question(question)

            if result['success']:
                print(f"   ✅ SQL Generated")
                print(f"   Explanation: {result['explanation']}")
                print(f"   SQL: {result['sql'][:100]}...")
            else:
                print(f"   ❌ Failed: {result.get('error')}")
                return False

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_query_execution():
    """Test 4: Full AI query execution."""
    print_section("Test 4: AI Query Execution (End-to-End)")

    test_questions = [
        "What product categories are available?",
        "Show me 5 stores",
    ]

    try:
        ai_service = AIQueryService()

        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Question: {question}")
            print("-" * 70)

            result = ai_service.answer_question(question)

            if result['success']:
                print(f"\n{result['answer']}\n")
                print(f"SQL: {result['sql']}")
                print(f"Rows: {result['row_count']}")
            else:
                print(f"❌ Failed: {result.get('error')}")
                if 'sql_error' in result:
                    print(f"   SQL Error: {result['sql_error']}")
                if 'sql' in result:
                    print(f"   SQL: {result['sql']}")
                return False

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print_section("AI DATA QUERY SERVICE - TEST SUITE")

    tests = [
        ("Database Connection", test_database_connection),
        ("Simple Query", test_simple_query),
        ("AI SQL Generation", test_ai_sql_generation),
        ("AI Query Execution", test_ai_query_execution),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")

    print(f"\n  Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n  🎉 All tests passed!")
        return 0
    else:
        print("\n  ⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
