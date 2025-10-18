# RDS Connection Testing Guide

This guide explains how to test connectivity to the Contoso RDS database in AWS.

## Prerequisites

### 1. AWS Account Setup
- AWS account with access to the RDS instance
- RDS PostgreSQL instance running and accessible
- Appropriate IAM permissions

### 2. Network Configuration
- Security group configured to allow inbound traffic on port 5432
- If RDS is in a VPC, ensure network connectivity:
  - EC2 instance in same VPC, OR
  - VPN/Direct Connect configured, OR
  - RDS set to publicly accessible (not recommended for production)

### 3. Database Credentials
You'll need:
- RDS endpoint (e.g., `contoso-db.xxxxx.us-east-1.rds.amazonaws.com`)
- Database name (e.g., `contoso_db`)
- Master username
- Master password
- Port (default: 5432)

## Installation

### Step 1: Install Required Packages

```bash
pip install -r requirements.txt
```

This will install:
- `psycopg2-binary` - PostgreSQL database adapter
- `boto3` - AWS SDK for Python
- `python-dotenv` - Environment variable management
- Other supporting libraries

### Step 2: Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your actual RDS connection details:

```env
# AWS RDS Configuration
RDS_HOST=your-actual-endpoint.rds.amazonaws.com
RDS_PORT=5432
RDS_DATABASE=contoso_db
RDS_USER=postgres
RDS_PASSWORD=your-secure-password

# AWS Credentials (optional if using IAM roles)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

**Security Note**: The `.env` file is in `.gitignore` and should NEVER be committed to version control.

### Step 3: Configure AWS Credentials (Alternative)

Instead of using `.env` for AWS credentials, you can configure them using AWS CLI:

```bash
aws configure
```

This creates `~/.aws/credentials` and `~/.aws/config` files.

## Running the Connection Test

Execute the test script:

```bash
python scripts/test_rds_connection.py
```

## Test Script Features

The script performs the following tests:

### 1. Configuration Validation
- Verifies all required environment variables are set
- Validates connection parameters

### 2. AWS Credentials Test
- Confirms AWS credentials are valid
- Shows account information

### 3. Database Connection Test
- Tests connectivity to RDS endpoint
- Verifies PostgreSQL version
- Reports connection success/failure

### 4. Schema Verification
- Lists all tables in the database
- Shows row counts for each table
- Identifies Contoso dimension tables

### 5. Query Execution Test
- Executes sample queries
- Verifies data can be retrieved
- Shows column structure

## Expected Output

### Successful Connection

```
============================================================
RDS CONNECTION TESTER - CONTOSO DATABASE
============================================================

============================================================
CONFIGURATION VALIDATION
============================================================
✅ RDS_HOST: contoso-db.xxxxx.us-east-1.rds.amazonaws.com
✅ RDS_DATABASE: contoso_db
✅ RDS_USER: postgres
✅ RDS_PASSWORD: ********
✅ RDS_PORT: 5432
✅ AWS_REGION: us-east-1

✅ All required configuration present

============================================================
AWS CREDENTIALS TEST
============================================================
✅ AWS credentials valid
   Account: 123456789012
   User ARN: arn:aws:iam::123456789012:user/admin
   Region: us-east-1

============================================================
DATABASE CONNECTION TEST
============================================================
Connecting to: contoso-db.xxxxx.us-east-1.rds.amazonaws.com:5432/contoso_db
User: postgres

✅ Connection successful!
   PostgreSQL version: PostgreSQL 15.4 on x86_64-pc-linux-gnu...

============================================================
SCHEMA VERIFICATION
============================================================

✅ Found 20 tables:
   - dimaccount: 110 rows
   - dimchannel: 3 rows
   - dimcurrency: 7 rows
   - dimcustomer: 18,869 rows
   - dimdate: 2,556 rows
   ...

============================================================
QUERY EXECUTION TEST
============================================================
Testing query on table: dimproduct

✅ Query executed successfully
   Retrieved 5 rows
   Columns: productkey, productlabel, productname, productdescription...

✅ Connection closed

============================================================
TEST SUMMARY
============================================================
✅ All tests passed!

Connection parameters:
   host: contoso-db.xxxxx.us-east-1.rds.amazonaws.com
   port: 5432
   database: contoso_db
   user: postgres
   region: us-east-1
```

## Troubleshooting

### Connection Timeout

**Error**: `could not connect to server: Operation timed out`

**Solutions**:
1. Verify security group allows inbound on port 5432 from your IP
2. Check VPC network ACLs
3. Ensure RDS endpoint is correct
4. Verify you're connected to the right network (VPN if required)

### Authentication Failed

**Error**: `FATAL: password authentication failed`

**Solutions**:
1. Double-check username and password in `.env`
2. Ensure no extra spaces in credentials
3. Verify master user credentials in AWS Console
4. Check if password has special characters that need escaping

### Database Does Not Exist

**Error**: `FATAL: database "contoso_db" does not exist`

**Solutions**:
1. Verify database name in RDS console
2. Create the database if it doesn't exist:
   ```bash
   psql -h your-endpoint -U postgres -c "CREATE DATABASE contoso_db;"
   ```

### Security Group Issues

**Error**: Connection timeout or "could not connect to server"

**Solutions**:
1. In AWS Console, go to RDS → Databases → Your DB → Connectivity & Security
2. Click on the security group
3. Edit inbound rules:
   - Type: PostgreSQL
   - Port: 5432
   - Source: Your IP address or 0.0.0.0/0 (for testing only)

### RDS Not Publicly Accessible

If your RDS instance is not publicly accessible:

**Option 1**: Make it publicly accessible
1. Go to RDS Console → Your Database
2. Click "Modify"
3. Under "Connectivity", set "Public access" to "Yes"
4. Apply changes

**Option 2**: Use SSH Tunnel (More secure)
```bash
ssh -L 5432:rds-endpoint:5432 ec2-user@your-ec2-ip
```

Then in `.env` use:
```env
RDS_HOST=localhost
RDS_PORT=5432
```

**Option 3**: Run script from EC2 instance in same VPC

## Connection Parameters Summary

After successful testing, document these parameters:

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Host** | `your-endpoint.rds.amazonaws.com` | RDS endpoint |
| **Port** | `5432` | Default PostgreSQL port |
| **Database** | `contoso_db` | Database name |
| **User** | `postgres` | Master username |
| **Region** | `us-east-1` | AWS region |
| **SSL** | `prefer` | SSL mode (default) |

## Next Steps

After successful connection testing:

1. ✅ **Connection Verified** - RDS is accessible and working
2. 📊 **Load Data** - Import Contoso dataset CSV files to RDS tables
3. 🔐 **Setup RBAC** - Configure role-based access control
4. 🤖 **Build Agent** - Integrate RDS with data analysis agent
5. 🌐 **Connect Frontend** - Link Next.js frontend to backend

## Security Best Practices

1. **Never commit `.env` file** - Keep credentials secure
2. **Use IAM database authentication** - For better security
3. **Restrict security groups** - Only allow necessary IPs
4. **Use SSL/TLS** - Enable encrypted connections
5. **Rotate credentials** - Change passwords regularly
6. **Use secrets manager** - Consider AWS Secrets Manager for production

## Additional Resources

- [AWS RDS PostgreSQL Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review AWS CloudWatch logs for RDS
3. Verify VPC and networking configuration
4. Consult AWS support documentation
