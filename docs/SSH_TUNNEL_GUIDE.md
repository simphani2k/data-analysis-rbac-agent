# SSH Access & EC2 Logs Guide

## Access EC2 Instance

### 1. Set Key Permissions
```bash
chmod 400 ai-orchestrator-key-pair.pem
```

### 2. Connect to EC2
```bash
ssh -i ai-orchestrator-key-pair.pem ubuntu@3.80.111.127
```

## View EC2 Logs

### Live Logs (Real-time)
```bash
sudo journalctl -u ai-orchestrator -f
```

### Recent Logs
```bash
sudo journalctl -u ai-orchestrator -n 100
```

### Logs Since Boot
```bash
sudo journalctl -u ai-orchestrator -b
```

### Time-based Logs
```bash
# Last hour
sudo journalctl -u ai-orchestrator --since "1 hour ago"

# Last 30 minutes
sudo journalctl -u ai-orchestrator --since "30 minutes ago"
```

### Service Status
```bash
sudo systemctl status ai-orchestrator
```

## Service Management

```bash
# Restart service
sudo systemctl restart ai-orchestrator

# Stop service
sudo systemctl stop ai-orchestrator

# Start service
sudo systemctl start ai-orchestrator
```

## Quick Reference

```bash
# Connect to EC2
ssh -i ai-orchestrator-key-pair.pem ubuntu@3.80.111.127

# View live logs
sudo journalctl -u ai-orchestrator -f

# Check service status
sudo systemctl status ai-orchestrator
```

## Common Issues

### Permission Denied
```bash
chmod 400 ai-orchestrator-key-pair.pem
```

### Connection Timeout
- Verify EC2 instance is running
- Check security group allows SSH (port 22) from your IP

### Host Key Verification Failed
```bash
ssh-keygen -R 3.80.111.127
