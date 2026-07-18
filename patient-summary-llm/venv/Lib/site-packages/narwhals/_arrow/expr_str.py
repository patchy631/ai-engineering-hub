from __future__ import annotations

from typing import TYPE_CHECKING

from narwhals._arrow.utils import ArrowExprNamespace
from narwhals._expression_parsing import reuse_series_namespace_implementation

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._arrow.expr import ArrowExpr


class ArrowExprStringNamespace(ArrowExprNamespace):
    def len_chars(self: Self) -> ArrowExpr:
        return reuse_series_namespace_implementation(self.compliant, "str", "len_chars")

    def replace(
        self: Self, pattern: str, value: str, *, literal: bool, n: int
    ) -> ArrowExpr:
        return reuse_series_namespace_implementation(
            self.compliant,
            "str",
            "replace",
            pattern=pattern,
            value=value,
            literal=literal,
            n=n,
        )

    def replace_all(self: Self, pattern: str, value: str, *, literal: bool) -> ArrowExpr:
        return reuse_series_namespace_implementation(
            self.compliant,
            "str",
            "replace_all",
            pattern=pattern,
            value=value,
            literal=literal,
        )

    def strip_chars(self: Self, characters: str | None) -> ArrowExpr:
        return reuse_series_namespace_implementation(
            self.compliant, "str", "strip_chars", characters=characters
        )

    def starts_with(self: Self, prefix: str) -> ArrowExpr:
        return reuse_series_namespace_implementation(
            self.compliant, "str", "starts_with", prefix=prefix
        )

    def ends_with(self: Self, suffix: str) -> ArrowExpr:
        return reuse_series_namespace_implementation(
            self.compliant, "str", "ends_with", suffix=suffix
        )

    def contains(self: Self, pattern: str, *, literal: bool) -> ArrowExpr:
        return reuse_series_namespace_implementation(
            self.compliant, "str", "contains", pattern=pattern, literal=literal
        )

    def slice(self: Self, offset: int, length: int | None) -> ArrowExpr:
        return reuse_series_namespace_implementation(
            self.compliant, "str", "slice", offset=offset, length=length
        )

    def split(self: Self, by: str) -> ArrowExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr, "str", "split", by=by
        )

    def to_datetime(self: Self, format: str | None) -> ArrowExpr:  # noqa: A002
        return reuse_series_namespace_implementation(
            self.compliant, "str", "to_datetime", format=format
        )

    def to_uppercase(self: Self) -> ArrowExpr:
        return reuse_series_namespace_implementation(
            self.compliant, "str", "to_uppercase"
        )

    def to_lowercase(self: Self) -> ArrowExpr:
        return reuse_series_namespace_implementation(
            self.compliant, "str", "to_lowercase"
        )
