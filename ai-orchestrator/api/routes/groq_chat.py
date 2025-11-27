from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Create router
router = APIRouter(prefix="/api", tags=["AI"])

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "llama-3.3-70b-versatile"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024

class ChatResponse(BaseModel):
    response: str
    model: str
    usage: dict

@router.post("/chat", response_model=ChatResponse)
async def chat_with_groq(request: ChatRequest):
    """
    Send a message to Groq LLM and get a response
    
    Available models:
    - llama-3.3-70b-versatile (default)
    - llama-3.1-70b-versatile
    - llama-3.1-8b-instant
    - mixtral-8x7b-32768
    - gemma2-9b-it
    """
    try:
        # Make API call to Groq
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": request.message,
                }
            ],
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        # Extract response
        response_text = chat_completion.choices[0].message.content
        
        return ChatResponse(
            response=response_text,
            model=request.model,
            usage={
                "prompt_tokens": chat_completion.usage.prompt_tokens,
                "completion_tokens": chat_completion.usage.completion_tokens,
                "total_tokens": chat_completion.usage.total_tokens,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")