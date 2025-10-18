# RDS Security Group Configuration Required

## Current Status

✅ **SSH Tunnel Setup**: Configured correctly
✅ **EC2 Instance**: Accessible and working
✅ **EC2 → Your Machine**: SSH connection works
❌ **EC2 → RDS**: **BLOCKED** - This is the issue!

## The Problem

Your EC2 instance (`i-0cce4408ded63038a`) **cannot reach** your RDS instance (`contoso`) because the **RDS security group is blocking inbound connections** from EC2.

## The Solution

You need to add an **inbound rule** to the RDS security group to allow PostgreSQL traffic from the EC2 security group.

---

## Step-by-Step Fix (AWS Console)

### Step 1: Find the EC2 Security Group ID

1. Go to: https://console.aws.amazon.com/ec2/v2/home?region=us-east-2#Instances
2. Click on instance: `i-0cce4408ded63038a` (ec2-dev01)
3. Click the **Security** tab
4. **Copy the Security Group ID** (format: `sg-xxxxxxxxxxxxxxxxx`)
   - Example: `sg-0a1b2c3d4e5f6g7h8`

### Step 2: Update RDS Security Group

1. Go to: https://console.aws.amazon.com/rds/home?region=us-east-2#databases:
2. Click on database: **contoso**
3. Go to **Connectivity & security** tab
4. Under **Security**, click on the **VPC security groups** link
   - This opens the RDS security group

5. Click **Edit inbound rules** button

6. Click **Add rule** and configure:
   ```
   Type: PostgreSQL
   Protocol: TCP
   Port range: 5432
   Source: Custom
   Source value: <PASTE EC2 SECURITY GROUP ID HERE>
   Description: PostgreSQL from EC2 bastion
   ```

7. Click **Save rules**

---

## Visual Guide

### What You're Adding:

```
┌─────────────────────────────────────────────────────┐
│ RDS Security Group - Inbound Rules                 │
├─────────────────────────────────────────────────────┤
│ Type         │ Protocol │ Port │ Source            │
│──────────────┼──────────┼──────┼───────────────────│
│ PostgreSQL   │ TCP      │ 5432 │ sg-xxxx (EC2 SG) │
└─────────────────────────────────────────────────────┘
```

### The Flow After Fix:

```
Your Mac
   │
   │ SSH (port 22)
   ▼
EC2 Instance (18.217.115.219)
   │
   │ PostgreSQL (port 5432) ✅ ALLOWED
   ▼
RDS Database (contoso.cpcggusmcw6o.us-east-2.rds.amazonaws.com)
```

---

## Quick Copy-Paste Info

**Region**: us-east-2
**EC2 Instance**: i-0cce4408ded63038a
**RDS Endpoint**: contoso.cpcggusmcw6o.us-east-2.rds.amazonaws.com
**RDS Port**: 5432

---

## After You Apply the Fix

Run these commands to test:

```bash
# 1. Start the SSH tunnel
python scripts/ssh_tunnel_manager.py start

# 2. Test the connection
python scripts/ssh_tunnel_manager.py test

# 3. Run full RDS test (connect through tunnel)
python scripts/test_rds_connection.py
```

---

## Why This Is Secure

- ✅ RDS remains **private** (not publicly accessible)
- ✅ Only EC2 instance can reach RDS
- ✅ You connect through **encrypted SSH tunnel**
- ✅ No direct internet exposure of database

---

## Common Mistakes to Avoid

❌ **Don't** add your IP directly to RDS security group (defeats the purpose)
❌ **Don't** make RDS publicly accessible
✅ **Do** add EC2 security group to RDS inbound rules
✅ **Do** keep RDS in private subnet

---

## Verification

After adding the rule, you should see:

**From your Mac:**
```bash
$ python scripts/ssh_tunnel_manager.py test

✅ Connection successful!
   PostgreSQL: PostgreSQL 15.x
   Tables: 0
✅ SSH tunnel is working correctly!
```

---

## Still Not Working?

If you still get errors after adding the rule:

1. **Wait 30 seconds** - security group changes take a moment to propagate
2. **Restart tunnel**: `python scripts/ssh_tunnel_manager.py stop && python scripts/ssh_tunnel_manager.py start`
3. **Check both security groups**:
   - EC2 SG allows SSH (port 22) from your IP ✅
   - RDS SG allows PostgreSQL (port 5432) from EC2 SG ❌ ← FIX THIS

---

## Need Help?

If you're stuck, check:
- EC2 instance is running
- RDS instance is available (not stopped)
- Correct region (us-east-2)
- Security group IDs match

