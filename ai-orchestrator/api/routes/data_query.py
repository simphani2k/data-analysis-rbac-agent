"""
Data Query API Routes

API endpoints for natural language data queries.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from services.ai_query_service import AIQueryService
import logging

router = APIRouter(prefix="/api/data", tags=["data-query"])


class DataQueryRequest(BaseModel):
    """Request model for data queries."""
    question: str
    context: Optional[List[Dict[str, str]]] = None  # For conversation history


class DataQueryResponse(BaseModel):
    """Response model for data queries."""
    success: bool
    answer: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    row_count: Optional[int] = None
    sql: Optional[str] = None
    explanation: Optional[str] = None
    error: Optional[str] = None


@router.post("/query", response_model=DataQueryResponse)
async def query_data(request: DataQueryRequest):
    try:
        ai_service = AIQueryService()
        result = ai_service.answer_question(request.question)
        logging.info(f"SQL: {result.get('sql')}, Error: {result.get('error')}")

        if not result['success']:
            return DataQueryResponse(
                success=False,
                error=result.get('error', 'Unknown error'),
                sql=result.get('sql'),
                explanation=result.get('explanation')
            )

        return DataQueryResponse(
            success=True,
            answer=result['answer'],
            data=result['data'],
            row_count=result['row_count'],
            sql=result['sql'],
            explanation=result['explanation']
        )

    except Exception as e:
        logging.exception("Unhandled exception")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "data-query"}
