# AI Orchestrator - FastAPI Backend

A modern, fast FastAPI backend for AI orchestration with built-in CRUD operations and health checks.

## Features

- ⚡ **FastAPI** - High-performance async web framework
- 🤖 **Groq LLM Integration** - AI-powered chat with multiple models
- 🔄 **CORS Support** - Pre-configured CORS middleware
- 📝 **Auto Documentation** - Interactive API docs with Swagger UI
- 🎯 **Type Safety** - Pydantic models for request/response validation
- 🔍 **Health Checks** - Built-in health monitoring endpoints
- 🚀 **Hot Reload** - Development server with auto-reload

## Project Structure

```
ai-orchestrator/
├── main.py              # Main FastAPI application
├── api/
│   ├── __init__.py     # API package initialization
│   └── routes/
│       ├── __init__.py # Routes package initialization
│       └── groq_chat.py # Groq LLM chat route
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Groq API key (get one from [Groq Console](https://console.groq.com))

## Installation

1. **Navigate to the project directory:**
   ```bash
   cd ai-orchestrator
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

6. **Add your Groq API key to `.env`:**
   ```env
   GROQ_API_KEY=gsk_your_actual_api_key_here
   ```
   
   Replace `gsk_your_actual_api_key_here` with your actual Groq API key from the [Groq Console](https://console.groq.com).

## Running the Application

### Development Mode (with auto-reload)

```bash
python3 main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Swagger UI (Interactive):** http://localhost:8000/docs
- **ReDoc (Alternative):** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## API Endpoints

### Health & Status

- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check endpoint

### Items CRUD

- `GET /items` - Get all items
- `GET /items/{item_id}` - Get a specific item
- `POST /items` - Create a new item
- `PUT /items/{item_id}` - Update an existing item
- `DELETE /items/{item_id}` - Delete an item

### Groq LLM Chat

- `POST /api/chat` - Send a message to Groq LLM and get a response

### Example Requests

**Chat with Groq LLM:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is FastAPI?",
    "model": "llama-3.3-70b-versatile",
    "temperature": 0.7,
    "max_tokens": 1024
  }'
```

**Available Groq Models:**
- `llama-3.3-70b-versatile` (default) - Latest Llama model
- `llama-3.1-70b-versatile` - Llama 3.1 70B
- `llama-3.1-8b-instant` - Fast 8B model
- `mixtral-8x7b-32768` - Mixtral model
- `gemma2-9b-it` - Google's Gemma 2

**Create an item:**
```bash
curl -X POST "http://localhost:8000/items" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Item",
    "description": "This is an example item"
  }'
```

**Get all items:**
```bash
curl http://localhost:8000/items
```

## Development

### Adding New Endpoints

1. Create new route files in [`api/routes/`](api/routes/) directory (e.g., `api/routes/new_feature.py`)
2. Define your Pydantic models for request/response validation
3. Import and include routers in [`main.py`](main.py)
4. The API documentation will update automatically

Example structure for a new route file:
```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["YourTag"])

@router.get("/your-endpoint")
async def your_endpoint():
    return {"message": "Hello"}
```

### Project Expansion

Consider adding:
- Database integration (PostgreSQL, MongoDB, etc.)
- Authentication & Authorization (JWT, OAuth2)
- Background tasks with Celery
- Caching with Redis
- Logging and monitoring
- Unit and integration tests

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True
CORS_ORIGINS=*
ENVIRONMENT=development
GROQ_API_KEY=gsk_your_actual_api_key_here
```

**Important:** Never commit your `.env` file with real API keys to version control!

## Dependencies

- **fastapi** - Modern web framework for building APIs
- **uvicorn** - ASGI server for running FastAPI
- **pydantic** - Data validation using Python type hints
- **python-multipart** - For form data and file uploads
- **python-dotenv** - Environment variable management
- **groq** - Official Groq SDK for LLM integration

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, change the port:
```bash
uvicorn main:app --reload --port 8001
```

### Virtual Environment Issues

Make sure your virtual environment is activated:
```bash
which python  # Should point to venv/bin/python
```

### Module Not Found

Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

### Groq API Key Issues

If you get authentication errors:
1. Verify your API key is correct in `.env`
2. Check that the `.env` file is in the project root
3. Ensure the API key starts with `gsk_`
4. Verify your API key is active in the [Groq Console](https://console.groq.com)

## License

MIT License - Feel free to use this project for your needs.

## Next Steps

1. ✅ Set up the project following installation steps
2. 🔧 Customize the API endpoints for your use case
3. 🗄️ Add database integration
4. 🔐 Implement authentication
5. 📊 Add logging and monitoring
6. 🧪 Write tests
7. 🚀 Deploy to production

Happy coding! 🎉