# Step-by-step Guide

A step-by-step guide to connecting MongoDB and HubSpot in MindsDB, querying across them, and using an AI agent over the same data.

---

## 1. Create Databases

Connect MongoDB (reviews, product sales) and HubSpot (companies, contacts) as MindsDB datasources.

**MongoDB**

```sql
CREATE DATABASE mongodb_data
WITH ENGINE = 'mongodb',
PARAMETERS = {
    "host": "mongodb+srv://demouser:MindsDB_demo@mindsdb-demo.whljnvh.mongodb.net/demo"
};
```

**HubSpot**

```sql
CREATE DATABASE hubspot_data
WITH ENGINE = 'hubspot',
PARAMETERS = {
    "access_token": "pat-na1-d7a93c10-07d1-45fd-ac7a-b109d00d9e2b"
};
```

---

## 2. Display Data

Verify data from each source.

**HubSpot companies** (sample fields):

```sql
SELECT name, domain, industry, annualrevenue, numberofemployees
FROM hubspot_data.companies
LIMIT 10;
```

**MongoDB reviews** (sample fields):

```sql
SELECT customer_email, product_sku, star_rating, review_title, review_text
FROM mongodb_data.reviews
LIMIT 10;
```

---

## 3. Query Data

### Single-database queries

**Q. What is the average product review rating?**

```sql
SELECT AVG(star_rating) AS average_rating
FROM mongodb_data.reviews;
```

### Cross-database queries

**Q. Who are our top 10 customers by revenue?**

```sql
SELECT
    hc.firstname,
    hc.lastname,
    ROUND(SUM(ps.sales_amount), 2) AS total_revenue
FROM mongodb_data.product_sales AS ps
JOIN hubspot_data.contacts AS hc ON ps.customer_email = hc.email
GROUP BY hc.firstname, hc.lastname
ORDER BY total_revenue DESC
LIMIT 10;
```

---

## 4. Create Agent

Define a `sales_agent` that can answer questions over HubSpot contacts and MongoDB product sales.

```sql
CREATE AGENT sales_agent
USING
    model = {
        "provider": "openai",
        "model_name": "gpt-5.4",
        "api_key": "<your-openai-api-key>"
    },
    data = {
        "tables": [
            "hubspot_data.contacts",
            "mongodb_data.product_sales"
        ]
    },
    prompt_template = '
        hubspot_data.contacts stores CRM contact data including:
        id, email, firstname, lastname, jobtitle, company, city,
        website, lifecyclestage, hs_lead_status.

        mongodb_data.product_sales stores sales order line items including:
        order_number, order_date, customer_email, city, state, product_sku,
        sales_quantity, discount_percent, sales_price, sales_amount,
        sales_tax_percent, tax_amount.

        To join both sources, use:
        hubspot_data.contacts.email = mongodb_data.product_sales.customer_email.
    ',
    timeout = 60;
```

---

## 5. Query Agent

### Single-database question

```sql
SELECT answer FROM sales_agent
WHERE question = 'What is the total revenue in product sales?';
```

### Cross-database question

```sql
SELECT answer FROM sales_agent
WHERE question = 'What is the lifecycle stage of noah.johnson@clearwaterholdings.co, and how much have they spent in total?';
```
