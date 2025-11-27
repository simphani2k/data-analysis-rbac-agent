# AI Orchestrator - EC2 Deployment Guide

This guide will help you deploy the AI Orchestrator FastAPI backend to an AWS EC2 instance with automated GitHub Actions deployment.

## Prerequisites

- AWS EC2 instance (Ubuntu 20.04 or later)
- SSH access to your EC2 instance
- GitHub repository with the ai-orchestrator code
- Groq API key

## Table of Contents

1. [EC2 Instance Setup](#ec2-instance-setup)
2. [GitHub Secrets Configuration](#github-secrets-configuration)
3. [Initial Deployment](#initial-deployment)
4. [Automated Deployment](#automated-deployment)
5. [Troubleshooting](#troubleshooting)

---

## EC2 Instance Setup

### Step 1: Connect to Your EC2 Instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 2: Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 3: Install Python and Required Tools

```bash
sudo apt install -y python3 python3-pip python3-venv
```

### Step 4: Create Application Directory

```bash
mkdir -p /home/ubuntu/ai-orchestrator
cd /home/ubuntu/ai-orchestrator
```

### Step 5: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 6: Create Environment File

```bash
nano .env
```

Add your configuration:
```env
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=False
CORS_ORIGINS=*
ENVIRONMENT=production
GROQ_API_KEY=your_actual_groq_api_key_here
```

Save and exit (Ctrl+X, then Y, then Enter).

### Step 7: Set Up Systemd Service

Copy the service file to systemd directory:
```bash
sudo cp ai-orchestrator.service /etc/systemd/system/
```

Or create it manually:
```bash
sudo nano /etc/systemd/system/ai-orchestrator.service
```

Paste the following content:
```ini
[Unit]
Description=AI Orchestrator FastAPI Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-orchestrator
Environment="PATH=/home/ubuntu/ai-orchestrator/venv/bin"
EnvironmentFile=/home/ubuntu/ai-orchestrator/.env
ExecStart=/home/ubuntu/ai-orchestrator/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 8: Enable and Start the Service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable ai-orchestrator

# Start the service
sudo systemctl start ai-orchestrator

# Check service status
sudo systemctl status ai-orchestrator
```

### Step 9: Configure Security Group (AWS Console)

1. Go to AWS EC2 Console
2. Select your instance
3. Click on the Security Group
4. Add inbound rule:
   - Type: Custom TCP
   - Port: 8000
   - Source: 0.0.0.0/0 (or restrict to specific IPs)

### Step 10: Test the Deployment

```bash
# From EC2 instance
curl http://localhost:8000/health

# From your local machine
curl http://your-ec2-ip:8000/health
```

---

## GitHub Secrets Configuration

### Required Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

1. **EC2_SSH_KEY**
   - Your EC2 private key content
   - Copy the entire content of your `.pem` file
   ```bash
   cat your-key.pem
   ```

2. **EC2_HOST**
   - Your EC2 instance public IP or hostname
   - Example: `13.233.212.132` or `ec2-13-233-212-132.ap-south-1.compute.amazonaws.com`

### How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with its name and value
5. Click **Add secret**

---

## Initial Deployment

### Option 1: Manual Deployment

1. Clone the repository on EC2:
```bash
cd /home/ubuntu
git clone https://github.com/your-username/your-repo.git ai-orchestrator
cd ai-orchestrator
```

2. Set up virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Create `.env` file with your configuration

4. Start the service:
```bash
sudo systemctl start ai-orchestrator
```

### Option 2: Using GitHub Actions

1. Push your code to the `main` branch
2. The GitHub Actions workflow will automatically deploy
3. Monitor the deployment in the **Actions** tab

---

## Automated Deployment

### How It Works

The GitHub Actions workflow (`.github/workflows/ai_orchestrator_deploy.yml`) automatically:

1. Triggers on push to `main` branch (only when `ai-orchestrator/` files change)
2. Syncs code to EC2 using rsync
3. Installs/updates dependencies
4. Restarts the service

### Manual Trigger

You can also manually trigger deployment:

1. Go to **Actions** tab in GitHub
2. Select **Deploy AI Orchestrator to EC2**
3. Click **Run workflow**
4. Select branch and click **Run workflow**

### Monitoring Deployments

1. Go to **Actions** tab in your GitHub repository
2. Click on the latest workflow run
3. View logs for each step
4. Check for any errors

---

## Service Management Commands

### Check Service Status
```bash
sudo systemctl status ai-orchestrator
```

### View Service Logs
```bash
# View recent logs
sudo journalctl -u ai-orchestrator -n 50

# Follow logs in real-time
sudo journalctl -u ai-orchestrator -f

# View logs from today
sudo journalctl -u ai-orchestrator --since today
```

### Restart Service
```bash
sudo systemctl restart ai-orchestrator
```

### Stop Service
```bash
sudo systemctl stop ai-orchestrator
```

### Start Service
```bash
sudo systemctl start ai-orchestrator
```

### Disable Service (prevent auto-start on boot)
```bash
sudo systemctl disable ai-orchestrator
```

---

## Troubleshooting

### Service Won't Start

1. Check service status:
```bash
sudo systemctl status ai-orchestrator
```

2. View detailed logs:
```bash
sudo journalctl -u ai-orchestrator -n 100 --no-pager
```

3. Common issues:
   - Missing `.env` file
   - Invalid Groq API key
   - Port 8000 already in use
   - Python dependencies not installed

### Port Already in Use

Find and kill the process:
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Permission Issues

Ensure correct ownership:
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/ai-orchestrator
```

### GitHub Actions Deployment Fails

1. Check GitHub Actions logs
2. Verify EC2_SSH_KEY secret is correct
3. Verify EC2_HOST is correct
4. Ensure EC2 security group allows SSH (port 22)
5. Test SSH connection manually:
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### API Not Accessible

1. Check if service is running:
```bash
sudo systemctl status ai-orchestrator
```

2. Check if port is listening:
```bash
sudo netstat -tlnp | grep 8000
```

3. Verify security group allows port 8000

4. Test locally on EC2:
```bash
curl http://localhost:8000/health
```

### Environment Variables Not Loading

1. Verify `.env` file exists:
```bash
cat /home/ubuntu/ai-orchestrator/.env
```

2. Check service file has correct EnvironmentFile path:
```bash
cat /etc/systemd/system/ai-orchestrator.service
```

3. Reload systemd and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ai-orchestrator
```

---

## API Endpoints

Once deployed, your API will be available at:

- **Base URL**: `http://your-ec2-ip:8000`
- **Health Check**: `http://your-ec2-ip:8000/health`
- **API Docs**: `http://your-ec2-ip:8000/docs`
- **Chat Endpoint**: `http://your-ec2-ip:8000/api/chat`

### Example API Call

```bash
curl -X POST "http://your-ec2-ip:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "model": "llama-3.3-70b-versatile"
  }'
```

---

## Security Best Practices

1. **Restrict Security Group**: Only allow necessary IPs to access port 8000
2. **Use HTTPS**: Set up nginx as reverse proxy with SSL certificate
3. **Environment Variables**: Never commit `.env` file to git
4. **API Key Rotation**: Regularly rotate your Groq API key
5. **Update Dependencies**: Keep packages up to date
6. **Monitor Logs**: Regularly check application logs for issues

---

## Updating the Application

### Automatic Updates (via GitHub Actions)

Simply push changes to the `main` branch:
```bash
git add .
git commit -m "Update ai-orchestrator"
git push origin main
```

### Manual Updates

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Navigate to directory
cd /home/ubuntu/ai-orchestrator

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart ai-orchestrator
```

---

## Next Steps

1. ✅ Set up nginx as reverse proxy
2. ✅ Configure SSL certificate (Let's Encrypt)
3. ✅ Set up monitoring (CloudWatch, Prometheus)
4. ✅ Configure log rotation
5. ✅ Set up backup strategy
6. ✅ Implement rate limiting
7. ✅ Add authentication if needed

---

## Support

For issues or questions:
- Check the logs: `sudo journalctl -u ai-orchestrator -f`
- Review GitHub Actions logs
- Verify all configuration files
- Test API endpoints manually

Happy deploying! 🚀