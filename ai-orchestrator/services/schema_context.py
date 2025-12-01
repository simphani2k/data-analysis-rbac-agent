"""
Database Schema Context for AI SQL Generation

Provides schema information to help the AI generate accurate SQL queries.
"""

CONTOSO_SCHEMA_DESCRIPTION = """
# Contoso Retail Database Schema

## Schema: contiso

This is a retail data warehouse containing sales, customer, product, and inventory data from 2005-2011.

### Dimension Tables

**dimcustomer** (18,868 rows) - Customer information
- CustomerKey (primary key)
- GeographyKey (foreign key to dimgeography)
- FirstName, LastName
- BirthDate
- MaritalStatus (M/S)
- Gender (M/F)
- YearlyIncome (numeric)
- TotalChildren, NumberChildrenAtHome (numeric)
- Education (e.g., "Bachelors", "Graduate Degree")
- Occupation (e.g., "Professional", "Skilled Manual")
- HouseOwnerFlag (0/1)
- NumberCarsOwned (numeric)

**dimproduct** (2,232 rows) - Product catalog
- ProductKey (primary key)
- ProductName (text)
- ProductDescription (text)
- ProductSubcategoryKey (foreign key)
- Manufacturer (text)
- BrandName (text)
- ClassName (e.g., "Economy", "Regular", "Deluxe")
- ColorName (text)
- UnitCost, UnitPrice (numeric as text - needs CAST)
- AvailableForSaleDate (date)
- Status (text)

**dimproductcategory** (7 rows) - Product categories
- ProductCategoryKey (primary key)
- ProductCategoryName (e.g., "Computers", "TV and Video", "Cell phones")

**dimproductsubcategory** (43 rows) - Product subcategories
- ProductSubcategoryKey (primary key)
- ProductSubcategoryName (text)
- ProductCategoryKey (foreign key)

**dimstore** (305 rows) - Store locations
- StoreKey (primary key)
- GeographyKey (foreign key to dimgeography)
- StoreName (text)
- StoreType (text)
- Status (text)

**dimgeography** (673 rows) - Geographic information
- GeographyKey (primary key)
- CityName (text)
- StateProvinceName (text)
- RegionCountryName (text - country name)
- ContinentName (text)

**dimdate** (2,555 rows) - Date dimension (2005-2011)
- DateKey (primary key)
- FullDateAlternateKey (date)
- CalendarYear (e.g., 2007)
- CalendarQuarter (1-4)
- CalendarMonth (1-12)
- MonthLabel (e.g., "January 2007")
- CalendarWeek (1-53)
- DayOfWeek (1-7)

**dimchannel** (3 rows) - Sales channels
- ChannelKey (primary key)
- ChannelName (e.g., "Store", "Online", "Catalog")

**dimpromotion** (27 rows) - Promotions
- PromotionKey (primary key)
- PromotionName (text)
- DiscountPercent (numeric)
- PromotionType (text)

### Fact Tables

**factsales** (3,406,088 rows) - In-store sales transactions
- SalesKey (primary key - stored as text)
- DateKey (foreign key - stored as text)
- channelKey (foreign key - stored as text)
- StoreKey (foreign key - stored as text)
- ProductKey (foreign key - stored as text)
- PromotionKey (foreign key - stored as text)
- SalesQuantity (numeric as text - needs CAST)
- SalesAmount (numeric as text - needs CAST)
- ReturnQuantity (numeric as text - needs CAST)
- ReturnAmount (numeric as text - needs CAST)
- DiscountQuantity (numeric as text - needs CAST)
- DiscountAmount (numeric as text - needs CAST)

**factonlinesales** (12,627,607 rows) - Online sales transactions
- OnlineSalesKey (primary key - stored as text)
- DateKey (foreign key - stored as text)
- ProductKey (foreign key - stored as text)
- SalesQuantity (numeric as text - needs CAST)
- SalesAmount (numeric as text - needs CAST)
- ReturnQuantity (numeric as text - needs CAST)
- ReturnAmount (numeric as text - needs CAST)

**factinventory** (8,013,098 rows) - Inventory levels
- InventoryKey (primary key)
- DateKey (foreign key)
- StoreKey (foreign key)
- ProductKey (foreign key)
- OnHandQuantity (numeric as text - needs CAST)
- OnSalesQuantity (numeric as text - needs CAST)

### Important Notes

1. **Column Names**: ALL column names are case-sensitive. Use exact casing with double quotes.
   - Example: "ProductName" not productname
   - Example: "SalesAmount" not salesamount

2. **Numeric Fields**: Many numeric fields are stored as TEXT and need CAST:
   - CAST("SalesAmount" AS NUMERIC)
   - CAST("UnitPrice" AS NUMERIC)

3. **Schema Prefix**: All tables are in the 'contiso' schema:
   - Use: SELECT * FROM contiso.dimproduct
   - Not: SELECT * FROM dimproduct

4. **Common Joins**:
   - Sales to Products: factsales."ProductKey" = dimproduct."ProductKey"
   - Sales to Stores: factsales."StoreKey" = dimstore."StoreKey"
   - Stores to Geography: dimstore."GeographyKey" = dimgeography."GeographyKey"
   - Sales to Dates: factsales."DateKey" = dimdate."DateKey"
   - Products to Categories: dimproduct."ProductSubcategoryKey" = dimproductsubcategory."ProductSubcategoryKey"

5. **Date Range**: Data spans from 2005 to 2011

6. **Key Metrics**:
   - Total Sales = SUM(CAST("SalesAmount" AS NUMERIC))
   - Total Quantity = SUM(CAST("SalesQuantity" AS NUMERIC))
   - Average Price = AVG(CAST("UnitPrice" AS NUMERIC))
"""


EXAMPLE_QUERIES = {
    "list_products": """
        SELECT "ProductName", CAST("UnitPrice" AS NUMERIC) as price
        FROM contiso.dimproduct
        LIMIT 10;
    """,

    "stores_by_country": """
        SELECT
            g."RegionCountryName" as country,
            COUNT(*) as store_count
        FROM contiso.dimstore s
        LEFT JOIN contiso.dimgeography g ON s."GeographyKey" = g."GeographyKey"
        WHERE g."RegionCountryName" IS NOT NULL
        GROUP BY g."RegionCountryName"
        ORDER BY store_count DESC;
    """,

    "top_selling_products": """
        SELECT
            p."ProductName",
            SUM(CAST(s."SalesQuantity" AS NUMERIC)) as total_quantity,
            SUM(CAST(s."SalesAmount" AS NUMERIC)) as total_revenue
        FROM contiso.factsales s
        JOIN contiso.dimproduct p ON s."ProductKey" = p."ProductKey"
        GROUP BY p."ProductName"
        ORDER BY total_revenue DESC
        LIMIT 10;
    """,

    "customer_demographics": """
        SELECT
            "Gender",
            COUNT(*) as customer_count,
            AVG("YearlyIncome") as avg_income
        FROM contiso.dimcustomer
        WHERE "Gender" IS NOT NULL
        GROUP BY "Gender";
    """,

    "product_categories": """
        SELECT *
        FROM contiso.dimproductcategory
        ORDER BY "ProductCategoryName";
    """
}


def get_schema_context() -> str:
    """Get the full schema context for AI prompts."""
    return CONTOSO_SCHEMA_DESCRIPTION


def get_example_queries() -> dict:
    """Get example queries for reference."""
    return EXAMPLE_QUERIES
