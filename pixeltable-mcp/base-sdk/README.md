# Pixeltable MCP Server

This is a simple MCP (Model-Client-Protocol) server that wraps around the Pixeltable SDK, providing a convenient API for working with Pixeltable's multimodal data infrastructure.

## Clone the repo
`gh repo clone pixeltable/mcp-server-pixeltable`

## Docker Setup

### Build the Docker image
```bash
docker build -t pixeltable-mcp-server .
```

### Run the Docker container
```bash
docker run -p 8080:8080 pixeltable-mcp-server
```

This will start the MCP server on port 8080, making it accessible at `http://localhost:8080`.

## Add the tool to Cursor
1. Go to Cursor MCP settings
2. Add MCP > Add Name > Type = 'SSE'
3. For the URL, enter: `http://localhost:8080/sse`

## Alternative: Local Installation

If you prefer to run the server locally without Docker (requires Python >= 3.11):

```bash
pip install -r requirements.txt
```

Then run the server:
```bash
python server.py
```

Note you will need a MCP client to interact with it.

## Security

Tool arguments come from a model, so a prompt injection could put code in them. `add_computed_column`, `create_view`, `execute_query` and `create_query` therefore never run their strings as Python. `safe_expr.py` parses each string with `ast` and walks the tree against an allowlist, building the result directly from the objects.

**Allowed in expressions:**
- Literals (int, float, str, bool, None) and lists/tuples of them
- Columns as `table.<column>` or `<table name>.<column>`
- Comparisons: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Arithmetic: `+`, `-`, `*`, `/`, `//`, `%` (strings and lists support `+` only)
- Logic: `&`, `|`, `~`, plus unary `-` and `+`
- Calls with positional arguments to `lower`, `upper`, `strip`, `len`, `contains`, `startswith`, `endswith`, `capitalize`, `abs`, `round`, `floor`, `ceil`, `year`, `month`, `day`

**Rejected:** everything else, including `_private` and dunder attributes, table methods such as `table.delete`, nested attributes, other names and calls (`__import__`, `open`, `getattr`, ...), keyword arguments, subscripts, lambdas, comprehensions, conditionals, f-strings, walrus, chained comparisons, `and`/`or`/`not` (use `&`, `|`, `~`), and input over 2000 characters.

**`create_query`** accepts a restricted DSL instead of a Python function body: an optional `return ` followed by a method chain on `table` using only `.where(<expr>)`, `.select(<expr>, ...)`, `.order_by(<expr>, asc=<bool>)` and `.limit(<int>)`:

```python
create_query(
    "recent_adults",
    "users",
    "return table.where(table.age >= 18).select(table.name).order_by(table.name, asc=True).limit(10)",
)
```

Named queries take no parameters. They are registered with `pxt.query` and held in memory, so they are lost when the server restarts. No tool runs saved queries yet: they are only registered.

### Run the tests

```bash
pip install pytest
python -m pytest tests -q
```

Tests that need a real Pixeltable database use a temporary `PIXELTABLE_HOME`, and are skipped if it can't be initialized.
