"""Safe parsing of model-supplied Pixeltable expressions.

Tool arguments come from an LLM, so they can carry prompt-injected code. Strings
are parsed with `ast` and the tree is walked against an allowlist; the result is
built directly from the objects. Nothing is ever compiled or run as Python.

Allowed in an expression:
    - Literals: int, float, str, bool, None, and lists/tuples of allowed elements
    - Columns: `table.<column>` (or `<table name>.<column>`), never `_private` names
    - Comparisons: == != < <= > >= (chained comparisons are rejected)
    - Arithmetic: + - * / // %  (strings and lists support + only)
    - Logic on columns: & | ~ and unary - +
    - Calls to bare allowlisted functions, with positional arguments only:
        string:    lower upper strip len contains startswith endswith capitalize
        math:      abs round floor ceil
        timestamp: year month day

Everything else raises UnsafeExpressionError: subscripts, lambdas, comprehensions,
`and`/`or`/`not`, conditionals, f-strings, walrus, any other attribute, name or call.

`build_query` adds a small chain DSL on top, see its docstring.
"""

import ast
import functools
import importlib
import inspect
import keyword
import operator
import re

MAX_EXPRESSION_LENGTH = 2000

_FUNCTION_ALLOWLIST = {
    "string": ("lower", "upper", "strip", "len", "contains", "startswith", "endswith", "capitalize"),
    "math": ("abs", "round", "floor", "ceil"),
    "timestamp": ("year", "month", "day"),
}

_COMPARE_OPS = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}

_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.BitAnd: operator.and_,
    ast.BitOr: operator.or_,
}

_UNARY_OPS = {ast.USub: operator.neg, ast.UAdd: operator.pos, ast.Invert: operator.invert}

# Query method -> exact number of positional arguments (None means one or more).
_QUERY_METHODS = {"where": 1, "select": None, "order_by": None, "limit": 1}

_RETURN_PREFIX = re.compile(r"\s*return\s+")


class UnsafeExpressionError(ValueError):
    """Raised when an expression is invalid or uses a construct outside the allowlist."""


def _load_default_functions() -> dict:
    try:
        return {
            name: getattr(importlib.import_module(f"pixeltable.functions.{module}"), name)
            for module, names in _FUNCTION_ALLOWLIST.items()
            for name in names
        }
    except ImportError:
        return {}  # Without pixeltable no function calls are allowed, unless injected


DEFAULT_FUNCTIONS = _load_default_functions()


def _reject_deep_nesting(func):
    """Report parser and evaluator stack exhaustion as a rejected expression."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (RecursionError, MemoryError) as e:
            raise UnsafeExpressionError("Expression is too deeply nested") from e

    return wrapper


def _parse(source: str) -> ast.Expression:
    if not isinstance(source, str):
        raise UnsafeExpressionError("Expression must be a string")
    if len(source) > MAX_EXPRESSION_LENGTH:
        raise UnsafeExpressionError(f"Expression is longer than {MAX_EXPRESSION_LENGTH} characters")
    try:
        return ast.parse(source.strip(), mode="eval")
    except (SyntaxError, ValueError) as e:
        raise UnsafeExpressionError(f"Invalid expression syntax: {e}") from e


def _table_alias(table, functions: dict) -> str | None:
    """Return the table's own name if it can safely be used in place of `table`."""
    name = getattr(table, "_name", None)
    if callable(name):  # Current pixeltable exposes _name() as a method
        name = name()
    if not isinstance(name, str):
        name = getattr(table, "name", None)
    if (
        isinstance(name, str)
        and name.isidentifier()
        and not keyword.iskeyword(name)
        and name not in functions
    ):
        return name
    return None


def parse_column_name(name: str, table):
    """Resolve a plain column name on the table, rejecting private names and methods."""
    if not isinstance(name, str) or not name.isidentifier() or name.startswith("_"):
        raise UnsafeExpressionError(f"Invalid column name: {name!r}")
    try:
        column = getattr(table, name)
    except AttributeError:
        raise UnsafeExpressionError(f"Column '{name}' not found") from None
    if inspect.isroutine(column):  # e.g. table.delete is a method, not a column
        raise UnsafeExpressionError(f"'{name}' is a table method, not a column")
    return column


class _Evaluator(ast.NodeVisitor):
    """Builds the result of an expression, allowing only the node types defined below."""

    def __init__(self, table, functions: dict | None = None):
        self.table = table
        self.functions = DEFAULT_FUNCTIONS if functions is None else functions
        self.table_names = {"table", _table_alias(table, self.functions)}

    def generic_visit(self, node):
        raise UnsafeExpressionError(f"Disallowed construct: {type(node).__name__}")

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        if node.value is None or type(node.value) in (int, float, str, bool):
            return node.value
        raise UnsafeExpressionError(f"Disallowed literal: {node.value!r}")

    def visit_List(self, node):
        return [self.visit(element) for element in node.elts]

    def visit_Tuple(self, node):
        return tuple(self.visit(element) for element in node.elts)

    def visit_Name(self, node):
        if node.id in self.table_names:
            return self.table
        if node.id in self.functions:
            return self.functions[node.id]
        raise UnsafeExpressionError(f"Disallowed name: '{node.id}'")

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id in self.table_names:
            return parse_column_name(node.attr, self.table)
        raise UnsafeExpressionError(
            f"Disallowed attribute access: '{ast.unparse(node)}' (only table.<column> is allowed)"
        )

    def visit_Compare(self, node):
        if len(node.ops) > 1:
            raise UnsafeExpressionError(
                "Chained comparisons are not supported, use (a < b) & (b < c)"
            )
        compare = _COMPARE_OPS.get(type(node.ops[0]))
        if compare is None:
            raise UnsafeExpressionError(f"Disallowed operator: {type(node.ops[0]).__name__}")
        return compare(self.visit(node.left), self.visit(node.comparators[0]))

    def visit_BinOp(self, node):
        binary_op = _BINARY_OPS.get(type(node.op))
        if binary_op is None:
            raise UnsafeExpressionError(f"Disallowed operator: {type(node.op).__name__}")
        left, right = self.visit(node.left), self.visit(node.right)
        # 'x' * 10**12 and '%999999999d' % 1 would allocate memory while parsing
        if not isinstance(node.op, ast.Add) and (
            isinstance(left, (str, list, tuple)) or isinstance(right, (str, list, tuple))
        ):
            raise UnsafeExpressionError("Strings and lists only support the + operator")
        return binary_op(left, right)

    def visit_UnaryOp(self, node):
        if isinstance(node.op, ast.Not):
            raise UnsafeExpressionError("Disallowed construct: 'not' (use ~ instead)")
        return _UNARY_OPS[type(node.op)](self.visit(node.operand))

    def visit_BoolOp(self, node):
        raise UnsafeExpressionError("Disallowed construct: 'and'/'or' (use & and | instead)")

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name) or node.func.id not in self.functions:
            raise UnsafeExpressionError(f"Disallowed function call: '{ast.unparse(node.func)}'")
        if node.keywords:
            raise UnsafeExpressionError(
                f"Keyword arguments are not supported in call to '{node.func.id}'"
            )
        return self.functions[node.func.id](*[self.visit(arg) for arg in node.args])


@_reject_deep_nesting
def parse_expression(expr: str, table, functions: dict | None = None):
    """Evaluate an allowlisted expression against `table`.

    Args:
        expr: The expression, e.g. "lower(table.name) == 'bob'".
        table: The object `table.<column>` resolves on.
        functions: Callable names to allow, defaults to DEFAULT_FUNCTIONS.

    Raises:
        UnsafeExpressionError: If the expression is invalid or not allowlisted.
    """
    return _Evaluator(table, functions).visit(_parse(expr))


def _query_call_args(method: str, call: ast.Call, evaluator: _Evaluator) -> tuple[list, dict]:
    """Validate the arguments of one chained call, returning (args, kwargs)."""
    args = [evaluator.visit(arg) for arg in call.args]
    expected = _QUERY_METHODS[method]
    if not args or (expected is not None and len(args) != expected):
        raise UnsafeExpressionError(f"Wrong number of arguments for {method}()")
    if method == "limit" and (type(args[0]) is not int or args[0] < 0):
        raise UnsafeExpressionError("limit() requires a non-negative integer")

    kwargs = {}
    for keyword_arg in call.keywords:
        value = keyword_arg.value
        if (
            method != "order_by"
            or keyword_arg.arg != "asc"
            or not isinstance(value, ast.Constant)
            or type(value.value) is not bool
        ):
            raise UnsafeExpressionError(
                f"Disallowed keyword argument in {method}(): '{keyword_arg.arg}'"
            )
        kwargs["asc"] = value.value
    return args, kwargs


@_reject_deep_nesting
def build_query(body: str, table, functions: dict | None = None):
    """Build a query from a restricted method chain rooted at `table`.

    The body is an optional `return ` followed by any of these, in any order:
        .where(<expr>)  .select(<expr>, ...)  .order_by(<expr>, ..., asc=<bool>)  .limit(<int>)

    Arguments follow the same rules as parse_expression. Pixeltable itself rejects
    repeating .where() or .select(). This is not a general Python function body:
    statements, parameters and any other method raise UnsafeExpressionError.
    """
    node = _parse(_RETURN_PREFIX.sub("", body, count=1)).body
    evaluator = _Evaluator(table, functions)

    calls = []
    while isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        method = node.func.attr
        if method not in _QUERY_METHODS:
            raise UnsafeExpressionError(f"Disallowed query method: '{method}'")
        calls.append((method, node))
        node = node.func.value

    if not (calls and isinstance(node, ast.Name) and node.id in evaluator.table_names):
        raise UnsafeExpressionError(
            "Query must be a chain of where/select/order_by/limit calls on table"
        )

    query = table
    for method, call in reversed(calls):
        args, kwargs = _query_call_args(method, call, evaluator)
        query = getattr(query, method)(*args, **kwargs)
    return query
