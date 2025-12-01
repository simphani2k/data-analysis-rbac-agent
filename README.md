# 🤖 Data Analysis RBAC Agent

A full-stack application for AI-powered data analysis with role-based access control.

## 🏗️ Architecture

```
┌─────────────────┐
│  Frontend       │
│  (Next.js)      │
│  Vercel         │
└────────┬────────┘
         │ HTTPS
         │
         ▼
┌─────────────────┐
│  AI Orchestrator│
│  (FastAPI)      │
│  Backend        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL     │
│  (AWS RDS)      │
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm/pnpm
- Python 3.9+
- PostgreSQL database (AWS RDS or local)
- Groq API key

### Frontend Setup

```bash
cd frontend
npm install

# Copy and configure environment variables
cp .env.example .env.local
# Edit .env.local with your values

# Run development server
npm run dev
```

### Backend Setup

```bash
cd ai-orchestrator
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your values

# Run development server
python main.py
```

## 📦 Deployment

### Deploy Frontend to Vercel

```bash
cd frontend
vercel --prod
```

**Environment Variables in Vercel:**
- `GROQ_API_KEY` - Your Groq API key
- `GROQ_MODEL` - Model name (e.g., llama-3.3-70b-versatile)
- `GROQ_API_URL` - **Must be a publicly accessible HTTPS URL**

### Deploy Backend

**Option 1: Vercel (Serverless)**
```bash
cd ai-orchestrator
vercel --prod
```

**Option 2: Railway**
```bash
cd ai-orchestrator
railway login
railway init
railway up
```

**Option 3: Render**
1. Connect GitHub repo
2. Create new Web Service
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## ⚠️ Common Issues

### "Cannot connect to Groq API (AI Orchestrator)"

This error occurs when the frontend cannot reach the backend. See [`docs/VERCEL_DEPLOYMENT_FIX.md`](docs/VERCEL_DEPLOYMENT_FIX.md) for detailed troubleshooting.

**Quick fixes:**
1. Ensure `GROQ_API_URL` is a publicly accessible HTTPS URL
2. Don't use `localhost`, `127.0.0.1`, or private IPs in production
3. Redeploy Vercel after changing environment variables
4. Check that your backend is running and accessible

### Database Connection Issues

See [`docs/RDS_CONNECTION_GUIDE.md`](docs/RDS_CONNECTION_GUIDE.md) for RDS setup and troubleshooting.

## 📚 Documentation

- [Initial Setup Guide](docs/INITIAL_SETUP.md)
- [Vercel Deployment Fix](docs/VERCEL_DEPLOYMENT_FIX.md)
- [RDS Connection Guide](docs/RDS_CONNECTION_GUIDE.md)
- [SSH Tunnel Guide](docs/SSH_TUNNEL_GUIDE.md)
- [GitHub Actions Setup](docs/GITHUB_ACTIONS_SETUP.md)

## 🛠️ Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components

**Backend:**
- FastAPI
- Python 3.9+
- Groq API (LLM)
- PostgreSQL

**Deployment:**
- Vercel (Frontend & Backend)
- AWS RDS (Database)

## 📝 Environment Variables

### Frontend (.env.local)
```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_URL=https://your-backend-url.com
```

### Backend (.env)
```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
DB_HOST=your-db-host
DB_NAME=postgres
DB_USER=postgres
DB_PASS=your_password
DB_PORT=5432
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details