import pixeltable as pxt
from mcp.server.fastmcp import FastMCP
from safe_expr import build_query, parse_column_name, parse_expression

mcp = FastMCP("Pixeltable")

# Named queries live in memory: pxt.query does not persist them
_named_queries = {}


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
        expression: An allowlisted expression (see safe_expr.py) to compute the column.
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

        # Construct the expression
        column_expr = parse_expression(expression, table)

        # Add the computed column with kwargs format
        kwargs = {column_name: column_expr}
        table.add_computed_column(**kwargs)

        return f"Computed column '{column_name}' added successfully to table '{table_name}'."
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
            # Convert the string expression to a Pixeltable expression
            filter_condition = parse_expression(filter_expr, table)

            # Create the view with the filter
            view = pxt.create_view(view_name, table.where(filter_condition))
        else:
            # Create a view without a filter
            view = pxt.create_view(view_name, table)

        return f"View '{view_name}' created successfully."
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
            where_condition = parse_expression(where_expr, data_source)
            query = query.where(where_condition)

        # Apply order by if provided
        if order_by_column:
            # Handle ordering on a specific column
            order_col = parse_column_name(order_by_column, data_source)
            query = query.order_by(order_col, asc=order_asc)

        # Apply limit if provided
        if limit is not None:
            query = query.limit(limit)

        # Apply select if provided
        if select_columns:
            select_args = [parse_column_name(col_name, data_source) for col_name in select_columns]

            # Execute the query with select
            result = query.select(*select_args).collect()
        else:
            # Execute the query for all columns
            result = query.collect()

        # Convert result to string representation
        result_str = result.to_pandas().to_string()
        return f"Query executed successfully:\n\n{result_str}"

    except Exception as e:
        return f"Error executing query: {str(e)}"


@mcp.tool()
def create_query(query_name: str, table_name: str, query_function: str) -> str:
    """Create a named query in Pixeltable.

    Args:
        query_name: The name of the query to create.
        table_name: The name of the table the query will operate on.
        query_function: A restricted query, not arbitrary Python: an optional 'return '
                       followed by a method chain on 'table' (or the table name) using
                       only .where(), .select(), .order_by(col, asc=True) and .limit(n).
                       Arguments follow the same rules as other tool expressions.
                       Queries take no parameters and are kept in memory only, so they
                       are lost when the server restarts. No tool runs saved queries
                       yet: they are only registered.

    Example:
        create_query(
            "get_active_users",
            "users",
            "return table.where(table.is_active == True).select(table.name, table.email)"
        )
    """
    try:
        table = pxt.get_table(table_name)
        if table is None:
            return f"Error: Table {table_name} not found."

        if not query_name.isidentifier():
            return f"Error creating query: invalid query name '{query_name}'."

        # Build the query from the restricted method chain
        query = build_query(query_function, table)

        # Register it as a named Pixeltable query
        def named_query():
            return query

        named_query.__name__ = query_name
        _named_queries[query_name] = pxt.query(named_query)

        return f"Query '{query_name}' created successfully for table '{table_name}'."
    except Exception as e:
        return f"Error creating query: {str(e)}"
