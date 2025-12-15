# Data Analysis AI Platform - Requirements Document

**Version:** 1.1  
**Date:** December 14, 2025  
**Project:** Claude-like B2B Data Analysis Platform with Enterprise Database Integration

---

## 1. Executive Summary

Building a B2B SaaS platform that enables businesses to query and analyze their enterprise databases using natural language, with strong data governance, RBAC controls, and team collaboration features. The platform learns from past conversations to improve answer quality over time.

**Target Market:** B2B customers requiring governed data analysis
**Initial Scale:** 5 businesses × 2,000 users each = 10,000 total users
**Core Value Proposition:** Reduce CSV/Excel usage by enabling direct, governed access to enterprise databases with AI-powered insights

---

## 2. Technical Stack

### Frontend
- **Framework:** Next.js (React)
- **API Layer:** Next.js API Routes
- **Real-time:** WebSocket for agent streaming

### Backend
- **API Service:** Node.js (Express + Next.js API routes)
- **Agent Service:** Python (custom framework, no LangGraph)
- **Deployment:** AWS ECS Fargate (Python containers)

### Databases
- **Platform DB:** PostgreSQL (users, projects, conversations, RBAC, audit logs)
- **Vector Search:** pgvector extension (conversation embeddings)
- **Tenant DBs:** Customer databases (AWS RDS, Snowflake, Databricks Unity Catalog)
- **Future:** Neo4j for knowledge graph (Phase 2)

### AI/ML
- **MVP:** Groq API with open-source models (Llama 3.1)
- **Production:** AWS Bedrock with Claude (data stays in AWS VPC)
- **Embeddings:** Text-embedding models for semantic search

### Infrastructure
- **Primary Cloud:** AWS
- **Secondary:** Azure, GCP (future expansion)
- **Cache/Sessions:** Redis
- **File Storage:** S3
- **Auth:** Custom (email/password) + Azure AD SSO

---

## 3. RBAC Workflow Example

To illustrate how the system works, here's a concrete example with three users at a fictional company.

### 3.1 Scenario Setup

**Organization:** Acme Corp (retail company)
- **Database:** Snowflake instance
- **Schemas:** `sales`, `finance`, `hr`
- **Tables:**
  - `sales.orders` (order transactions)
  - `sales.customers` (customer information)
  - `finance.revenue` (revenue data)
  - `hr.employees` (employee information)

**Users:**

| Name | Role | Email | Hierarchy Level |
|------|------|-------|----------------|
| **Alice** | Sales Analyst | alice@acme.com | Analyst (Level 3) |
| **Bob** | Finance Manager | bob@acme.com | Manager (Level 2) |
| **Carol** | CEO | carol@acme.com | Admin (Level 1) |

### 3.2 Permission Matrix

| User | Role | Allowed Schemas | Allowed Tables | Row-Level Rules |
|------|------|----------------|----------------|-----------------|
| **Alice** | Analyst | `sales` | `sales.orders`<br/>`sales.customers` | **Region filter:**<br/>Can only see `region = 'West'` |
| **Bob** | Manager | `sales`<br/>`finance` | All tables in both schemas | **No restrictions:**<br/>Sees all data across all regions |
| **Carol** | Admin | All schemas | All tables | **No restrictions:**<br/>Full access |

### 3.3 Detailed Permissions Configuration

**Alice's Permissions (JSON format):**
```json
{
  "user_id": "user-uuid-111",
  "email": "alice@acme.com",
  "role": "analyst",
  "allowed_schemas": ["sales"],
  "allowed_tables": [
    "sales.orders",
    "sales.customers"
  ],
  "row_level_rules": {
    "sales.orders": {
      "conditions": [
        {
          "column": "region",
          "operator": "=",
          "value": "West"
        }
      ],
      "logic": "AND"
    },
    "sales.customers": {
      "conditions": [
        {
          "column": "region",
          "operator": "=",
          "value": "West"
        }
      ],
      "logic": "AND"
    }
  },
  "temporal_rules": {
    "max_historical_days": 365,
    "date_column_mappings": {
      "sales.orders": "order_date",
      "sales.customers": "created_at"
    }
  },
  "query_limits": {
    "max_rows": 10000,
    "timeout_seconds": 30
  }
}
```

**Bob's Permissions (JSON format):**
```json
{
  "user_id": "user-uuid-222",
  "email": "bob@acme.com",
  "role": "manager",
  "allowed_schemas": ["sales", "finance"],
  "allowed_tables": ["*"],
  "row_level_rules": {},
  "temporal_rules": {
    "max_historical_days": 730
  },
  "query_limits": {
    "max_rows": 50000,
    "timeout_seconds": 60
  }
}
```

**Carol's Permissions (JSON format):**
```json
{
  "user_id": "user-uuid-333",
  "email": "carol@acme.com",
  "role": "admin",
  "allowed_schemas": ["*"],
  "allowed_tables": ["*"],
  "row_level_rules": {},
  "temporal_rules": {},
  "query_limits": {
    "max_rows": 100000,
    "timeout_seconds": 120
  }
}
```

---

### 3.4 Example Workflow: Alice's Query

**Alice asks:** "What were our top customers last month?"

#### Step 1: Authentication & Authorization
```sql
-- User logs in
SELECT id, email, organization_id, role 
FROM users 
WHERE email = 'alice@acme.com' AND password_hash = hash('password123');

-- Returns:
{
  id: 'user-uuid-111',
  email: 'alice@acme.com',
  organization_id: 'org-acme-uuid',
  role: 'analyst'
}
```

#### Step 2: Load User Permissions
```sql
-- Fetch Alice's database permissions
SELECT allowed_schemas, allowed_tables, row_level_rules, query_limits
FROM user_db_permissions
WHERE user_id = 'user-uuid-111' 
  AND organization_id = 'org-acme-uuid';

-- Returns Alice's permissions as shown above
```

#### Step 3: Agent Generates SQL

The agent sees Alice can only access:
- `sales.orders` and `sales.customers` tables
- Data where `region = 'West'`

**Generated SQL:**
```sql
SELECT 
  c.customer_name,
  SUM(o.order_total) as total_revenue,
  COUNT(o.order_id) as order_count
FROM sales.customers c
JOIN sales.orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
  AND o.order_date < DATE_TRUNC('month', CURRENT_DATE)
  AND o.region = 'West'      -- ← Automatically injected by RBAC
  AND c.region = 'West'      -- ← Automatically injected by RBAC
GROUP BY c.customer_name
ORDER BY total_revenue DESC
LIMIT 10;
```

#### Step 4: SQL Validation

**Validation Checks:**
- ✅ **Tables used:** `sales.orders`, `sales.customers` (Alice has access)
- ✅ **Row-level filter applied:** `region = 'West'` (automatically injected)
- ✅ **Query limit:** `LIMIT 10` (under 10,000 max rows)
- ✅ **No forbidden operations:** No `DELETE`, `UPDATE`, `DROP`
- ✅ **Temporal check:** Query within 365-day limit

**Validation Result:** PASSED

#### Step 5: Query Execution

```sql
-- Query executes on Acme's Snowflake database
-- Results: Top 10 West region customers

| customer_name      | total_revenue | order_count |
|--------------------|---------------|-------------|
| TechCorp West      | $125,000     | 45          |
| RetailGiant CA     | $98,500      | 32          |
| ...                | ...          | ...         |
```

#### Step 6: Audit Logging

```sql
-- Log execution for compliance
INSERT INTO sql_execution_log (
  message_id, user_id, organization_id, 
  sql_query, execution_time_ms, rows_returned, success, executed_at
) VALUES (
  'msg-uuid-456',
  'user-uuid-111',           -- Alice
  'org-acme-uuid',           -- Acme Corp
  'SELECT c.customer_name, SUM(o.order_total)...',
  245,                        -- 245ms execution time
  10,                         -- 10 rows returned
  true,                       -- Success
  NOW()
);
```

#### Step 7: Agent Response to Alice

**Agent's Answer:**
```
Based on your sales data for the West region last month:

**Top 5 Customers by Revenue:**
1. TechCorp West - $125,000 (45 orders)
2. RetailGiant CA - $98,500 (32 orders)
3. WestCoast Supplies - $87,300 (28 orders)
4. Pacific Traders - $76,800 (41 orders)
5. Golden State Inc - $65,200 (19 orders)

**Key Insights:**
- TechCorp West significantly outperforms others with 45 orders
- Average order value varies: TechCorp ($2,778), Pacific ($1,873)
- High-frequency customers (40+ orders) generate 55% of total revenue

**Suggested follow-up questions:**
- What products did TechCorp West purchase most?
- How do these numbers compare to last quarter?
- Which customers showed the highest growth?
```

---

### 3.5 What if Bob Asked the Same Question?

**Bob asks:** "What were our top customers last month?"

#### Key Differences:

**Bob's Generated SQL:**
```sql
SELECT 
  c.customer_name,
  c.region,                    -- ← Bob can see region column
  SUM(o.order_total) as total_revenue,
  COUNT(o.order_id) as order_count
FROM sales.customers c
JOIN sales.orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
  AND o.order_date < DATE_TRUNC('month', CURRENT_DATE)
  -- NO region filter - Bob sees ALL regions
GROUP BY c.customer_name, c.region
ORDER BY total_revenue DESC
LIMIT 10;
```

**Bob's Results:**
```
| customer_name      | region | total_revenue | order_count |
|--------------------|--------|---------------|-------------|
| MegaCorp East      | East   | $250,000     | 78          |
| TechCorp West      | West   | $125,000     | 45          |
| SouthernRetail     | South  | $115,000     | 52          |
| ...                | ...    | ...          | ...         |
```

**Key Insight:** Bob sees customers from ALL regions, while Alice only saw West region customers.

---

### 3.6 What if Alice Tried to Query Finance Data?

**Alice asks:** "What was our total revenue last quarter?"

#### Step 1: Agent Generates SQL
```sql
SELECT SUM(revenue_amount) as total_revenue
FROM finance.revenue
WHERE quarter = 'Q3 2024';
```

#### Step 2: Validation FAILS

**Validation Error:**
```
❌ Permission Denied: Table 'finance.revenue' not in allowed_tables
Alice's allowed tables: ['sales.orders', 'sales.customers']
```

#### Step 3: Agent Response to Alice

```
I'm unable to access the finance.revenue table with your current permissions. 
You have access to sales data only.

**What you can query:**
- Sales data: orders, customers, products (West region only)

**To answer your question about total revenue:**
- You would need Finance Manager permissions
- Or I can help you analyze West region sales revenue instead

Would you like me to show West region revenue from sales data?
```

---

### 3.7 Shared Project Scenario

**Setup:**
- Bob creates a project: "Q4 Sales Analysis"
- Bob adds Alice as a member (role: Editor)

**Project Members:**
```sql
INSERT INTO project_members VALUES
('pm-1', 'proj-q4-sales', 'user-uuid-222', 'owner', true, true),   -- Bob (owner)
('pm-2', 'proj-q4-sales', 'user-uuid-111', 'editor', false, true);  -- Alice (editor)
```

**can_view_others_queries Explanation:**
- **Bob:** `true` (Manager can see Alice's queries)
- **Alice:** `false` (Analyst cannot see Bob's queries)

#### Scenario A: Alice Creates a Conversation in Shared Project

**Alice's conversation:**
- Title: "West region customer analysis"
- Contains queries filtered to `region = 'West'`
- SQL queries show only West data

**What Bob sees when viewing the project:**
```
✅ Bob CAN see Alice's conversation
✅ Bob CAN see Alice's SQL queries
✅ Bob CAN see Alice's results (West region data only)
✅ Bob's agent CAN learn from Alice's queries (when Bob asks similar questions)
```

#### Scenario B: Bob Creates a Conversation in Shared Project

**Bob's conversation:**
- Title: "Company-wide sales performance"
- Contains queries with ALL regions (East, West, South, etc.)
- SQL queries show data across all regions

**What Alice sees when viewing the project:**
```
❌ Alice CANNOT see Bob's conversation (not listed in her UI)
❌ Alice CANNOT see Bob's SQL queries
❌ Alice CANNOT see Bob's results
❌ Alice's agent CANNOT learn from Bob's queries (vector search filters by hierarchy)
```

**Rationale:** Prevents Alice from accessing information about other regions through Bob's queries, which would violate her row-level security constraints.

---

### 3.8 Complex Query Example with Alice

**Alice asks:** "How many of our customers have bought more than 2 items in every single order they've made?"

This is a complex query testing the agent's capability.

#### Agent's Multi-Attempt Process

**Attempt 1 (Generated SQL):**
```sql
SELECT COUNT(DISTINCT customer_id) 
FROM sales.orders
WHERE items_count > 2
  AND region = 'West';  -- Auto-injected
```

**Validation Result:** 
```
❌ FAILED - Logic Error
This counts customers with ANY order >2 items, not EVERY order >2 items
```

**Agent Thinking (shown to Alice):**
```
🔄 Attempt 1 failed, retrying...
Error: Logic doesn't match "every order" requirement
```

**Attempt 2 (Generated SQL):**
```sql
SELECT COUNT(DISTINCT customer_id) as customer_count
FROM (
    SELECT 
        customer_id,
        COUNT(*) as total_orders,
        SUM(CASE WHEN items_count > 2 THEN 1 ELSE 0 END) as qualifying_orders
    FROM sales.orders
    WHERE region = 'West'  -- Auto-injected
    GROUP BY customer_id
) subquery
WHERE total_orders = qualifying_orders
  AND total_orders > 0;
```

**Validation Result:**
```
✅ PASSED
- Syntax: Valid
- Permissions: Uses allowed tables only
- Logic: Correctly filters for customers where ALL orders have >2 items
- EXPLAIN: Executable
```

**Agent Thinking (shown to Alice):**
```
✅ SQL query generated successfully (attempt 2)
```

#### Execution & Results

**Query Results:**
```
| customer_count |
|----------------|
| 42             |
```

**Agent's Answer to Alice:**
```
In the West region, **42 customers** have consistently purchased more than 2 items in every single order they've placed.

**Additional Context:**
- This represents approximately 8% of your total West region customer base (42 out of ~520 customers)
- These customers show strong purchasing behavior consistency
- Average order size for this group: 4.3 items per order

**Related past analysis:**
I found a similar analysis from 2 months ago where you looked at high-value customers. 
The overlap between these consistent multi-item buyers and your top revenue customers is 67%.

**Suggested follow-ups:**
- What products do these 42 customers typically buy together?
- How does their customer lifetime value compare to average?
- What's the retention rate for this customer segment?
```

---

### 3.9 Database State (Concrete Data Example)

Here's what the actual data looks like in the platform database:

#### organizations table
```
id                  | name       | slug   | db_connection              | db_type
--------------------|------------|--------|----------------------------|----------
org-acme-uuid       | Acme Corp  | acme   | snowflake://acme.snow...  | snowflake
```

#### users table
```
id              | email              | organization_id   | role
----------------|--------------------|--------------------|--------
user-uuid-111   | alice@acme.com    | org-acme-uuid     | analyst
user-uuid-222   | bob@acme.com      | org-acme-uuid     | manager
user-uuid-333   | carol@acme.com    | org-acme-uuid     | admin
```

#### user_db_permissions table
```
id  | user_id       | allowed_schemas      | allowed_tables                    | row_level_rules
----|---------------|---------------------|-----------------------------------|------------------
p-1 | user-uuid-111 | ["sales"]           | ["sales.orders","sales.customers"]| {"sales.orders": {...region=West}}
p-2 | user-uuid-222 | ["sales","finance"] | ["*"]                            | {}
p-3 | user-uuid-333 | ["*"]               | ["*"]                            | {}
```

#### projects table
```
id              | organization_id | name                | created_by
----------------|-----------------|---------------------|-------------
proj-uuid-1     | org-acme-uuid  | Q4 Sales Analysis   | user-uuid-222
proj-uuid-2     | org-acme-uuid  | West Region Deep Dive| user-uuid-111
```

#### project_members table
```
id   | project_id  | user_id       | role   | can_view_others_queries
-----|-------------|---------------|--------|------------------------
pm-1 | proj-uuid-1 | user-uuid-222 | owner  | true
pm-2 | proj-uuid-1 | user-uuid-111 | editor | false   ← Alice can't see Bob's queries
pm-3 | proj-uuid-2 | user-uuid-111 | owner  | true
```

#### conversations table
```
id              | project_id  | title                      | created_by
----------------|-------------|----------------------------|-------------
conv-uuid-1     | proj-uuid-1 | Top customers analysis     | user-uuid-111  (Alice)
conv-uuid-2     | proj-uuid-1 | Regional sales comparison  | user-uuid-222  (Bob)
conv-uuid-3     | proj-uuid-2 | West coast trends         | user-uuid-111  (Alice)
```

#### messages table
```
id      | conversation_id | role      | content                                  | metadata
--------|-----------------|-----------|------------------------------------------|----------
msg-1   | conv-uuid-1     | user      | What were our top customers last month? | {}
msg-2   | conv-uuid-1     | assistant | Based on your sales data...             | {"sql": "SELECT...", "rows": 10}
msg-3   | conv-uuid-2     | user      | Compare all regions sales               | {}
msg-4   | conv-uuid-2     | assistant | Company-wide analysis shows...          | {"sql": "SELECT...", "rows": 4}
```

#### sql_execution_log table (audit trail)
```
id    | message_id | user_id       | sql_query                    | rows_returned | success | executed_at
------|------------|---------------|------------------------------|---------------|---------|------------
log-1 | msg-2      | user-uuid-111 | SELECT c.customer_name...   | 10            | true    | 2024-12-14 10:30
log-2 | msg-4      | user-uuid-222 | SELECT region, SUM(...)     | 4             | true    | 2024-12-14 11:15
```

**Key Observations:**
- Alice's queries (log-1) only return West region data
- Bob's queries (log-2) return data from all regions
- Every query is logged with user_id for accountability
- Alice's conversation (conv-uuid-1) is visible to Bob
- Bob's conversation (conv-uuid-2) is NOT visible to Alice

---

### 3.10 Vector Search with RBAC

When Alice asks a question, the agent searches past conversations:

```python
# Search for similar conversations
similar_convos = await search_similar_conversations(
    embedding=alice_query_embedding,
    organization_id='org-acme-uuid',
    project_id='proj-uuid-1',
    user_id='user-uuid-111',  # Alice
    top_k=5,
    similarity_threshold=0.7
)
```

**Search Logic:**
```sql
SELECT 
    ce.conversation_id,
    ce.content_summary,
    c.title,
    c.created_by,
    m.metadata->>'sql_query' as sql_query,
    (ce.embedding <=> $1) as similarity_score
FROM conversation_embeddings ce
JOIN conversations c ON ce.conversation_id = c.id
JOIN messages m ON ce.message_id = m.id
WHERE c.organization_id = 'org-acme-uuid'
  AND c.project_id = 'proj-uuid-1'
  AND (
    -- Alice can see her own conversations
    c.created_by = 'user-uuid-111'
    OR
    -- Alice can see conversations from users she CAN view (based on hierarchy)
    -- In this case, Alice CANNOT view Bob's (manager) conversations
    c.created_by IN (
      SELECT u.id FROM users u
      JOIN user_db_permissions p ON u.id = p.user_id
      WHERE u.organization_id = 'org-acme-uuid'
        AND p.role IN ('analyst', 'viewer')  -- Same or lower hierarchy
    )
  )
  AND (ce.embedding <=> $1) < 0.3  -- Similarity threshold
ORDER BY similarity_score ASC
LIMIT 5;
```

**Result for Alice:**
- ✅ Finds Alice's own past conversations
- ✅ Finds other analysts' conversations in the project
- ❌ Does NOT find Bob's (manager) conversations
- ❌ Does NOT find Carol's (admin) conversations

**Result for Bob (if he asked):**
- ✅ Finds Bob's own conversations
- ✅ Finds Alice's (analyst) conversations
- ✅ Finds other analysts' conversations
- ✅ Can learn from all lower-hierarchy users' queries

---

## 4. Core Features (MVP)

### 4.1 User Authentication & Authorization
- Email/password authentication
- Azure AD SSO integration
- JWT-based session management
- Multi-tenant organization isolation

### 4.2 Role-Based Access Control (RBAC)

**Hierarchy:**
- **Admin:** Full access to all data, manage users
- **Manager:** Access to multiple schemas, can view analyst queries
- **Analyst:** Limited schema access, row-level filtering
- **Viewer:** Read-only access to shared analyses

**Permission Controls (Structured Format):**
```json
{
  "allowed_schemas": ["sales", "finance"],
  "allowed_tables": ["sales.orders", "sales.customers"],
  "row_level_rules": {
    "sales.orders": {
      "conditions": [
        {"column": "region", "operator": "IN", "values": ["West", "Southwest"]},
        {"column": "order_date", "operator": ">=", "value": "2024-01-01"}
      ],
      "logic": "AND"
    }
  },
  "temporal_rules": {
    "max_historical_days": 30,
    "allowed_hours": {"start": "08:00", "end": "18:00", "timezone": "America/Los_Angeles"},
    "date_column_mappings": {
      "sales.orders": "order_date"
    }
  },
  "query_limits": {
    "max_rows": 10000,
    "timeout_seconds": 30
  }
}
```

**Query Visibility Rules:**
- Lower hierarchy users CANNOT see higher hierarchy users' queries
- Higher hierarchy users CAN see lower hierarchy users' queries
- Shared projects respect this hierarchy
- Vector search automatically filters based on hierarchy

### 4.3 Projects & Workspaces

**Project Structure:**
- Organization → Projects → Conversations → Messages
- Multiple users can be members of a project
- Project roles: Owner, Editor, Viewer
- Conversations within projects are shared among members (respecting hierarchy)

**Project Members Schema:**
```sql
project_members (
  project_id,
  user_id,
  role,
  can_view_others_queries,  -- Based on hierarchy
  can_execute_queries
)
```

### 4.4 Natural Language to SQL Agent

**Agent Pipeline:**
1. **Search Context** (automatic)
   - Search past conversations using vector similarity
   - Respects user hierarchy (only retrieves visible conversations)
   - Find related SQL queries and insights
   - Show related conversations as suggestions to user

2. **Generate SQL** (with retry logic)
   - Maximum 3 attempts
   - Shows "Attempt X failed, retrying..." to user
   - Uses past conversation context for better SQL generation
   - Validates against user permissions and schema
   - Automatically injects row-level filters
   - Automatically injects temporal filters
   - If all attempts fail: show error + best SQL attempt

3. **Execute SQL** (automatic)
   - Runs on tenant's database (Snowflake/RDS/Databricks)
   - Applies RBAC filters automatically (user cannot bypass)
   - Enforces row-level security
   - Enforces temporal restrictions
   - Logs all executions for audit

4. **Generate Answer** (automatic)
   - Provides insights from results
   - Compares with past analyses (respecting hierarchy)
   - Suggests follow-up questions
   - Handles errors gracefully

**User Experience:**
- **Option C (Hybrid):** Collapsible "Agent Thinking" section in UI
- User sees thinking steps, SQL generation, validation, execution
- Defaults to clean final answer
- SQL displayed in editable code block
- User can edit SQL and re-run manually
- Results shown in table format
- Natural language answer with insights
- Links to related past conversations (that user has permission to see)

### 4.5 SQL Validation & Safety

**Multi-layer Validation:**
1. **Syntax Validation:** Check SQL is well-formed
2. **Permission Validation:** Verify tables/schemas are allowed
3. **EXPLAIN Validation:** Test query is executable without running
4. **Automatic Filter Injection:** Add row-level and temporal filters
5. **Execution Limits:** Timeout and max rows enforcement

**Prohibited Operations:**
- DELETE, UPDATE, DROP, TRUNCATE
- Schema modifications (CREATE, ALTER)
- System table access

### 4.6 Conversation History & Search

**Features:**
- All conversations stored with embeddings
- Semantic search across past conversations
- Agent automatically retrieves relevant context (respecting hierarchy)
- Users can manually search past analyses
- Conversation metadata: title, summary, tags
- Message threading (parent-child relationships)
- Hierarchy-aware search (users only see conversations they have permission to view)

**Storage:**
```sql
conversations (id, project_id, title, created_by, metadata)
messages (id, conversation_id, role, content, metadata, parent_message_id)
conversation_embeddings (id, conversation_id, message_id, embedding VECTOR(1536), content_summary)
```

### 4.7 Audit & Compliance

**SQL Execution Log:**
```sql
sql_execution_log (
  message_id,
  user_id,
  organization_id,
  sql_query,
  execution_time_ms,
  rows_returned,
  success,
  error_message,
  executed_at
)
```

**Audit Features:**
- Every SQL query logged (success or failure)
- User actions tracked
- Execution times recorded
- Full query history per user/organization
- Export capabilities for compliance reports

### 4.8 Multi-Tenancy & Crisis Control

**Isolation Strategy:**
- Separate PostgreSQL database per tenant organization
- Single RDS instance initially (cost-effective)
- Connection pooling with circuit breakers
- If one tenant DB fails, others unaffected
- Migration path to separate RDS instances per tenant

**Data Encryption:**
- Encryption at rest (database level)
- Encryption in transit (TLS/SSL)
- Database credentials encrypted in platform DB
- Secrets managed via AWS Secrets Manager

---

## 5. Future Features (Post-MVP)

### 5.1 Knowledge Graph (Phase 2)
- Neo4j integration
- Store entities: tables, columns, metrics, insights
- Relationships: "Revenue relates to sales_table.amount_column"
- Query history graph: "User X found insight Y about metric Z"
- Semantic layer for business definitions

### 5.2 RLHF & Human-in-the-Loop (Phase 2)
- Present users with 2 different SQL/answers
- Ask which is more accurate/truthful
- Store feedback for model fine-tuning
- Continuous improvement of SQL generation quality

### 5.3 Advanced Features (Phase 3)
- File uploads (discouraged, but CSV/Excel processing if needed)
- Data visualization generation (charts, dashboards)
- Scheduled queries and reports
- Email/Slack alerts for insights
- API access for programmatic queries
- Custom dashboard builder

---

## 6. Database Schema

### 6.1 Platform Database (PostgreSQL)

**Core Tables:**
```sql
-- Organizations (tenants)
organizations (
  id UUID PRIMARY KEY,
  name VARCHAR(255),
  slug VARCHAR(100) UNIQUE,
  db_connection_string TEXT ENCRYPTED,
  db_type VARCHAR(50),  -- 'postgres', 'snowflake', 'databricks'
  created_at TIMESTAMP,
  settings JSONB
)

-- Users
users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  password_hash TEXT,  -- null if SSO only
  full_name VARCHAR(255),
  organization_id UUID REFERENCES organizations(id),
  role VARCHAR(50),  -- 'admin', 'manager', 'analyst', 'viewer'
  created_at TIMESTAMP,
  last_login TIMESTAMP
)

-- RBAC Permissions
user_db_permissions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  organization_id UUID REFERENCES organizations(id),
  allowed_schemas TEXT[],
  allowed_tables TEXT[],
  row_level_rules JSONB,  -- Structured format
  temporal_rules JSONB,   -- Time-based restrictions
  query_limits JSONB,
  UNIQUE(user_id, organization_id)
)

-- Projects (Workspaces)
projects (
  id UUID PRIMARY KEY,
  organization_id UUID REFERENCES organizations(id),
  name VARCHAR(255),
  description TEXT,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP,
  settings JSONB
)

-- Project Members (for sharing)
project_members (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  user_id UUID REFERENCES users(id),
  role VARCHAR(50),  -- 'owner', 'editor', 'viewer'
  can_view_others_queries BOOLEAN,  -- Hierarchy-based
  can_execute_queries BOOLEAN,
  added_at TIMESTAMP,
  UNIQUE(project_id, user_id)
)

-- Conversations
conversations (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  title VARCHAR(500),
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  metadata JSONB  -- tags, summary, etc.
)

-- Messages
messages (
  id UUID PRIMARY KEY,
  conversation_id UUID REFERENCES conversations(id),
  role VARCHAR(20),  -- 'user', 'assistant', 'system'
  content TEXT,
  created_at TIMESTAMP,
  metadata JSONB,  -- SQL queries, execution results, thinking steps
  parent_message_id UUID REFERENCES messages(id)
)

-- Audit Log
sql_execution_log (
  id UUID PRIMARY KEY,
  message_id UUID REFERENCES messages(id),
  user_id UUID REFERENCES users(id),
  organization_id UUID REFERENCES organizations(id),
  sql_query TEXT,
  execution_time_ms INTEGER,
  rows_returned INTEGER,
  success BOOLEAN,
  error_message TEXT,
  executed_at TIMESTAMP
)

-- Vector Search (pgvector)
conversation_embeddings (
  id UUID PRIMARY KEY,
  conversation_id UUID REFERENCES conversations(id),
  message_id UUID REFERENCES messages(id),
  embedding VECTOR(1536),  -- Dimension depends on model
  content_summary TEXT,
  created_at TIMESTAMP
)

-- Optional: Business Metadata (helps SQL generation)
database_metadata (
  id UUID PRIMARY KEY,
  organization_id UUID REFERENCES organizations(id),
  table_name VARCHAR(255),
  column_name VARCHAR(255),
  business_definition TEXT,
  sample_query TEXT,
  created_at TIMESTAMP
)
```

### 6.2 Tenant Databases
- Customer's existing databases (no schema changes)
- Read-only access from platform
- Support: PostgreSQL, Snowflake, Databricks Unity Catalog

---

## 7. Agent Architecture

### 7.1 Custom Framework (No LangGraph)

**Components:**
- **AgentState:** Immutable state object passed between nodes
- **BaseNode:** Abstract class for all nodes
- **AgentOrchestrator:** Main controller for pipeline execution

**Nodes (Sequential Pipeline):**
1. **SearchContextNode**
   - Generates embedding for user query
   - Searches pgvector for similar conversations
   - Filters results based on user hierarchy
   - Returns top 5 related analyses (that user can see)

2. **GenerateSQLNode**
   - Loads user permissions and schema
   - Calls LLM (Groq/Bedrock) with context
   - Validates SQL (3 attempts max)
   - Shows retry messages to user
   - Automatically injects row-level filters
   - Automatically injects temporal filters
   - If all fail: returns best attempt + error

3. **ExecuteSQLNode**
   - Executes SQL with RBAC enforcement
   - Applies row-level filters automatically
   - Applies temporal filters automatically
   - Logs execution to audit trail
   - Enforces timeout and row limits

4. **GenerateAnswerNode**
   - Calls LLM with results + past insights
   - Generates natural language answer
   - Suggests follow-up questions
   - Handles error explanations gracefully

**State Streaming:**
- Each node yields state updates
- WebSocket streams to frontend in real-time
- Frontend shows collapsible "Agent Thinking" section

### 7.2 Agent State Structure

```python
@dataclass
class AgentState:
    # Request context
    user_query: str
    conversation_id: str
    user_id: str
    organization_id: str
    project_id: str
    user_permissions: Dict[str, Any]
    
    # Status tracking
    status: AgentStatus  # IDLE, SEARCHING, GENERATING_SQL, etc.
    current_node: str
    
    # Search results
    retrieved_conversations: List[Dict]
    
    # SQL generation
    sql_query: Optional[str]
    sql_generation_attempts: List[Dict]
    current_attempt: int
    max_attempts: int = 3
    validation_errors: List[str]
    sql_is_valid: bool
    
    # Execution results
    sql_results: Optional[Dict]
    execution_time_ms: Optional[int]
    
    # Final output
    final_answer: Optional[str]
    suggested_follow_ups: List[str]
    
    # Thinking process (for UI)
    thinking_steps: List[Dict]
    
    # Error handling
    error: Optional[str]
    error_type: Optional[str]
```

---

## 8. API Endpoints

### 8.1 Authentication
```
POST /api/auth/login
Body: { email, password }
Response: { token, user, organization }

POST /api/auth/sso
Body: { azure_token }
Response: { token, user, organization }

POST /api/auth/logout
```

### 8.2 Projects
```
GET /api/projects
Response: { projects[] }

POST /api/projects
Body: { name, description, organization_id }
Response: { project }

GET /api/projects/:id
Response: { project, members, conversations }

POST /api/projects/:id/members
Body: { user_id, role }
Response: { member }
```

### 8.3 Conversations
```
GET /api/conversations/:id/messages
Response: { messages[], has_more }

POST /api/conversations/:id/messages
Body: { content, role: 'user' }
Response: { message_id }
```

### 8.4 Agent (WebSocket)
```
WS /api/agent/query
Send: { query, conversation_id, project_id }
Receive (stream):
  - { type: "agent_update", data: { status, thinking_steps, sql_query, results } }
  - { type: "agent_complete", data: { final_answer, suggested_follow_ups } }
```

### 8.5 SQL Execution (Manual)
```
POST /api/sql/execute
Body: { sql_query, conversation_id, edited: true }
Response: { results, execution_time }
```

---

## 9. Security & Compliance

### 9.1 Data Security
- **Encryption at rest:** Database-level encryption
- **Encryption in transit:** TLS 1.3 for all connections
- **Secrets management:** AWS Secrets Manager
- **Database credentials:** Encrypted in platform DB
- **API authentication:** JWT tokens with expiration
- **Rate limiting:** Per user/organization

### 9.2 RBAC Enforcement
- **Schema-level:** Only allowed schemas accessible
- **Table-level:** Only allowed tables queryable
- **Row-level:** Automatic filter injection (user cannot bypass)
- **Temporal:** Date range restrictions enforced
- **Query limits:** Timeout and max rows enforced
- **Operation restrictions:** No DELETE/UPDATE/DROP/CREATE
- **Hierarchy-based visibility:** Lower roles cannot see higher roles' queries

### 9.3 Audit Trail
- All SQL queries logged (success and failure)
- User actions tracked
- Execution times recorded
- Results row counts stored
- Exportable for compliance audits

### 9.4 Compliance (Future)
- SOC 2 Type II certification path
- GDPR compliance (data residency, right to deletion)
- HIPAA compliance (if handling healthcare data)
- ISO 27001 certification path

---

## 10. Deployment Architecture

### 10.1 AWS Infrastructure

```
┌─────────────────────────────────────────────┐
│              AWS Account                     │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │         VPC (us-east-1)                │ │
│  │                                        │ │
│  │  ┌──────────────┐  ┌───────────────┐ │ │
│  │  │ Public Subnet│  │Private Subnet │ │ │
│  │  │              │  │               │ │ │
│  │  │  - ALB       │  │ - ECS Fargate │ │ │
│  │  │  - NAT GW    │  │   (Python)    │ │ │
│  │  └──────────────┘  │ - RDS         │ │ │
│  │                    │ - Redis       │ │ │
│  │                    └───────────────┘ │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  Managed Services                      │ │
│  │  - S3 (file storage)                  │ │
│  │  - Secrets Manager                    │ │
│  │  - CloudWatch (monitoring)            │ │
│  │  - WAF (security)                     │ │
│  │  - Bedrock (LLM - production)         │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### 10.2 Service Deployment

**Frontend (Next.js):**
- Vercel or AWS Amplify hosting
- Static assets on CloudFront CDN

**Backend (Node.js):**
- Next.js API routes (serverless)
- Or ECS Fargate for long-running connections

**Agent Service (Python):**
- ECS Fargate containers
- Auto-scaling based on CPU/memory
- Health checks and automatic recovery

**Databases:**
- RDS PostgreSQL (platform + tenant DBs)
- Redis ElastiCache (sessions, caching)

---

## 11. Non-Functional Requirements

### 11.1 Performance
- **Query response time:** <5 seconds for simple queries
- **Complex queries:** <30 seconds (with progress indication)
- **Concurrent users:** Support 1,000 concurrent queries
- **Agent thinking latency:** Stream updates every 1-2 seconds

### 11.2 Scalability
- **Horizontal scaling:** ECS Fargate auto-scaling
- **Database scaling:** Read replicas for tenant DBs
- **Cache layer:** Redis for frequent queries
- **Vector search:** Optimize pgvector indexes for <100ms search

### 11.3 Reliability
- **Uptime SLA:** 99.9% (Phase 1), 99.95% (Production)
- **Circuit breakers:** Prevent cascading tenant DB failures
- **Graceful degradation:** Continue operation if vector search fails
- **Retry logic:** 3 attempts for SQL generation with backoff

### 11.4 Monitoring
- **Metrics:** Query latency, error rates, SQL validation failures
- **Logging:** Centralized logging (CloudWatch or ELK stack)
- **Alerting:** PagerDuty/Opsgenie for critical failures
- **Dashboards:** Grafana for real-time metrics

---

## 12. Success Metrics

### 12.1 Business Metrics
- **User adoption:** 70% of users query database weekly
- **CSV reduction:** 50% decrease in CSV/Excel usage
- **Query accuracy:** >85% SQL queries execute successfully
- **User satisfaction:** NPS score >50

### 12.2 Technical Metrics
- **SQL generation success rate:** >80% (first attempt)
- **Query execution success rate:** >95%
- **Average query time:** <10 seconds
- **Vector search relevance:** >70% users find past conversations helpful

---

## 13. MVP Timeline Estimate

**Phase 1: Foundation (4-6 weeks)**
- Database schema + migrations
- User authentication (email/password + Azure AD SSO)
- Basic RBAC setup
- Project/workspace structure

**Phase 2: Core Agent (6-8 weeks)**
- Custom agent framework (4 nodes)
- SQL generation with Groq
- SQL validation (3-layer)
- Query execution with RBAC
- WebSocket streaming
- Frontend UI for chat interface

**Phase 3: Search & Context (3-4 weeks)**
- pgvector setup
- Embedding generation
- Conversation search
- Context retrieval in agent
- Hierarchy-aware search filtering

**Phase 4: Polish & Testing (3-4 weeks)**
- Error handling improvements
- UI/UX refinement
- Security audit
- Load testing
- Documentation

**Total MVP Timeline: 16-22 weeks (4-5.5 months)**

---

## 14. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| SQL generation quality poor with smaller models | High | Add retry logic (3 attempts), fallback to manual SQL editing, collect good examples for few-shot prompting |
| Tenant DB performance impact | High | Query timeouts, row limits, connection pooling, circuit breakers |
| RBAC bypasses | Critical | Multi-layer validation, automatic filter injection, audit all queries |
| User expects 100% accuracy | Medium | Set expectations upfront, show confidence scores, allow manual SQL editing |
| Complex queries fail | Medium | Query decomposition (Phase 2), ask clarifying questions, human-in-loop |
| Scalability bottlenecks | Medium | Horizontal scaling, caching, read replicas, async processing |
| Hierarchy violations | Critical | Enforce hierarchy in code, test edge cases, audit conversation visibility |

---

## 15. Open Questions

1. **Pricing model:** Per user? Per query? Per organization?
2. **Data retention:** How long to keep conversation history?
3. **Tenant onboarding:** Self-service or sales-assisted?
4. **Custom model fine-tuning:** When to invest in fine-tuned models?
5. **Competitive analysis:** How do we differentiate from ThoughtSpot, Mode, Hex?

---

## 16. Next Steps

1. **Week 1-2:** Set up infrastructure (AWS, databases, Redis)
2. **Week 3-4:** Implement authentication + RBAC schema
3. **Week 5-8:** Build custom agent framework
4. **Week 9-12:** Frontend chat interface + WebSocket integration
5. **Week 13-16:** Testing, security audit, documentation
6. **Week 17+:** Beta launch with first customer (Acme Corp scenario)

---

**Document Owner:** Paddy  
**Last Updated:** December 14, 2025  
**Status:** Draft v1.1