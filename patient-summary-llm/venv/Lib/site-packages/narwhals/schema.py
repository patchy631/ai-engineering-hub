"""Schema.

Adapted from Polars implementation at:
https://github.com/pola-rs/polars/blob/main/py-polars/polars/schema.py.
"""

from __future__ import annotations

from collections import OrderedDict
from functools import partial
from typing import TYPE_CHECKING
from typing import Iterable
from typing import Mapping
from typing import cast

from narwhals.utils import Implementation
from narwhals.utils import Version
from narwhals.utils import parse_version

if TYPE_CHECKING:
    from typing import Any
    from typing import ClassVar

    import polars as pl
    import pyarrow as pa
    from typing_extensions import Self

    from narwhals.dtypes import DType
    from narwhals.typing import DTypeBackend

    BaseSchema = OrderedDict[str, DType]
else:
    # Python 3.8 does not support generic OrderedDict at runtime
    BaseSchema = OrderedDict

__all__ = ["Schema"]


class Schema(BaseSchema):
    """Ordered mapping of column names to their data type.

    Arguments:
        schema: Mapping[str, DType] | Iterable[tuple[str, DType]] | None
            The schema definition given by column names and their associated.
            *instantiated* Narwhals data type. Accepts a mapping or an iterable of tuples.

    Examples:
        Define a schema by passing *instantiated* data types.

        >>> import narwhals as nw
        >>> schema = nw.Schema({"foo": nw.Int8(), "bar": nw.String()})
        >>> schema
        Schema({'foo': Int8, 'bar': String})

        Access the data type associated with a specific column name.

        >>> schema["foo"]
        Int8

        Access various schema properties using the `names`, `dtypes`, and `len` methods.

        >>> schema.names()
        ['foo', 'bar']
        >>> schema.dtypes()
        [Int8, String]
        >>> schema.len()
        2
    """

    _version: ClassVar[Version] = Version.MAIN

    def __init__(
        self: Self,
        schema: Mapping[str, DType] | Iterable[tuple[str, DType]] | None = None,
    ) -> None:
        schema = schema or {}
        super().__init__(schema)

    def names(self: Self) -> list[str]:
        """Get the column names of the schema.

        Returns:
            Column names.
        """
        return list(self.keys())

    def dtypes(self: Self) -> list[DType]:
        """Get the data types of the schema.

        Returns:
            Data types of schema.
        """
        return list(self.values())

    def len(self: Self) -> int:
        """Get the number of columns in the schema.

        Returns:
            Number of columns.
        """
        return len(self)

    def to_arrow(self: Self) -> pa.Schema:
        """Convert Schema to a pyarrow Schema.

        Returns:
            A pyarrow Schema.

        Examples:
            >>> import narwhals as nw
            >>> schema = nw.Schema({"a": nw.Int64(), "b": nw.Datetime("ns")})
            >>> schema.to_arrow()
            a: int64
            b: timestamp[ns]
        """
        import pyarrow as pa  # ignore-banned-import

        from narwhals._arrow.utils import narwhals_to_native_dtype

        return pa.schema(
            (name, narwhals_to_native_dtype(dtype, self._version))
            for name, dtype in self.items()
        )

    def to_pandas(
        self: Self, dtype_backend: DTypeBackend | Iterable[DTypeBackend] = None
    ) -> dict[str, Any]:
        """Convert Schema to an ordered mapping of column names to their pandas data type.

        Arguments:
            dtype_backend: Backend(s) used for the native types. When providing more than
                one, the length of the iterable must be equal to the length of the schema.

        Returns:
            An ordered mapping of column names to their pandas data type.

        Examples:
            >>> import narwhals as nw
            >>> schema = nw.Schema({"a": nw.Int64(), "b": nw.Datetime("ns")})
            >>> schema.to_pandas()
            {'a': 'int64', 'b': 'datetime64[ns]'}

            >>> schema.to_pandas("pyarrow")
            {'a': 'Int64[pyarrow]', 'b': 'timestamp[ns][pyarrow]'}
        """
        import pandas as pd  # ignore-banned-import

        from narwhals._pandas_like.utils import narwhals_to_native_dtype

        to_native_dtype = partial(
            narwhals_to_native_dtype,
            implementation=Implementation.PANDAS,
            backend_version=parse_version(pd),
            version=self._version,
        )
        if dtype_backend is None or isinstance(dtype_backend, str):
            return {
                name: to_native_dtype(dtype=dtype, dtype_backend=dtype_backend)
                for name, dtype in self.items()
            }
        else:
            backends = tuple(dtype_backend)
            if len(backends) != len(self):
                from itertools import chain
                from itertools import islice
                from itertools import repeat

                n_user, n_actual = len(backends), len(self)
                suggestion = tuple(
                    islice(
                        chain.from_iterable(islice(repeat(backends), n_actual)), n_actual
                    )
                )
                msg = (
                    f"Provided {n_user!r} `dtype_backend`(s), but schema contains {n_actual!r} field(s).\n"
                    "Hint: instead of\n"
                    f"    schema.to_pandas({backends})\n"
                    "you may want to use\n"
                    f"    schema.to_pandas({backends[0]})\n"
                    f"or\n"
                    f"    schema.to_pandas({suggestion})"
                )
                raise ValueError(msg)
            return {
                name: to_native_dtype(dtype=dtype, dtype_backend=backend)
                for name, dtype, backend in zip(self.keys(), self.values(), backends)
            }

    def to_polars(self: Self) -> pl.Schema:
        """Convert Schema to a polars Schema.

        Returns:
            A polars Schema or plain dict (prior to polars 1.0).

        Examples:
            >>> import narwhals as nw
            >>> schema = nw.Schema({"a": nw.Int64(), "b": nw.Datetime("ns")})
            >>> schema.to_polars()
            Schema({'a': Int64, 'b': Datetime(time_unit='ns', time_zone=None)})
        """
        import polars as pl  # ignore-banned-import

        from narwhals._polars.utils import narwhals_to_native_dtype

        pl_version = parse_version(pl)
        schema = (
            (
                name,
                narwhals_to_native_dtype(
                    dtype, self._version, backend_version=pl_version
                ),
            )
            for name, dtype in self.items()
        )
        return (
            pl.Schema(schema)
            if pl_version >= (1, 0, 0)
            else cast("pl.Schema", dict(schema))
        )
