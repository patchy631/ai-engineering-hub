from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Callable
from typing import Sequence

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._pandas_like.expr import PandasLikeExpr


class PandasLikeExprNameNamespace:
    def __init__(self: Self, expr: PandasLikeExpr) -> None:
        self._compliant_expr = expr

    def keep(self: Self) -> PandasLikeExpr:
        return self._from_colname_func_and_alias_output_names(
            name_mapping_func=lambda name: name,
            alias_output_names=None,
        )

    def map(self: Self, function: Callable[[str], str]) -> PandasLikeExpr:
        return self._from_colname_func_and_alias_output_names(
            name_mapping_func=lambda name: function(str(name)),
            alias_output_names=lambda output_names: [
                function(str(name)) for name in output_names
            ],
        )

    def prefix(self: Self, prefix: str) -> PandasLikeExpr:
        return self._from_colname_func_and_alias_output_names(
            name_mapping_func=lambda name: f"{prefix}{name}",
            alias_output_names=lambda output_names: [
                f"{prefix}{output_name}" for output_name in output_names
            ],
        )

    def suffix(self: Self, suffix: str) -> PandasLikeExpr:
        return self._from_colname_func_and_alias_output_names(
            name_mapping_func=lambda name: f"{name}{suffix}",
            alias_output_names=lambda output_names: [
                f"{output_name}{suffix}" for output_name in output_names
            ],
        )

    def to_lowercase(self: Self) -> PandasLikeExpr:
        return self._from_colname_func_and_alias_output_names(
            name_mapping_func=lambda name: str(name).lower(),
            alias_output_names=lambda output_names: [
                str(name).lower() for name in output_names
            ],
        )

    def to_uppercase(self: Self) -> PandasLikeExpr:
        return self._from_colname_func_and_alias_output_names(
            name_mapping_func=lambda name: str(name).upper(),
            alias_output_names=lambda output_names: [
                str(name).upper() for name in output_names
            ],
        )

    def _from_colname_func_and_alias_output_names(
        self: Self,
        name_mapping_func: Callable[[str], str],
        alias_output_names: Callable[[Sequence[str]], Sequence[str]] | None,
    ) -> PandasLikeExpr:
        return self._compliant_expr.__class__(
            call=lambda df: [
                series.alias(name_mapping_func(name))
                for series, name in zip(
                    self._compliant_expr._call(df),
                    self._compliant_expr._evaluate_output_names(df),
                )
            ],
            depth=self._compliant_expr._depth,
            function_name=self._compliant_expr._function_name,
            evaluate_output_names=self._compliant_expr._evaluate_output_names,
            alias_output_names=alias_output_names,
            backend_version=self._compliant_expr._backend_version,
            implementation=self._compliant_expr._implementation,
            version=self._compliant_expr._version,
            call_kwargs=self._compliant_expr._call_kwargs,
        )
