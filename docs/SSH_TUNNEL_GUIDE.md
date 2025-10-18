# SSH Tunnel Guide for Secure RDS Access

This guide explains how to securely connect to your private AWS RDS instance using SSH tunneling through a bastion host (EC2 instance).

## Why Use SSH Tunneling?

SSH tunneling provides secure access to private RDS instances without exposing them to the public internet:

- ✅ **Security**: RDS remains private, no public accessibility needed
- ✅ **Encryption**: All traffic encrypted through SSH tunnel
- ✅ **Access Control**: Leverage EC2 security groups and SSH keys
- ✅ **Flexibility**: Connect from local machine as if RDS was local

## Architecture

```
Your Machine → SSH Tunnel → EC2 (Bastion) → RDS (Private)
localhost:5433              SSH           Port 5432
```

## Prerequisites

### 1. EC2 Bastion Host

You need an EC2 instance in the **same VPC** as your RDS instance:

- Running Amazon Linux 2 or Ubuntu
- Has public IP or elastic IP
- SSH access enabled (port 22)
- Can reach RDS instance (same VPC/subnet)

### 2. SSH Key Pair

- Download the `.pem` key file for your EC2 instance
- Store securely (e.g., `~/.ssh/contoso-bastion.pem`)
- Set correct permissions: `chmod 400 ~/.ssh/contoso-bastion.pem`

### 3. Security Groups

**EC2 Security Group** (Inbound):
- Allow SSH (port 22) from your IP address

**RDS Security Group** (Inbound):
- Allow PostgreSQL (port 5432) from EC2 security group

## Setup Instructions

### Step 1: Configure Environment Variables

Add SSH configuration to your `.env` file:

```bash
# AWS RDS Configuration
RDS_HOST=contico.cpcggusmcw6o.us-east-2.rds.amazonaws.com
RDS_PORT=5432
RDS_DATABASE=contoso_db
RDS_USER=postgres
RDS_PASSWORD=your-password

# SSH Tunnel Configuration
USE_SSH_TUNNEL=true
SSH_HOST=ec2-3-xxx-xxx-xxx.us-east-2.compute.amazonaws.com  # Your EC2 public IP
SSH_USER=ec2-user  # or 'ubuntu' for Ubuntu instances
SSH_KEY_PATH=~/.ssh/contoso-bastion.pem
SSH_LOCAL_PORT=5433  # Local port to use
```

### Step 2: Set SSH Key Permissions

```bash
chmod 400 ~/.ssh/contoso-bastion.pem
```

### Step 3: Verify EC2 Connectivity

Test SSH access to your bastion host:

```bash
ssh -i ~/.ssh/contoso-bastion.pem ec2-user@your-ec2-public-ip
```

If this works, you can proceed to tunnel setup.

## Using the SSH Tunnel Manager

### Start the Tunnel

```bash
python scripts/ssh_tunnel_manager.py start
```

**Expected output:**
```
============================================================
SSH TUNNEL CONFIGURATION
============================================================
✅ RDS Host: contico.cpcggusmcw6o.us-east-2.rds.amazonaws.com
✅ RDS Database: contoso_db
✅ SSH Host: ec2-3-xxx-xxx-xxx.us-east-2.compute.amazonaws.com
✅ SSH User: ec2-user
✅ SSH Key: /Users/username/.ssh/contoso-bastion.pem
✅ Local Port: 5433
✅ Remote Port: 5432

✅ Configuration valid

============================================================
STARTING SSH TUNNEL
============================================================
Creating tunnel: localhost:5433 → ec2-host → RDS:5432
✅ SSH tunnel started successfully (PID: 12345)

Connection details:
   Local:  localhost:5433
   Remote: contico.cpcggusmcw6o.us-east-2.rds.amazonaws.com:5432
   Via:    ec2-user@ec2-3-xxx-xxx-xxx.us-east-2.compute.amazonaws.com

💡 Use RDS_HOST=localhost and RDS_PORT=5433 to connect
```

### Check Tunnel Status

```bash
python scripts/ssh_tunnel_manager.py status
```

### Test Connection Through Tunnel

```bash
python scripts/ssh_tunnel_manager.py test
```

**Expected output:**
```
============================================================
TESTING CONNECTION THROUGH TUNNEL
============================================================
Connecting to: localhost:5433/contoso_db

✅ Connection successful!
   PostgreSQL: PostgreSQL 15.4 on x86_64-pc-linux-gnu...
   Tables: 20

✅ SSH tunnel is working correctly!
```

### Stop the Tunnel

```bash
python scripts/ssh_tunnel_manager.py stop
```

## Running RDS Tests Through Tunnel

### Option 1: Temporary Environment Override

```bash
# Start tunnel
python scripts/ssh_tunnel_manager.py start

# Run tests with localhost
RDS_HOST=localhost RDS_PORT=5433 python scripts/test_rds_connection.py

# Stop tunnel when done
python scripts/ssh_tunnel_manager.py stop
```

### Option 2: Update .env File

Temporarily modify `.env`:

```bash
# Original RDS host
RDS_HOST=contico.cpcggusmcw6o.us-east-2.rds.amazonaws.com
RDS_PORT=5432

# Change to:
RDS_HOST=localhost
RDS_PORT=5433
```

Then run:

```bash
python scripts/test_rds_connection.py
```

**Remember to change back after testing!**

## Troubleshooting

### SSH Connection Refused

**Error**: `ssh: connect to host X.X.X.X port 22: Connection refused`

**Solutions**:
1. Verify EC2 instance is running (AWS Console)
2. Check EC2 security group allows SSH (port 22) from your IP
3. Verify you're using correct public IP (may change after restart)
4. Check Network ACLs in VPC settings

### Permission Denied (publickey)

**Error**: `Permission denied (publickey)`

**Solutions**:
1. Verify SSH key path is correct in `.env`
2. Check key permissions: `chmod 400 ~/.ssh/your-key.pem`
3. Verify key matches EC2 instance key pair
4. Check SSH_USER is correct (`ec2-user` for Amazon Linux, `ubuntu` for Ubuntu)

### Tunnel Starts but Connection Fails

**Error**: Connection timeout when testing through tunnel

**Solutions**:
1. Verify EC2 can reach RDS:
   ```bash
   ssh -i key.pem ec2-user@ec2-ip
   psql -h rds-endpoint -U postgres -d contoso_db
   ```
2. Check RDS security group allows inbound from EC2 security group
3. Verify EC2 and RDS are in same VPC or have VPC peering
4. Check VPC route tables and network ACLs

### Port Already in Use

**Error**: `bind: Address already in use`

**Solutions**:
1. Check if tunnel is already running: `python scripts/ssh_tunnel_manager.py status`
2. Stop existing tunnel: `python scripts/ssh_tunnel_manager.py stop`
3. Find process using port: `lsof -ti:5433 | xargs kill -9`
4. Change `SSH_LOCAL_PORT` in `.env` to different port

### Tunnel Disconnects Frequently

**Solutions**:
1. The script uses `ServerAliveInterval=60` to keep connection alive
2. Check EC2 instance hasn't restarted (new IP if not using Elastic IP)
3. Verify network stability
4. Consider using an Elastic IP for EC2 to maintain consistent address

## Advanced Usage

### Manual SSH Tunnel (Without Script)

```bash
ssh -N -L 5433:rds-endpoint:5432 -i ~/.ssh/key.pem ec2-user@ec2-ip
```

- `-N`: Don't execute remote commands
- `-L`: Local port forwarding
- `-i`: Identity file (SSH key)

Keep this running in a terminal, use another terminal for database connections.

### Using psql Through Tunnel

```bash
# Start tunnel first
python scripts/ssh_tunnel_manager.py start

# Connect with psql
psql -h localhost -p 5433 -U postgres -d contoso_db

# Stop tunnel when done
python scripts/ssh_tunnel_manager.py stop
```

### Background Tunnel (Long-Running)

The tunnel runs in the background automatically. To ensure it stays running:

```bash
# Check periodically
watch -n 30 'python scripts/ssh_tunnel_manager.py status'

# Or create a cron job to restart if needed
*/5 * * * * cd /path/to/project && python scripts/ssh_tunnel_manager.py start
```

## Security Best Practices

1. **Never commit .env file** - Contains sensitive credentials
2. **Protect SSH keys** - Use 400 permissions, store securely
3. **Restrict security groups** - Only allow your IP for SSH
4. **Use Elastic IP** - For consistent bastion host address
5. **Rotate credentials** - Change RDS password regularly
6. **Monitor access** - Review CloudTrail and VPC flow logs
7. **Use session manager** - Consider AWS Systems Manager Session Manager as alternative
8. **Implement MFA** - For SSH access to critical bastion hosts

## Alternative Approaches

### AWS Systems Manager Session Manager

More secure alternative that doesn't require SSH keys or public IPs:

```bash
# Start session
aws ssm start-session --target i-instance-id

# Port forwarding
aws ssm start-session \
  --target i-instance-id \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["5432"],"localPortNumber":["5433"]}'
```

Requires IAM permissions and SSM agent on EC2.

### AWS Client VPN

For teams needing frequent RDS access:

1. Setup AWS Client VPN
2. Connect to VPN
3. Access RDS directly via private IP
4. No bastion host needed

### RDS Proxy

For application-level connections:

1. Create RDS Proxy in same VPC
2. Configure IAM authentication
3. Applications connect to proxy
4. Proxy manages connection pooling

## Comparison: Connection Methods

| Method | Security | Setup Complexity | Cost | Best For |
|--------|----------|------------------|------|----------|
| **SSH Tunnel** | ⭐⭐⭐⭐ | Medium | $ | Development/Testing |
| **Public RDS** | ⭐ | Low | $ | Quick testing only |
| **Session Manager** | ⭐⭐⭐⭐⭐ | High | $$ | Enterprise |
| **Client VPN** | ⭐⭐⭐⭐ | High | $$$ | Teams |
| **RDS Proxy** | ⭐⭐⭐⭐⭐ | Medium | $$$ | Production apps |

## Quick Reference Commands

```bash
# Setup (once)
chmod 400 ~/.ssh/your-key.pem
cp .env.example .env
# Edit .env with your details

# Daily workflow
python scripts/ssh_tunnel_manager.py start    # Start tunnel
python scripts/ssh_tunnel_manager.py test     # Verify working
python scripts/test_rds_connection.py         # Run RDS tests
python scripts/ssh_tunnel_manager.py stop     # Stop when done

# Troubleshooting
python scripts/ssh_tunnel_manager.py status   # Check if running
ssh -i ~/.ssh/key.pem ec2-user@ec2-ip        # Test EC2 access
lsof -ti:5433 | xargs kill -9                # Kill port 5433
```

## Next Steps

After successful tunnel setup:

1. ✅ **Test Connection** - Verify RDS connectivity through tunnel
2. 📊 **Load Data** - Import Contoso dataset to RDS
3. 🔐 **Configure RBAC** - Set up role-based access control
4. 🤖 **Integrate Agent** - Connect data analysis agent to RDS
5. 🌐 **Deploy Application** - Production deployment strategies

## Resources

- [AWS RDS Security Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.Security.html)
- [SSH Tunneling Documentation](https://www.ssh.com/academy/ssh/tunneling)
- [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)
