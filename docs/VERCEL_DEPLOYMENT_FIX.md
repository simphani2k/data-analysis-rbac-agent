# 🚀 Vercel Deployment Fix Guide

## Problem
Your Vercel deployment shows: "Cannot connect to Groq API (AI Orchestrator)"

## Root Cause
The `GROQ_API_URL` environment variable in Vercel is pointing to `http://3.80.111.127:8000` (your EC2 instance), but Vercel's servers cannot reach this URL because:

1. **EC2 Security Groups**: Your EC2 instance likely blocks incoming traffic from Vercel's IP ranges
2. **Private Network**: The EC2 instance may not be publicly accessible
3. **HTTP vs HTTPS**: Vercel prefers HTTPS connections

## Solutions

### ✅ Solution 1: Deploy AI Orchestrator Publicly (Recommended)

Deploy your FastAPI backend to a publicly accessible service:

#### Option A: Deploy to Vercel (Serverless)
```bash
cd ai-orchestrator
# Create vercel.json
cat > vercel.json << 'EOF'
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
EOF

# Deploy
vercel --prod
```

Then update your Vercel environment variable:
- `GROQ_API_URL` = `https://your-ai-orchestrator.vercel.app`

#### Option B: Deploy to Railway/Render/Fly.io
These platforms provide easy Python deployment with public URLs.

**Railway:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
cd ai-orchestrator
railway login
railway init
railway up
```

**Render:**
1. Connect your GitHub repo to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### ✅ Solution 2: Make EC2 Publicly Accessible

If you want to keep using EC2:

#### Step 1: Update EC2 Security Group
```bash
# Get Vercel's IP ranges (they use AWS, so allow all HTTPS traffic)
# Add inbound rule to your EC2 security group:
# Type: Custom TCP
# Port: 8000
# Source: 0.0.0.0/0 (or restrict to Vercel's IP ranges)
```

#### Step 2: Ensure EC2 is Running
```bash
# SSH into your EC2 instance
ssh -i your-key.pem ec2-user@3.80.111.127

# Check if the service is running
curl http://localhost:8000/health

# If not running, start it
cd /path/to/ai-orchestrator
python main.py
```

#### Step 3: Use HTTPS (Recommended)
Set up a reverse proxy with SSL:

```bash
# Install nginx and certbot
sudo yum install nginx certbot python3-certbot-nginx -y

# Configure nginx
sudo nano /etc/nginx/conf.d/ai-orchestrator.conf
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

Then update Vercel environment variable:
- `GROQ_API_URL` = `https://your-domain.com`

### ✅ Solution 3: Use Vercel Environment Variables Correctly

Ensure your Vercel environment variables are set correctly:

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Verify these variables exist and have correct values:

```
GROQ_API_KEY = gsk_xxxxxxxxxxxxx (your actual Groq API key)
GROQ_MODEL = llama-3.3-70b-versatile
GROQ_API_URL = https://your-backend-url.com (must be publicly accessible)
```

4. **Important**: After updating environment variables, you MUST redeploy:
   ```bash
   # Trigger a new deployment
   vercel --prod
   ```

## Testing the Fix

### Test 1: Check Backend Health
```bash
# Replace with your actual URL
curl https://your-backend-url.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### Test 2: Check from Vercel
After deploying, check your Vercel deployment logs:
1. Go to Vercel Dashboard → Your Project → Deployments
2. Click on the latest deployment
3. Check the **Functions** logs
4. Look for `[AI Availability Check]` messages

### Test 3: Frontend Check
Visit your deployed site and check the browser console (F12):
- Look for connection errors
- Check if the health check succeeds

## Quick Fix Checklist

- [ ] Backend is deployed and publicly accessible
- [ ] `GROQ_API_URL` in Vercel points to the public backend URL
- [ ] Backend URL uses HTTPS (not HTTP)
- [ ] Backend `/health` endpoint returns 200 OK
- [ ] Redeployed Vercel after changing environment variables
- [ ] Checked Vercel deployment logs for errors
- [ ] Tested the frontend in production

## Common Mistakes

1. ❌ Using `http://` instead of `https://`
2. ❌ Using `localhost` or `127.0.0.1` in GROQ_API_URL
3. ❌ Not redeploying after changing environment variables
4. ❌ Backend not running or crashed
5. ❌ EC2 security group blocking traffic
6. ❌ Wrong port number in URL

## Need Help?

If you're still having issues:

1. Check Vercel deployment logs
2. Check backend server logs
3. Test the backend URL directly with curl
4. Verify all environment variables are set correctly
5. Ensure you redeployed after making changes

## Recommended Architecture

```
┌─────────────────┐
│  Vercel         │
│  (Frontend)     │
│  Next.js App    │
└────────┬────────┘
         │ HTTPS
         │
         ▼
┌─────────────────┐
│  Railway/Render │
│  (Backend)      │
│  FastAPI        │
│  AI Orchestrator│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Groq API       │
│  (LLM Service)  │
└─────────────────┘
```

This architecture ensures:
- ✅ Both frontend and backend are publicly accessible
- ✅ HTTPS everywhere
- ✅ Easy deployment and scaling
- ✅ No security group configuration needed