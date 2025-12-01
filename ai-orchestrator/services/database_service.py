"""
Database Service for AI Data Queries

Handles database connections and query execution for the AI bot.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class DatabaseService:
    """Service for executing database queries."""

    def __init__(self):
        """Initialize database connection parameters."""
        self.host = os.getenv('DB_HOST')
        self.database = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASS')
        self.port = os.getenv('DB_PORT', '5432')

    def get_connection(self):
        """Create and return a database connection."""
        return psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
            port=self.port,
            connect_timeout=10
        )

    def execute_query(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            Dict with 'success', 'data', 'row_count', 'error' keys
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params)

                    # Check if query returns data
                    if cursor.description:
                        results = cursor.fetchall()
                        return {
                            'success': True,
                            'data': [dict(row) for row in results],
                            'row_count': len(results),
                            'columns': [desc[0] for desc in cursor.description]
                        }
                    else:
                        return {
                            'success': True,
                            'data': [],
                            'row_count': 0,
                            'message': 'Query executed successfully (no data returned)'
                        }

        except psycopg2.Error as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': e.pgcode if hasattr(e, 'pgcode') else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_table_schema(self, schema_name: str = 'contiso') -> List[Dict[str, Any]]:
        """
        Get schema information for all tables.

        Args:
            schema_name: Database schema name (default: 'contiso')

        Returns:
            List of tables with their columns
        """
        query = """
            SELECT
                t.table_name,
                array_agg(
                    json_build_object(
                        'column_name', c.column_name,
                        'data_type', c.data_type
                    ) ORDER BY c.ordinal_position
                ) as columns
            FROM information_schema.tables t
            JOIN information_schema.columns c
                ON t.table_name = c.table_name
                AND t.table_schema = c.table_schema
            WHERE t.table_schema = %s
            GROUP BY t.table_name
            ORDER BY t.table_name;
        """

        result = self.execute_query(query, (schema_name,))
        if result['success']:
            return result['data']
        return []

    def get_sample_data(self, table_name: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get sample data from a table.

        Args:
            table_name: Name of the table
            limit: Number of rows to return

        Returns:
            Query result dict
        """
        query = f"SELECT * FROM contiso.{table_name} LIMIT %s;"
        return self.execute_query(query, (limit,))
