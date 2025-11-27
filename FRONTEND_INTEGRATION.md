# Frontend Integration with AI Orchestrator (Groq API)

This guide explains how the frontend has been integrated with the AI Orchestrator backend running on EC2.

## 🔄 Changes Made

### 1. **Backend API Calls** (`frontend/src/app/actions.tsx`)

Replaced OpenAI SDK calls with direct HTTP requests to the Groq API endpoint:

#### Before (OpenAI):
```typescript
import { openai, createOpenAI } from '@ai-sdk/openai';

const result = await streamText({
  model: openai('gpt-4-turbo'),
  messages,
});
```

#### After (Groq API):
```typescript
const response = await fetch(`${groqApiUrl}/api/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: messages[messages.length - 1].content,
    model: 'llama-3.3-70b-versatile',
    temperature: 0.7,
    max_tokens: 1024,
  }),
});
```

### 2. **Environment Variables** (`frontend/.env.example`)

#### Before:
```env
OPENAI_API_KEY=
OPENAI_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini
```

#### After:
```env
GROQ_API_URL=http://3.80.111.127:8000
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. **Error Messages** (`frontend/src/components/cards/envcard.tsx`)

Updated error messages to reflect Groq API usage instead of OpenAI.

## 🚀 Setup Instructions

### Step 1: Update Environment Variables

Create or update your `.env.local` file in the `frontend/` directory:

```bash
cd frontend
cp .env.example .env.local
```

Edit `.env.local`:
```env
# 🤖 Groq API Configuration (AI Orchestrator)
GROQ_API_URL=http://3.80.111.127:8000
GROQ_MODEL=llama-3.3-70b-versatile

# 🗄️ Database Configuration (if needed)
DB_HOST=your-db-host
DB_NAME=postgres
DB_USER=postgres
DB_PASS=your_password
DB_PORT=5432
```

### Step 2: Install Dependencies

```bash
cd frontend
npm install
# or
pnpm install
```

### Step 3: Run the Frontend

```bash
npm run dev
# or
pnpm dev
```

The frontend will be available at `http://localhost:3000`

## 🔌 API Integration Details

### Available Functions

#### 1. `continueTextConversation(messages)`
Streams text responses from Groq API for chat conversations.

**Usage:**
```typescript
const stream = await continueTextConversation([
  { role: 'user', content: 'Hello!' }
]);
```

#### 2. `continueConversation(history)`
Handles conversations with UI components (like weather widgets).

**Usage:**
```typescript
const result = await continueConversation([
  { role: 'user', content: 'What is the weather in New York?' }
]);
```

#### 3. `checkAIAvailability()`
Checks if the Groq API is accessible.

**Usage:**
```typescript
const isAvailable = await checkAIAvailability();
```

### API Endpoint

**Base URL:** `http://3.80.111.127:8000`

**Chat Endpoint:** `POST /api/chat`

**Request Body:**
```json
{
  "message": "Your message here",
  "model": "llama-3.3-70b-versatile",
  "temperature": 0.7,
  "max_tokens": 1024
}
```

**Response:**
```json
{
  "response": "AI response here",
  "model": "llama-3.3-70b-versatile",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

## 🎯 Available Groq Models

You can change the model by updating the `GROQ_MODEL` environment variable:

- `llama-3.3-70b-versatile` (default) - Latest Llama model, best for general tasks
- `llama-3.1-70b-versatile` - Llama 3.1 70B, great for complex reasoning
- `llama-3.1-8b-instant` - Fast 8B model, good for quick responses
- `mixtral-8x7b-32768` - Mixtral model with large context window
- `gemma2-9b-it` - Google's Gemma 2, efficient and capable

## 🧪 Testing the Integration

### 1. Test API Availability

```bash
curl http://3.80.111.127:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### 2. Test Chat Endpoint

```bash
curl -X POST "http://3.80.111.127:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "model": "llama-3.3-70b-versatile"
  }'
```

### 3. Test Frontend

1. Start the frontend: `npm run dev`
2. Open `http://localhost:3000`
3. Try the chat interface
4. Check browser console for any errors

## 🔧 Troubleshooting

### Issue: "Cannot connect to Groq API"

**Solutions:**
1. Verify the EC2 instance is running:
   ```bash
   ssh -i your-key.pem ubuntu@3.80.111.127
   sudo systemctl status ai-orchestrator
   ```

2. Check if the API is accessible:
   ```bash
   curl http://3.80.111.127:8000/health
   ```

3. Verify environment variables in `.env.local`:
   ```bash
   cat frontend/.env.local
   ```

4. Check EC2 security group allows port 8000

### Issue: CORS Errors

The backend is configured to allow all origins (`allow_origins=["*"]`). If you still see CORS errors:

1. Check the backend logs:
   ```bash
   ssh ubuntu@3.80.111.127
   sudo journalctl -u ai-orchestrator -f
   ```

2. Verify CORS middleware in `ai-orchestrator/main.py`

### Issue: Slow Responses

1. Try a faster model:
   ```env
   GROQ_MODEL=llama-3.1-8b-instant
   ```

2. Reduce max_tokens:
   ```typescript
   max_tokens: 512  // instead of 1024
   ```

### Issue: TypeScript Errors

The TypeScript errors you see are type-checking issues and won't affect runtime. To fix them:

1. Ensure `@types/node` is installed:
   ```bash
   npm install --save-dev @types/node
   ```

2. Update `tsconfig.json` to include node types

## 📊 Monitoring

### Check Backend Logs

```bash
ssh ubuntu@3.80.111.127
sudo journalctl -u ai-orchestrator -f
```

### Check Frontend Console

Open browser DevTools (F12) and check:
- Console for errors
- Network tab for API calls
- Response times

## 🔐 Security Considerations

### For Production:

1. **Use HTTPS**: Set up nginx with SSL certificate
2. **Restrict CORS**: Update `allow_origins` in backend to specific domains
3. **Add Authentication**: Implement API key or JWT authentication
4. **Rate Limiting**: Add rate limiting to prevent abuse
5. **Environment Variables**: Never commit `.env.local` to git

### Example nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🚀 Deployment

### Frontend Deployment (Vercel)

1. Push your code to GitHub
2. Connect repository to Vercel
3. Add environment variables in Vercel dashboard:
   - `GROQ_API_URL=http://3.80.111.127:8000`
   - `GROQ_MODEL=llama-3.3-70b-versatile`
4. Deploy

### Backend Already Deployed

Your AI Orchestrator is already running on EC2 at `http://3.80.111.127:8000`

## 📝 Next Steps

1. ✅ Test the integration thoroughly
2. ✅ Set up HTTPS for production
3. ✅ Add error handling and retry logic
4. ✅ Implement caching for common queries
5. ✅ Add analytics and monitoring
6. ✅ Optimize model selection based on query type
7. ✅ Add user feedback mechanism

## 🆘 Support

If you encounter issues:

1. Check the logs (backend and frontend console)
2. Verify all environment variables are set correctly
3. Test the API endpoint directly with curl
4. Check EC2 instance status and security groups
5. Review the GitHub Actions deployment logs

## 📚 Additional Resources

- [Groq API Documentation](https://console.groq.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [AI Orchestrator Deployment Guide](ai-orchestrator/DEPLOYMENT.md)

---

Happy coding! 🎉