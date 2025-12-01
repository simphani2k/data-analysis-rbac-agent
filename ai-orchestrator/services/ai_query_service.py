"""
AI Query Service

Converts natural language questions to SQL queries using Groq AI.
"""

import os
import json
from typing import Dict, Any, List
from groq import Groq
from dotenv import load_dotenv
from .schema_context import get_schema_context, get_example_queries
from .database_service import DatabaseService

load_dotenv()


class AIQueryService:
    """Service for converting natural language to SQL and executing queries."""

    def __init__(self):
        """Initialize AI and database services."""
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.db_service = DatabaseService()
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.conversation_history = []

    def generate_sql_from_question(self, question: str) -> Dict[str, Any]:
        """
        Convert a natural language question to SQL query.

        Args:
            question: User's natural language question

        Returns:
            Dict with 'sql' query and 'explanation'
        """
        schema_context = get_schema_context()
        examples = get_example_queries()

        # Build example queries string
        examples_str = "\n\n".join([
            f"Example: {name}\n{query}"
            for name, query in examples.items()
        ])

        system_prompt = f"""You are a SQL expert for a Contoso retail database. Your job is to convert natural language questions into accurate SQL queries.

{schema_context}

## Example Queries

{examples_str}

## Rules:
1. ALWAYS use double quotes for column names (case-sensitive)
2. ALWAYS prefix tables with 'contiso.' schema
3. ALWAYS CAST numeric text fields to NUMERIC for math operations
4. Return ONLY valid SQL - no explanations in the query
5. Use appropriate JOINs when querying across tables
6. Limit results to 100 rows unless specifically asked for more
7. For aggregations, use proper GROUP BY clauses

## Response Format:
Return a JSON object with:
{{
  "sql": "your SQL query here",
  "explanation": "brief explanation of what the query does",
  "tables_used": ["table1", "table2"]
}}
"""

        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Convert this question to SQL: {question}"}
                ],
                temperature=0.1,
                max_tokens=1024,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'sql': result.get('sql', ''),
                'explanation': result.get('explanation', ''),
                'tables_used': result.get('tables_used', [])
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a natural language question about the data.

        Args:
            question: User's question

        Returns:
            Dict with query results and formatted answer
        """
        # Generate SQL from question
        sql_result = self.generate_sql_from_question(question)

        if not sql_result['success']:
            return {
                'success': False,
                'error': 'Failed to generate SQL',
                'details': sql_result.get('error')
            }

        sql_query = sql_result['sql']
        explanation = sql_result['explanation']

        # Execute the SQL query
        query_result = self.db_service.execute_query(sql_query)

        if not query_result['success']:
            return {
                'success': False,
                'error': 'SQL execution failed',
                'sql': sql_query,
                'sql_error': query_result.get('error'),
                'explanation': explanation
            }

        # Format the answer
        data = query_result['data']
        row_count = query_result['row_count']

        # Generate natural language response
        answer = self.format_answer(question, data, row_count, explanation)

        return {
            'success': True,
            'answer': answer,
            'data': data,
            'row_count': row_count,
            'sql': sql_query,
            'explanation': explanation
        }

    def format_answer(self, question: str, data: List[Dict], row_count: int, explanation: str) -> str:
        """
        Format query results into a natural language answer.

        Args:
            question: Original question
            data: Query results
            row_count: Number of rows returned
            explanation: SQL explanation

        Returns:
            Formatted answer string
        """
        if row_count == 0:
            return "No data found matching your query."

        # Create a simple formatted response
        answer_parts = [explanation]

        if row_count <= 20:
            # Show all results if small dataset
            answer_parts.append(f"\n\nFound {row_count} result(s):\n")
            for i, row in enumerate(data, 1):
                answer_parts.append(f"\n{i}. {self._format_row(row)}")
        else:
            # Show first 10 for larger datasets
            answer_parts.append(f"\n\nFound {row_count} results. Showing first 10:\n")
            for i, row in enumerate(data[:10], 1):
                answer_parts.append(f"\n{i}. {self._format_row(row)}")
            answer_parts.append(f"\n\n... and {row_count - 10} more results.")

        return "".join(answer_parts)

    def _format_row(self, row: Dict) -> str:
        """Format a single row for display."""
        formatted = []
        for key, value in row.items():
            if value is not None:
                # Format numbers nicely
                if isinstance(value, (int, float)):
                    if isinstance(value, float) and value > 100:
                        formatted.append(f"{key}: {value:,.2f}")
                    elif isinstance(value, int) and value > 1000:
                        formatted.append(f"{key}: {value:,}")
                    else:
                        formatted.append(f"{key}: {value}")
                else:
                    formatted.append(f"{key}: {value}")
        return " | ".join(formatted)
