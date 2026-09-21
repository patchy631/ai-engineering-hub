from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self


class NarwhalsError(ValueError):
    """Base class for all Narwhals exceptions."""


class FormattedKeyError(KeyError):
    """KeyError with formatted error message.

    Python's `KeyError` has special casing around formatting
    (see https://bugs.python.org/issue2651). Use this class when the error
    message has newlines and other special format characters.
    Needed by https://github.com/tensorflow/tensorflow/issues/36857.
    """

    def __init__(self: Self, message: str) -> None:
        self.message = message

    def __str__(self: Self) -> str:
        return self.message


class ColumnNotFoundError(FormattedKeyError, NarwhalsError):
    """Exception raised when column name isn't present."""

    def __init__(self: Self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    @classmethod
    def from_missing_and_available_column_names(
        cls: type, missing_columns: list[str], available_columns: list[str]
    ) -> ColumnNotFoundError:
        message = (
            f"The following columns were not found: {missing_columns}"
            f"\n\nHint: Did you mean one of these columns: {available_columns}?"
        )
        return ColumnNotFoundError(message)


class ComputeError(NarwhalsError):
    """Exception raised when the underlying computation could not be evaluated."""


class ShapeError(NarwhalsError):
    """Exception raised when trying to perform operations on data structures with incompatible shapes."""


class DuplicateError(NarwhalsError):
    """Exception when duplicate column names are encountered."""


class InvalidOperationError(NarwhalsError):
    """Exception raised during invalid operations."""


class InvalidIntoExprError(TypeError, NarwhalsError):
    """Exception raised when object can't be converted to expression."""

    def __init__(self: Self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    @classmethod
    def from_invalid_type(cls: type, invalid_type: type) -> InvalidIntoExprError:
        message = (
            f"Expected an object which can be converted into an expression, got {invalid_type}\n\n"
            "Hint:\n"
            "- if you were trying to select a column which does not have a string\n"
            "  column name, then you should explicitly use `nw.col`.\n"
            "  For example, `df.select(nw.col(0))` if you have a column named `0`.\n"
            "- if you were trying to create a new literal column, then you \n"
            "  should explicitly use `nw.lit`.\n"
            "  For example, `df.select(nw.lit(0))` if you want to create a new\n"
            "  column with literal value `0`."
        )
        return InvalidIntoExprError(message)


class AnonymousExprError(NarwhalsError):  # pragma: no cover
    """Exception raised when trying to perform operations on anonymous expressions."""

    def __init__(self: Self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    @classmethod
    def from_expr_name(cls: type, expr_name: str) -> AnonymousExprError:
        message = (
            f"Anonymous expressions are not supported in `{expr_name}`.\n"
            "Instead of `nw.all()`, try using a named expression, such as "
            "`nw.col('a', 'b')`"
        )
        return AnonymousExprError(message)


class OrderDependentExprError(NarwhalsError):
    """Exception raised when trying to use an order-dependent expressions with LazyFrames."""

    def __init__(self: Self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class LengthChangingExprError(NarwhalsError):
    """Exception raised when trying to use an expression which changes length with LazyFrames."""

    def __init__(self: Self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class UnsupportedDTypeError(NarwhalsError):
    """Exception raised when trying to convert to a DType which is not supported by the given backend."""


class NarwhalsUnstableWarning(UserWarning):
    """Warning issued when a method or function is considered unstable in the stable api."""
