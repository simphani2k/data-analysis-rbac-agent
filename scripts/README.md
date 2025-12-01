# Database Scripts Documentation

This directory contains scripts for testing database connectivity and querying the Contoso retail dataset.

## Directory Structure

```
scripts/
├── tests/               # Connection test scripts
│   ├── test_db_connection.py        # Quick connection test
│   └── test_rds_connection.py       # Comprehensive RDS test
├── samples/             # Sample query scripts
│   ├── simple_queries.py            # Basic query examples
│   └── query_retail_data.py         # Advanced analytics queries
└── utilities/           # Helper utilities
    ├── ssh_tunnel_manager.py        # SSH tunnel management
    └── check_security_groups.py     # Security group checker
```

---

## Test Scripts

### Quick Connection Test

**File:** `tests/test_db_connection.py`

Quick test to verify database connectivity and show available data.

**Usage:**
```bash
python scripts/tests/test_db_connection.py
```

**Output:**
- PostgreSQL version
- Available schemas
- Table counts in `contiso` schema
- Sample row counts for key tables

---

### Comprehensive RDS Test

**File:** `tests/test_rds_connection.py`

Full-featured RDS connection testing with AWS integration.

**Usage:**
```bash
python scripts/tests/test_rds_connection.py
```

**Features:**
- Configuration validation
- AWS credentials check
- Database connection test
- Schema verification
- Sample query execution
- Detailed troubleshooting tips

---

## Sample Query Scripts

### Simple Queries

**File:** `samples/simple_queries.py`

Basic examples demonstrating how to query the Contoso database.

**Usage:**
```bash
python scripts/samples/simple_queries.py
```

**Queries Included:**
1. **Table Row Counts** - Count rows in all tables
2. **Sample Customers** - Retrieve first 5 customers
3. **Sample Products** - Retrieve first 5 products
4. **Stores by Country** - Count stores by country
5. **Product Categories** - List all product categories
6. **Date Range** - Show sales data date range (2005-2011)

**Example Output:**
```
======================================================================
  Query 1: Table Row Counts
======================================================================

Found 25 tables:

  dimcustomer                             18,868 rows
  dimproduct                               2,232 rows
  dimstore                                   305 rows
  factsales                            3,406,088 rows
  factonlinesales                     12,627,607 rows
  factinventory                        8,013,098 rows
```

---

### Advanced Retail Analytics

**File:** `samples/query_retail_data.py`

More complex queries for retail data analysis (Note: Column names may need adjustment).

**Planned Queries:**
- Sales summary (total transactions, revenue)
- Top products by revenue
- Sales by channel
- Top performing stores
- Customer demographics
- Online vs in-store comparison
- Monthly sales trends
- Inventory status

**Note:** This script is currently being updated to match the exact column names in your database.

---

## Database Schema

### Schema: `contiso`

#### Dimension Tables (16 tables)
- `dimaccount` (23 rows)
- `dimchannel` (3 rows)
- `dimcurrency` (27 rows)
- `dimcustomer` (18,868 rows) - Customer information
- `dimdate` (2,555 rows) - Date dimension (2005-2011)
- `dimemployee` (292 rows)
- `dimentity` (420 rows)
- `dimgeography` (673 rows) - Geographic data
- `dimmachine` (7,815 rows)
- `dimoutage` (302 rows)
- `dimproduct` (2,232 rows) - Product catalog
- `dimproductcategory` (7 rows) - Product categories
- `dimproductsubcategory` (43 rows) - Product subcategories
- `dimpromotion` (27 rows)
- `dimsalesterritory` (264 rows)
- `dimscenario` (2 rows)
- `dimstore` (305 rows) - Store locations

#### Fact Tables (9 tables)
- `factexchangerate` (772 rows)
- `factinventory` (8,013,098 rows) - Inventory data
- `factitmachine` (23,282 rows)
- `factitsla` (4,924 rows)
- `factonlinesales` (12,627,607 rows) - Online sales transactions
- `factsales` (3,406,088 rows) - In-store sales transactions
- `factsalesquota` (7,465,910 rows)
- `factstrategyplan` (2,750,627 rows)

**Total Records:** ~38.2 million rows

---

## Prerequisites

### 1. Python Dependencies

Install required packages (already done if you followed setup):
```bash
source .venv/bin/activate
pip install psycopg2-binary python-dotenv boto3
```

### 2. Environment Configuration

Ensure `.env` file in project root contains:
```bash
# Database Configuration
DB_HOST=data-analysis-db-public.checoi26cyca.us-west-1.rds.amazonaws.com
DB_NAME=postgres
DB_USER=postgres
DB_PASS=your_password
DB_PORT=5432

# RDS Configuration (for test scripts)
RDS_HOST=data-analysis-db-public.checoi26cyca.us-west-1.rds.amazonaws.com
RDS_PORT=5432
RDS_DATABASE=postgres
RDS_USER=postgres
RDS_PASSWORD=your_password

# AWS Configuration
AWS_REGION=us-west-1
```

### 3. Network Access

- RDS security group must allow inbound traffic on port 5432 from your IP
- Verify in AWS Console: RDS → Database → Security Groups → Inbound Rules

---

## Usage Examples

### Quick Test
```bash
# Activate virtual environment
source .venv/bin/activate

# Test connection
python scripts/tests/test_db_connection.py

# Run sample queries
python scripts/samples/simple_queries.py
```

### Custom Queries

Example Python script to query the database:

```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Connect to database
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASS'),
    port=os.getenv('DB_PORT')
)

# Execute query
with conn.cursor(cursor_factory=RealDictCursor) as cur:
    cur.execute("""
        SELECT "ProductName", "UnitPrice"
        FROM contiso.dimproduct
        WHERE CAST("UnitPrice" AS NUMERIC) > 100
        LIMIT 10;
    """)

    for row in cur.fetchall():
        print(f"{row['ProductName']}: ${row['UnitPrice']}")

conn.close()
```

**Note:** Column names are case-sensitive. Use double quotes for exact casing (e.g., `"ProductName"`).

---

## Troubleshooting

### Connection Timeout

**Error:** `connection to server ... failed: Operation timed out`

**Solutions:**
1. Check RDS security group allows your IP on port 5432
2. Verify RDS endpoint in `.env` is correct
3. Ensure RDS is publicly accessible (or use SSH tunnel)

### Column Does Not Exist

**Error:** `column "productname" does not exist`

**Solution:** Use exact column casing with double quotes:
```sql
-- Wrong
SELECT productname FROM contiso.dimproduct;

-- Correct
SELECT "ProductName" FROM contiso.dimproduct;
```

### Permission Denied

**Error:** `permission denied for schema contiso`

**Solution:** Ensure database user has SELECT permissions:
```sql
GRANT USAGE ON SCHEMA contiso TO postgres;
GRANT SELECT ON ALL TABLES IN SCHEMA contiso TO postgres;
```

---

## Next Steps

1. **Integrate with AI Chatbot** - Use these queries as templates for natural language data analysis
2. **Create API Endpoints** - Wrap queries in FastAPI endpoints for frontend access
3. **Build Dashboards** - Use data for visualization and analytics
4. **Extend Queries** - Add more complex analysis queries based on business needs

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review connection test output for diagnostic info
3. Verify AWS Console for RDS status and security groups
