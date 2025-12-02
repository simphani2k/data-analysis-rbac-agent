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
        Format query results into a markdown table.

        Args:
            question: Original question
            data: Query results
            row_count: Number of rows returned
            explanation: SQL explanation

        Returns:
            Formatted answer string with markdown table
        """
        if row_count == 0:
            return "No data found matching your query."

        # Start with explanation
        answer_parts = [explanation, "\n\n"]

        # Determine how many rows to show
        display_limit = min(row_count, 20)
        display_data = data[:display_limit]

        # Get column names from first row
        if display_data:
            columns = list(display_data[0].keys())

            # Create markdown table header
            answer_parts.append("| " + " | ".join(columns) + " |\n")
            answer_parts.append("|" + "|".join(["---" for _ in columns]) + "|\n")

            # Add rows
            for row in display_data:
                formatted_values = []
                for col in columns:
                    value = row.get(col)
                    formatted_values.append(self._format_value(value))
                answer_parts.append("| " + " | ".join(formatted_values) + " |\n")

            # Add footer if there are more results
            if row_count > display_limit:
                answer_parts.append(f"\n*Showing {display_limit} of {row_count:,} total results*")
            else:
                answer_parts.append(f"\n*Total: {row_count:,} results*")

        return "".join(answer_parts)

    def _format_value(self, value) -> str:
        """Format a single value for display in table."""
        if value is None:
            return "-"

        # Format numbers with proper separators
        if isinstance(value, float):
            if value > 1000 or value < -1000:
                return f"{value:,.2f}"
            else:
                return f"{value:.2f}"
        elif isinstance(value, int):
            if value > 1000 or value < -1000:
                return f"{value:,}"
            else:
                return str(value)
        else:
            # Truncate long strings
            str_value = str(value)
            if len(str_value) > 50:
                return str_value[:47] + "..."
            return str_value
