"""
FastMCP SQLite Database Server
A simple MCP server that exposes a company database for text-to-SQL agent training.
"""

import sqlite3

# ── Initialize in-memory SQLite database ───────────────────────────────
DB = sqlite3.connect(":memory:")
DB.row_factory = sqlite3.Row

DB.executescript("""
CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    budget REAL NOT NULL
);

CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    role TEXT NOT NULL,
    salary REAL NOT NULL,
    hire_date TEXT NOT NULL
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    lead_id INTEGER REFERENCES employees(id),
    status TEXT NOT NULL CHECK(status IN ('active', 'completed', 'on_hold')),
    budget REAL NOT NULL
);

-- Departments
INSERT INTO departments VALUES (1, 'Engineering',  'San Francisco', 2500000);
INSERT INTO departments VALUES (2, 'Marketing',    'New York',      1200000);
INSERT INTO departments VALUES (3, 'Data Science', 'London',        1800000);
INSERT INTO departments VALUES (4, 'Sales',        'New York',       900000);
INSERT INTO departments VALUES (5, 'Operations',   'San Francisco',  750000);

-- Employees
INSERT INTO employees VALUES (1,  'Alice Chen',      1, 'Senior Engineer',     145000, '2020-03-15');
INSERT INTO employees VALUES (2,  'Bob Martinez',     1, 'Staff Engineer',      175000, '2018-07-01');
INSERT INTO employees VALUES (3,  'Carol White',      2, 'Marketing Manager',   120000, '2019-11-20');
INSERT INTO employees VALUES (4,  'David Kim',        3, 'Data Scientist',      135000, '2021-01-10');
INSERT INTO employees VALUES (5,  'Eva Johnson',      1, 'Junior Engineer',      95000, '2023-06-01');
INSERT INTO employees VALUES (6,  'Frank Brown',      4, 'Sales Lead',          110000, '2020-09-15');
INSERT INTO employees VALUES (7,  'Grace Liu',        3, 'Senior Data Scientist',155000, '2019-04-22');
INSERT INTO employees VALUES (8,  'Henry Wilson',     2, 'Content Strategist',   98000, '2022-02-14');
INSERT INTO employees VALUES (9,  'Irene Davis',      5, 'Operations Manager',  115000, '2020-08-30');
INSERT INTO employees VALUES (10, 'James Taylor',     1, 'Engineering Manager',  165000, '2017-05-12');
INSERT INTO employees VALUES (11, 'Karen Patel',      3, 'ML Engineer',         140000, '2021-09-05');
INSERT INTO employees VALUES (12, 'Leo Nguyen',       4, 'Account Executive',    92000, '2023-01-18');
INSERT INTO employees VALUES (13, 'Maria Garcia',     5, 'Logistics Coordinator', 78000, '2022-07-25');
INSERT INTO employees VALUES (14, 'Nathan Scott',     2, 'Brand Designer',      105000, '2021-03-11');
INSERT INTO employees VALUES (15, 'Olivia Reed',      1, 'DevOps Engineer',     130000, '2020-12-01');

-- Projects
INSERT INTO projects VALUES (1, 'Cloud Migration',     1, 2,  'active',    500000);
INSERT INTO projects VALUES (2, 'Brand Refresh',       2, 3,  'completed', 200000);
INSERT INTO projects VALUES (3, 'Recommendation Engine',3, 7,  'active',    350000);
INSERT INTO projects VALUES (4, 'Q4 Sales Push',       4, 6,  'active',    150000);
INSERT INTO projects VALUES (5, 'Warehouse Automation', 5, 9,  'on_hold',   280000);
INSERT INTO projects VALUES (6, 'ML Pipeline v2',      3, 11, 'active',    420000);
INSERT INTO projects VALUES (7, 'Mobile App Redesign',  1, 10, 'active',    300000);
INSERT INTO projects VALUES (8, 'SEO Overhaul',        2, 8,  'completed', 120000);
""")

import json
from fastmcp import FastMCP

# ── Create the MCP server ──────────────────────────────────────────────
mcp = FastMCP("company-db", instructions="You are a database assistant. Use the tools to explore the database schema and run SQL queries to answer questions about the company data.")

# ── Tool 1: List all tables ───────────────────────────────────────────
@mcp.tool()
def list_tables() -> str:
    """List all tables in the database."""
    cursor = DB.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row["name"] for row in cursor.fetchall()]
    return json.dumps(tables)


# ── Tool 2: Describe a table's schema ─────────────────────────────────
@mcp.tool()
def describe_table(table_name: str) -> str:
    """Get the column names, types, and constraints for a specific table.

    Args:
        table_name: Name of the table to describe.
    """
    # Validate table name to prevent injection
    cursor = DB.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    if not cursor.fetchone():
        return json.dumps({"error": f"Table '{table_name}' not found."})

    columns = DB.execute(f"PRAGMA table_info({table_name})").fetchall()
    schema = [
        {
            "name": col["name"],
            "type": col["type"],
            "nullable": not col["notnull"],
            "primary_key": bool(col["pk"]),
        }
        for col in columns
    ]
    return json.dumps(schema, indent=2)


# ── Tool 3: Run a SQL query ───────────────────────────────────────────
@mcp.tool()
def run_query(sql: str) -> str:
    """Execute a read-only SQL query and return the results.

    Args:
        sql: A SELECT SQL query to run against the database.
    """
    # Block write operations
    stripped = sql.strip().upper()
    if not stripped.startswith("SELECT"):
        return json.dumps({
            "error": "Only SELECT queries are allowed."
        })

    try:
        cursor = DB.execute(sql)
        rows = [dict(row) for row in cursor.fetchall()]
        return json.dumps({"row_count": len(rows), "results": rows}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Run the server ────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8903)