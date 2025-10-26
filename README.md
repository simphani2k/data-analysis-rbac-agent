# data-analysis-rbac-agent
AI data analysis agent with RBAC - role based access control hosted on AWS
This is a monorepo for both the backend and frontend of the app.

# Dataset Requirements for Data Analysis Agent (Retail Sector)
These requirements are for selecting retail datasets to power a data analysis agent. The datasets must be:

- Multi-table (sales, inventory, products, customers, stores, optionally employees/promotions)
- Realistic, with order-level detail, product/category/customer/store info, and time/date fields
- CSV (preferred) or other easy-to-import formats for Postgres/SQL
- Large enough: thousands of records, multiple years if possible
- Documented with basic table and column descriptions

Example Datasets
- Cleaned Contoso Dataset (Kaggle):
https://www.kaggle.com/datasets/bhanuthakurr/cleaned-contoso-dataset
- DemoData.ai Retail Demo Data:
https://demodata.ai/retail
- Retail Sales Analysis SQL Project (GitHub):
https://github.com/najirh/Retail-Sales-Analysis-SQL-Project--P1
https://github.com/Mahanteshrn/SQL-Retail-Data-Analysis
- Sample Sales Data (Kaggle):
https://www.kaggle.com/datasets/kyanyoga/sample-sales-data
- ContosoTR (Kaggle):
https://www.kaggle.com/datasets/kirshoff/contosotr

