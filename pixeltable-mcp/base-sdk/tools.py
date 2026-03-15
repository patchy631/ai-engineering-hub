import ast
import operator
import re

import pixeltable as pxt
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Pixeltable")


# Safe expression evaluator to avoid eval()/exec() with untrusted input.
# Only allows attribute access on the table object, basic operators, and literals.

_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.USub: operator.neg,
    ast.Not: operator.invert,  # Use ~ (invert) instead of not for Pixeltable expressions
}

# Validate identifiers to prevent injection through crafted attribute names
_IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def _safe_eval(expression: str, table):
    """Evaluate a simple expression safely against a Pixeltable table.

    Supports: table.column references, arithmetic/comparison operators,
    string/number/boolean literals, and parenthesized sub-expressions.

    Raises ValueError for any unsupported or potentially dangerous construct.
    """
    if len(expression) > 2000:
        raise ValueError("Expression too long (max 2000 characters).")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Invalid expression syntax: {e}") from e

    return _eval_node(tree.body, {"table": table})


def _eval_node(node, namespace):
    """Recursively evaluate an AST node using only safe operations."""

    # Literals: numbers, strings, booleans, None
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float, str, bool, type(None))):
            raise ValueError(
                f"Unsupported literal type: {type(node.value).__name__}"
            )
        return node.value

    # Variable lookup (only 'table' allowed; True/False/None are ast.Constant on 3.8+)
    if isinstance(node, ast.Name):
        if node.id == "table":
            return namespace["table"]
        raise ValueError(
            f"Unsupported variable '{node.id}'. Only 'table' references are allowed."
        )

    # Attribute access: table.column_name
    if isinstance(node, ast.Attribute):
        value = _eval_node(node.value, namespace)
        attr = node.attr
        if not _IDENTIFIER_RE.match(attr):
            raise ValueError(f"Invalid attribute name: '{attr}'")
        if attr.startswith("_"):
            raise ValueError(f"Access to private attribute '{attr}' is not allowed.")
        if not hasattr(value, attr):
            raise ValueError(f"Attribute '{attr}' not found.")
        return getattr(value, attr)

    # Binary operations: +, -, *, /, //, %, ==, !=, <, <=, >, >=
    if isinstance(node, ast.BinOp):
        op_func = _SAFE_OPERATORS.get(type(node.op))
        if op_func is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        left = _eval_node(node.left, namespace)
        right = _eval_node(node.right, namespace)
        return op_func(left, right)

    # Comparison operations (handles chained comparisons like a < b < c correctly)
    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, namespace)
        result = None
        for op, comparator in zip(node.ops, node.comparators):
            op_func = _SAFE_OPERATORS.get(type(op))
            if op_func is None:
                raise ValueError(f"Unsupported comparison: {type(op).__name__}")
            right = _eval_node(comparator, namespace)
            cmp = op_func(left, right)
            result = cmp if result is None else (result & cmp)
            left = right
        return result

    # Unary operations: -, not
    if isinstance(node, ast.UnaryOp):
        op_func = _SAFE_OPERATORS.get(type(node.op))
        if op_func is None:
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        return op_func(_eval_node(node.operand, namespace))

    # Boolean operations: and, or
    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            result = _eval_node(node.values[0], namespace)
            for v in node.values[1:]:
                result = result & _eval_node(v, namespace)
            return result
        if isinstance(node.op, ast.Or):
            result = _eval_node(node.values[0], namespace)
            for v in node.values[1:]:
                result = result | _eval_node(v, namespace)
            return result

    raise ValueError(
        f"Unsupported expression type: {type(node).__name__}. "
        "Only column references, operators, and literals are allowed."
    )


@mcp.tool()
def create_table(table_name: str, columns: dict[str, str]) -> str:
    """Create a table in Pixeltable.

    Args:
        table_name: The name of the table to create.
        columns: A dictionary of column names and types.

    Eligible column types:

    from .type_system import (
        Array,
        Audio,
        Bool,
        Document,
        Float,
        Image,
        Int,
        Json,
        Required,
        String,
        Timestamp,
        Video,
    )

    Example:
    columns = {
        "name": String,
        "age": Int,
        "is_active": Bool,
    }

    """
    # Map string type names to actual Pixeltable types
    type_mapping = {
        "array": pxt.Array,
        "audio": pxt.Audio,
        "bool": pxt.Bool,
        "document": pxt.Document,
        "float": pxt.Float,
        "image": pxt.Image,
        "int": pxt.Int,
        "json": pxt.Json,
        "required": pxt.Required,
        "string": pxt.String,
        "timestamp": pxt.Timestamp,
        "video": pxt.Video,
    }

    # Convert string type names to actual type objects
    converted_columns = {}
    for col_name, col_type in columns.items():
        col_type_lower = col_type.lower()
        if col_type_lower in type_mapping:
            converted_columns[col_name] = type_mapping[col_type_lower]
        else:
            return f"Invalid column type: {col_type}. Valid types are: {', '.join(type_mapping.keys())}"

    pxt.create_table(table_name, schema_or_df=converted_columns, if_exists="replace")
    if table_name in pxt.list_tables():
        return f"Table {table_name} created successfully."
    else:
        return f"Table {table_name} creation failed."


@mcp.tool()
def insert_data(table_name: str, data: list[dict]) -> str:
    """Insert data into a table in Pixeltable.

    Args:
        table_name: The name of the table to insert data into.
        data: A list of dictionaries, each representing a row of data.
        The keys of the dictionary should match the column names and types of the table.
    """
    try:
        table = pxt.get_table(table_name)
        if table is None:
            return f"Error: Table {table_name} not found."
        table.insert(data)
        return f"Data inserted successfully."
    except Exception as e:
        return f"Error inserting data: {str(e)}"


@mcp.tool()
def add_computed_column(table_name: str, column_name: str, expression: str) -> str:
    """Add a computed column to a table in Pixeltable.

    Args:
        table_name: The name of the table to add the computed column to.
        column_name: The name of the computed column to add.
        expression: A string representation of the Python expression to compute the column.
                   The expression should refer to other columns in the table using
                   the notation 'table.column_name'.

    Example:
        add_computed_column("my_table", "full_name", "table.first_name + ' ' + table.last_name")
        add_computed_column("my_table", "yoy_change", "table.pop_2023 - table.pop_2022")
    """
    try:
        table = pxt.get_table(table_name)
        if table is None:
            return f"Error: Table {table_name} not found."

        column_expr = _safe_eval(expression, table)

        # Add the computed column with kwargs format
        kwargs = {column_name: column_expr}
        table.add_computed_column(**kwargs)

        return f"Computed column '{column_name}' added successfully to table '{table_name}'."
    except ValueError as e:
        return f"Error: Invalid expression: {e}"
    except Exception as e:
        return f"Error adding computed column: {str(e)}"


@mcp.tool()
def create_view(view_name: str, table_name: str, filter_expr: str = None) -> str:
    """Create a view based on a table in Pixeltable.

    Args:
        view_name: The name of the view to create.
        table_name: The name of the base table for the view.
        filter_expr: Optional filter expression as a string.
                     The expression should refer to columns using 'table.column_name'.

    Example:
        create_view("active_users", "users", "table.is_active == True")
        create_view("adult_users", "users", "table.age >= 18")
    """
    try:
        table = pxt.get_table(table_name)
        if table is None:
            return f"Error: Table {table_name} not found."

        if filter_expr:
            filter_condition = _safe_eval(filter_expr, table)

            # Create the view with the filter
            view = pxt.create_view(view_name, table.where(filter_condition))
        else:
            # Create a view without a filter
            view = pxt.create_view(view_name, table)

        return f"View '{view_name}' created successfully."
    except ValueError as e:
        return f"Error: Invalid filter expression: {e}"
    except Exception as e:
        return f"Error creating view: {str(e)}"


@mcp.tool()
def execute_query(
    table_or_view_name: str,
    select_columns: list[str] = None,
    where_expr: str = None,
    order_by_column: str = None,
    order_asc: bool = True,
    limit: int = None,
) -> str:
    """Execute a query on a table or view in Pixeltable.

    Args:
        table_or_view_name: The name of the table or view to query.
        select_columns: List of column names to select. If None, selects all columns.
        where_expr: Optional filter expression as a string.
                    The expression should refer to columns using 'table.column_name'.
        order_by_column: Optional column name to order the results by.
        order_asc: Whether to order ascending (True) or descending (False).
        limit: Maximum number of rows to return.

    Example:
        execute_query("users", ["name", "email"], "table.age > 25", "name", True, 10)
    """
    try:
        # Get the table or view
        data_source = pxt.get_table(table_or_view_name)
        if data_source is None:
            data_source = pxt.get_view(table_or_view_name)
            if data_source is None:
                return f"Error: Table or view '{table_or_view_name}' not found."

        # Start building the query
        query = data_source

        # Apply where clause if provided
        if where_expr:
            where_condition = _safe_eval(where_expr, data_source)
            query = query.where(where_condition)

        # Apply order by if provided
        if order_by_column:
            if not _IDENTIFIER_RE.match(order_by_column):
                return f"Error: Invalid column name: '{order_by_column}'"
            # Handle ordering on a specific column
            if hasattr(data_source, order_by_column):
                order_col = getattr(data_source, order_by_column)
                query = query.order_by(order_col, asc=order_asc)
            else:
                return f"Error: Column '{order_by_column}' not found in '{table_or_view_name}'."

        # Apply limit if provided
        if limit is not None:
            query = query.limit(limit)

        # Apply select if provided
        if select_columns:
            select_args = []
            for col_name in select_columns:
                if not _IDENTIFIER_RE.match(col_name):
                    return f"Error: Invalid column name: '{col_name}'"
                if hasattr(data_source, col_name):
                    select_args.append(getattr(data_source, col_name))
                else:
                    return f"Error: Column '{col_name}' not found in '{table_or_view_name}'."

            # Execute the query with select
            result = query.select(*select_args).collect()
        else:
            # Execute the query for all columns
            result = query.collect()

        # Convert result to string representation
        result_str = result.to_pandas().to_string()
        return f"Query executed successfully:\n\n{result_str}"

    except ValueError as e:
        return f"Error: Invalid expression: {e}"
    except Exception as e:
        return f"Error executing query: {str(e)}"


@mcp.tool()
def create_query(
    query_name: str,
    table_name: str,
    select_columns: list[str] = None,
    where_expr: str = None,
) -> str:
    """Create a named query as a persistent view in Pixeltable.

    Args:
        query_name: The name of the query to create (stored as a Pixeltable view).
        table_name: The name of the table the query will operate on.
        select_columns: Optional list of column names to select.
                        If None, selects all columns.
        where_expr: Optional filter expression as a string.
                    The expression should refer to columns using 'table.column_name'.

    Example:
        create_query(
            "get_active_users",
            "users",
            select_columns=["name", "email"],
            where_expr="table.is_active == True"
        )
    """
    try:
        table = pxt.get_table(table_name)
        if table is None:
            return f"Error: Table {table_name} not found."

        # Build the query using Pixeltable's API directly instead of exec()
        query = table

        if where_expr:
            filter_condition = _safe_eval(where_expr, table)
            query = query.where(filter_condition)

        if select_columns:
            select_args = []
            for col_name in select_columns:
                if not _IDENTIFIER_RE.match(col_name):
                    return f"Error: Invalid column name: '{col_name}'"
                if hasattr(table, col_name):
                    select_args.append(getattr(table, col_name))
                else:
                    return f"Error: Column '{col_name}' not found in table '{table_name}'."
            query = query.select(*select_args)

        # Persist the query as a Pixeltable view so it can be retrieved later
        pxt.create_view(query_name, query)

        return f"Query '{query_name}' created successfully for table '{table_name}'."
    except ValueError as e:
        return f"Error: Invalid expression: {e}"
    except Exception as e:
        return f"Error creating query: {str(e)}"
