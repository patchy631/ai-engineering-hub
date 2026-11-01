import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

from safe_expr import (
    DEFAULT_FUNCTIONS,
    MAX_EXPRESSION_LENGTH,
    UnsafeExpressionError,
    build_query,
    parse_column_name,
    parse_expression,
)

BASE_SDK = Path(__file__).resolve().parent.parent


class FakeExpr:
    """Records operators as text, the way a Pixeltable Expr builds an expression tree."""

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text

    def __hash__(self):
        return hash(self.text)

    def __bool__(self):
        raise TypeError("Expressions have no truth value")

    def __neg__(self):
        return FakeExpr(f"-{self}")

    def __pos__(self):
        return FakeExpr(f"+{self}")

    def __invert__(self):
        return FakeExpr(f"~{self}")


def _add_operator(name, symbol):
    setattr(FakeExpr, f"__{name}__", lambda self, other: FakeExpr(f"({self!r} {symbol} {other!r})"))
    setattr(FakeExpr, f"__r{name}__", lambda self, other: FakeExpr(f"({other!r} {symbol} {self!r})"))


for _name, _symbol in {
    "add": "+",
    "sub": "-",
    "mul": "*",
    "truediv": "/",
    "floordiv": "//",
    "mod": "%",
    "and": "&",
    "or": "|",
}.items():
    _add_operator(_name, _symbol)

for _name, _symbol in {"eq": "==", "ne": "!=", "lt": "<", "le": "<=", "gt": ">", "ge": ">="}.items():
    setattr(
        FakeExpr,
        f"__{_name}__",
        lambda self, other, symbol=_symbol: FakeExpr(f"({self!r} {symbol} {other!r})"),
    )


class FakeQuery:
    def __init__(self, table, calls=()):
        self.table = table
        self.calls = list(calls)

    def _record(self, name, *args, **kwargs):
        return FakeQuery(self.table, [*self.calls, (name, args, kwargs)])

    def where(self, *args, **kwargs):
        return self._record("where", *args, **kwargs)

    def select(self, *args, **kwargs):
        return self._record("select", *args, **kwargs)

    def order_by(self, *args, **kwargs):
        return self._record("order_by", *args, **kwargs)

    def limit(self, *args, **kwargs):
        return self._record("limit", *args, **kwargs)


class FakeTable(FakeQuery):
    def __init__(self, name="users", columns=("a", "b", "name")):
        super().__init__(self)
        self._name = name
        self._columns = columns
        self.computed = {}
        self.destroyed = False

    def __getattr__(self, name):
        if name in self.__dict__["_columns"]:
            return FakeExpr(f"col.{name}")
        raise AttributeError(f"Unknown column: {name}")

    def delete(self):
        self.destroyed = True

    def drop(self):
        self.destroyed = True

    def add_computed_column(self, **kwargs):
        self.computed.update(kwargs)


class MethodNameTable(FakeTable):
    """Pixeltable 0.7 exposes the table name through a _name() method."""

    def __init__(self):
        super().__init__()
        self.__dict__["_table_name"] = self.__dict__.pop("_name")

    def _name(self):
        return self._table_name


FUNCTIONS = {
    "lower": lambda value: FakeExpr(f"lower({value!r})"),
    "contains": lambda value, substr: FakeExpr(f"contains({value!r}, {substr!r})"),
}


def parse(expr, table=None):
    return parse_expression(expr, table or FakeTable(), FUNCTIONS)


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("table.a", "col.a"),
        ("table.a + 1", "(col.a + 1)"),
        ("1 + table.a", "(1 + col.a)"),
        ("table.a - table.b * 2", "(col.a - (col.b * 2))"),
        ("table.a / 2 // 3 % 4", "(((col.a / 2) // 3) % 4)"),
        ("table.name + ' ' + table.name", "((col.name + ' ') + col.name)"),
        ("table.a == True", "(col.a == True)"),
        ("table.a != None", "(col.a != None)"),
        ("table.a < 1", "(col.a < 1)"),
        ("table.a <= 1.5", "(col.a <= 1.5)"),
        ("table.a > 1", "(col.a > 1)"),
        ("table.a >= 1", "(col.a >= 1)"),
        ("(table.a > 1) & (table.b < 2)", "((col.a > 1) & (col.b < 2))"),
        ("(table.a > 1) | (table.b < 2)", "((col.a > 1) | (col.b < 2))"),
        ("~(table.a > 1)", "~(col.a > 1)"),
        ("-table.a", "-col.a"),
        ("+table.a", "+col.a"),
        ("lower(table.name)", "lower(col.name)"),
        ("lower(table.name) == 'bob'", "(lower(col.name) == 'bob')"),
        ("contains(lower(table.name), 'b')", "contains(lower(col.name), 'b')"),
        ("users.a + 1", "(col.a + 1)"),
    ],
)
def test_valid_expressions(expr, expected):
    assert repr(parse(expr)) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("1", 1),
        ("1.5", 1.5),
        ("'x'", "x"),
        ("True", True),
        ("False", False),
        ("None", None),
        ("-1", -1),
        ("[1, 'x', None]", [1, "x", None]),
        ("(1, 2)", (1, 2)),
        ("'a' + 'b'", "ab"),
    ],
)
def test_literals(expr, expected):
    assert parse(expr) == expected


def test_table_alias_with_name_method():
    assert repr(parse("users.a + 1", MethodNameTable())) == "(col.a + 1)"


@pytest.mark.parametrize("name", ["not-an-identifier", "my table", "class", "lower", 7, None])
def test_table_alias_only_for_safe_names(name):
    table = FakeTable(name=name)
    with pytest.raises(UnsafeExpressionError):
        parse(f"{name}.a", table)
    assert repr(parse("table.a", table)) == "col.a"


@pytest.mark.parametrize(
    "expr",
    [
        "__import__('os').system('id')",
        "().__class__.__bases__[0].__subclasses__()",
        "open('/etc/passwd').read()",
        "lambda: 1",
        "table.__class__",
        "table.__dict__",
        "table._private",
        "table._name",
        "table.delete",
        "table.where",
        "table.missing",
        "[x for x in table.a]",
        "{x for x in table.a}",
        "{x: 1 for x in table.a}",
        "(x for x in table.a)",
        "table.a[0]",
        "table.a and table.b",
        "table.a or table.b",
        "not table.a",
        "unknown_name",
        "os.system('id')",
        "f'{table.a}'",
        "table.a.foo",
        "table.a.__class__",
        "lower(table.a).__class__",
        "(y := table.a)",
        "table.a if table.b else 1",
        "lower(*[table.a])",
        "lower(**{'value': table.a})",
        "lower(value=table.a)",
        "table.where(table.a > 1)",
        "(lambda: 1)()",
        "lower.__globals__",
        "1 < table.a < 3",
        "table.a in [1, 2]",
        "table.a is None",
        "table.a ** 2",
        "table.a ^ 1",
        "table.a << 1",
        "b'bytes'",
        "1j",
        "...",
        "{'a': 1}",
        "{1, 2}",
        "'x' * 99999999999",
        "[0] * 99999999999",
        "99999999999 * 'x'",
        "'%999999999d' % 1",
        "'%999999999s' % table.a",
        "await table.a",
        "1 +",
        "table.a = 1",
        "import os",
        "1; 2",
        "",
        "x" * (MAX_EXPRESSION_LENGTH + 1),
        "-" * 1900 + "1",
        "(" * 1000 + "1" + ")" * 500,
        "1" + "+1" * 950,
        "\x00",
        "__import__" + "." + "a" * 1000,
    ],
)
def test_rejected_expressions(expr):
    table = FakeTable()
    with pytest.raises(UnsafeExpressionError):
        parse(expr, table)
    assert not table.destroyed


@pytest.mark.parametrize(
    "name", ["eval", "exec", "compile", "open", "getattr", "__import__", "globals", "breakpoint"]
)
def test_rejected_builtin_calls(name):
    with pytest.raises(UnsafeExpressionError, match=name):
        parse(f"{name}('1')")
    with pytest.raises(UnsafeExpressionError, match=name):
        parse(f"{name}(table, 'a')")


@pytest.mark.parametrize(
    "expr, message",
    [
        ("table.a and table.b", "use & and |"),
        ("not table.a", r"use ~"),
        ("lambda: 1", "Lambda"),
        ("table.a[0]", "Subscript"),
        ("f'{table.a}'", "JoinedStr"),
        ("(y := table.a)", "NamedExpr"),
        ("1 < table.a < 3", "Chained comparisons"),
        ("table.missing", "Column 'missing' not found"),
        ("table.delete", "table method"),
        ("table.__class__", "Invalid column name"),
        ("table.a.foo", "table.a.foo"),
        ("unknown_name", "unknown_name"),
        ("x" * (MAX_EXPRESSION_LENGTH + 1), "longer than 2000"),
        ("1 +", "Invalid expression syntax"),
        ("-" * 1900 + "1", "deeply nested"),
    ],
)
def test_error_messages_name_the_problem(expr, message):
    with pytest.raises(UnsafeExpressionError, match=message):
        parse(expr)


def test_non_string_expression_is_rejected():
    with pytest.raises(UnsafeExpressionError):
        parse(123)


def test_unsafe_error_is_a_value_error():
    assert issubclass(UnsafeExpressionError, ValueError)


def test_empty_function_allowlist_rejects_calls():
    with pytest.raises(UnsafeExpressionError):
        parse_expression("lower(table.a)", FakeTable(), {})


def test_module_imports_without_pixeltable():
    code = (
        "import sys; sys.modules['pixeltable'] = None\n"
        "import safe_expr\n"
        "assert safe_expr.DEFAULT_FUNCTIONS == {}\n"
    )
    subprocess.run([sys.executable, "-c", code], cwd=BASE_SDK, check=True)


def test_parse_column_name():
    table = FakeTable()
    assert repr(parse_column_name("a", table)) == "col.a"
    for name in ["__class__", "_private", "delete", "missing", "a.b", "a b", "", None]:
        with pytest.raises(UnsafeExpressionError):
            parse_column_name(name, table)


def build(body, table=None):
    return build_query(body, table or FakeTable(), FUNCTIONS)


def test_build_query_full_chain():
    query = build(
        "return table.where(table.a > 1).select(table.a, lower(table.name))"
        ".order_by(table.a, asc=False).limit(10)"
    )
    assert [(name, repr(args), kwargs) for name, args, kwargs in query.calls] == [
        ("where", "((col.a > 1),)", {}),
        ("select", "(col.a, lower(col.name))", {}),
        ("order_by", "(col.a,)", {"asc": False}),
        ("limit", "(10,)", {}),
    ]


@pytest.mark.parametrize(
    "body, methods",
    [
        ("table.limit(1)", ["limit"]),
        ("table.limit(1).where(table.a > 1)", ["limit", "where"]),
        ("table.select(table.a).order_by(table.a)", ["select", "order_by"]),
        ("  return   table.select(table.a)  ", ["select"]),
        ("users.where(users.a == True).select(users.name)", ["where", "select"]),
    ],
)
def test_build_query_valid_chains(body, methods):
    assert [call[0] for call in build(body).calls] == methods


def test_build_query_alias_with_name_method():
    assert [call[0] for call in build("users.limit(1)", MethodNameTable()).calls] == ["limit"]


@pytest.mark.parametrize(
    "body",
    [
        "table",
        "return table",
        "table.a",
        "table.where(table.a > 1).__class__",
        "table.where(table.a > 1).__class__()",
        "table.where(table.a > 1).__class__.__init__",
        "table.delete()",
        "table.drop()",
        "table.where(table.a > 1).delete()",
        "table.limit(1).collect()",
        "table.select(table.a).insert([])",
        "os.system('id')",
        "return __import__('os')",
        "return __import__('os').system('id')",
        "lower(table.a).where(table.a > 1)",
        "other.where(other.a > 1)",
        "table.a.where(table.a > 1)",
        "(lambda: table)().where(table.a > 1)",
        "table.where(__import__('os'))",
        "table.where(table.a > 1 and table.b)",
        "table.where(table.where(table.a > 1))",
        "table.where(table.delete())",
        "table.where()",
        "table.where(table.a, table.b)",
        "table.where(pred=table.a)",
        "table.select()",
        "table.select(alias=table.a)",
        "table.select(*[table.a])",
        "table.select(**{'x': table.a})",
        "table.order_by()",
        "table.order_by(table.a, asc=1)",
        "table.order_by(table.a, asc=__import__('os'))",
        "table.order_by(table.a, desc=True)",
        "table.limit()",
        "table.limit(1, 2)",
        "table.limit('1')",
        "table.limit(True)",
        "table.limit(-1)",
        "table.limit(table.a)",
        "table.limit(1, offset=1)",
        "x = table.limit(1)\nreturn x",
        "import os; return table.limit(1)",
        "return",
        "return return table",
        "",
        "table.limit(1)" + ".limit(1)" * 500,
    ],
)
def test_build_query_rejects(body):
    table = FakeTable()
    with pytest.raises(UnsafeExpressionError):
        build(body, table)
    assert not table.destroyed


@pytest.mark.parametrize(
    "body",
    [
        "table.order_by(table.a, asc=True, asc=False)",
        "table.order_by(table.a, asc=True, asc=True)",
    ],
)
def test_build_query_rejects_duplicate_keywords(body):
    with pytest.raises(UnsafeExpressionError, match="Duplicate keyword argument"):
        build(body)


@pytest.mark.parametrize("prefix", ["", "return ", "  return\n  "])
def test_build_query_keeps_return_inside_literals(prefix):
    table = FakeTable(columns=("msg",))
    query = build(f"{prefix}table.where(table.msg == 'please return it')", table)
    assert repr(query.calls) == "[('where', ((col.msg == 'please return it'),), {})]"


def test_build_query_rejects_bad_method_before_building():
    table = FakeTable()
    with pytest.raises(UnsafeExpressionError, match="delete"):
        build("table.limit(1).delete()", table)


@pytest.fixture
def tools():
    return pytest.importorskip("tools", exc_type=ImportError)


@pytest.fixture
def fake_table(tools, monkeypatch):
    table = FakeTable()
    monkeypatch.setattr(tools.pxt, "get_table", lambda name: table)
    return table


def payloads(marker):
    """Expressions that would create `marker` if they were ever run as Python."""
    command = f"__import__('os').system('touch {marker}')"
    return [command, f"table.a + {command}", f"lambda: {command}", f"[{command} for _ in [1]]"]


def test_tools_reject_payloads(tools, fake_table, tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("A rejected expression must not reach pixeltable")

    monkeypatch.setattr(tools.pxt, "create_view", fail)
    monkeypatch.setattr(tools.pxt, "query", fail)
    marker = tmp_path / "pwned"

    for payload in payloads(marker):
        assert tools.add_computed_column("t", "c", payload).startswith(
            "Error adding computed column: "
        )
        assert tools.create_view("v", "t", payload).startswith("Error creating view: ")
        assert tools.execute_query("t", where_expr=payload).startswith("Error executing query: ")
        assert tools.create_query("q", "t", payload).startswith("Error creating query: ")
        assert tools.create_query("q", "t", f"return {payload}").startswith("Error creating query: ")

    assert not marker.exists()
    assert fake_table.computed == {}
    assert tools._named_queries == {}


def test_create_query_cannot_inject_statements_through_the_name(tools, fake_table, tmp_path):
    marker = tmp_path / "pwned"
    name = f"q(): pass\n__import__('os').system('touch {marker}')\ndef r"
    result = tools.create_query(name, "t", "table.limit(1)")
    assert result.startswith("Error creating query: ")
    assert not marker.exists()


def test_execute_query_rejects_non_column_names(tools, fake_table):
    for name in ["__class__", "delete"]:
        assert tools.execute_query("t", order_by_column=name).startswith("Error executing query: ")
        assert tools.execute_query("t", select_columns=[name]).startswith("Error executing query: ")


def test_add_computed_column_with_fake(tools, fake_table):
    result = tools.add_computed_column("t", "c", "table.a + table.b")
    assert "added successfully" in result
    assert repr(fake_table.computed["c"]) == "(col.a + col.b)"


def test_create_query_registers_with_fake(tools, fake_table, monkeypatch):
    monkeypatch.setattr(tools.pxt, "query", lambda fn: fn)
    monkeypatch.setattr(tools, "_named_queries", {})
    result = tools.create_query("first_rows", "t", "return table.limit(5)")
    assert "created successfully" in result
    assert tools._named_queries["first_rows"]().calls == [("limit", (5,), {})]


def test_default_functions_are_allowlisted():
    pytest.importorskip("pixeltable")
    assert set(DEFAULT_FUNCTIONS) == {
        "lower", "upper", "strip", "len", "contains", "startswith", "endswith", "capitalize",
        "abs", "round", "floor", "ceil", "year", "month", "day",
    }  # fmt: skip


@pytest.fixture(scope="module")
def real_table():
    pxt = pytest.importorskip("pixeltable")
    try:
        table = pxt.create_table(
            "safe_expr_test",
            {"age": pxt.Int, "name": pxt.String, "score": pxt.Float, "joined": pxt.Timestamp},
            if_exists="replace",
        )
        table.insert(
            [
                {"age": 17, "name": "Ann", "score": -1.5, "joined": datetime(2023, 1, 2)},
                {"age": 30, "name": "Bob", "score": 2.5, "joined": datetime(2024, 3, 4)},
                {"age": 45, "name": "Cid", "score": 4.5, "joined": datetime(2024, 5, 6)},
            ]
        )
    except Exception as e:
        pytest.skip(f"Could not initialize pixeltable: {e}")
    return table


@pytest.mark.parametrize(
    "expr, count",
    [
        ("table.age >= 18", 2),
        ("safe_expr_test.age >= 18", 2),
        ("(table.age > 18) & (table.age < 40)", 1),
        ("(table.age < 18) | (table.age > 40)", 2),
        ("~(table.age < 18)", 2),
        ("lower(table.name) == 'bob'", 1),
        ("contains(table.name, 'i')", 1),
        ("len(table.name) == 3", 3),
        ("abs(table.score) > 2", 2),
        ("year(table.joined) == 2024", 2),
    ],
)
def test_real_where(real_table, expr, count):
    pxt = pytest.importorskip("pixeltable")
    condition = parse_expression(expr, real_table)
    assert isinstance(condition, pxt.exprs.Expr)
    assert len(real_table.where(condition).collect()) == count


def test_real_tables_reject_methods(real_table):
    for expr in ["table.delete", "table.insert", "table.columns", "table.__class__"]:
        with pytest.raises(UnsafeExpressionError):
            parse_expression(expr, real_table)
    with pytest.raises(UnsafeExpressionError):
        build_query("table.delete()", real_table)
    assert real_table.count() == 3


def test_real_build_query(real_table):
    query = build_query(
        "return table.where(table.age > 18).select(table.name)"
        ".order_by(table.age, asc=False).limit(1)",
        real_table,
    )
    assert list(query.collect().to_pandas()["name"]) == ["Cid"]


@pytest.fixture(scope="module")
def real_messages():
    pxt = pytest.importorskip("pixeltable")
    try:
        table = pxt.create_table("safe_expr_messages", {"msg": pxt.String}, if_exists="replace")
        table.insert([{"msg": "please return it"}, {"msg": "pleaseit"}, {"msg": "keep it"}])
    except Exception as e:
        pytest.skip(f"Could not initialize pixeltable: {e}")
    return table


def test_real_build_query_keeps_return_inside_literals(real_messages):
    query = build_query("table.where(table.msg == 'please return it')", real_messages)
    assert list(query.collect().to_pandas()["msg"]) == ["please return it"]


def test_real_tools(tools, real_table):
    assert "added successfully" in tools.add_computed_column(
        "safe_expr_test", "label", "upper(table.name) + ' ' + 'x'"
    )
    assert real_table.select(real_table.label).order_by(real_table.age).limit(1).collect()[0] == {
        "label": "ANN x"
    }

    assert "created successfully" in tools.create_view(
        "safe_expr_adults", "safe_expr_test", "table.age >= 18"
    )
    result = tools.execute_query(
        "safe_expr_adults", ["name"], "table.age > 30", order_by_column="name", limit=5
    )
    assert result.startswith("Query executed successfully") and "Cid" in result

    assert "created successfully" in tools.create_query(
        "real_adults", "safe_expr_test", "return table.where(table.age >= 18).select(table.name)"
    )
    query = tools._named_queries.pop("real_adults")
    assert query.name == "real_adults"
    assert len(real_table.select(query()).limit(1).collect()) == 1
