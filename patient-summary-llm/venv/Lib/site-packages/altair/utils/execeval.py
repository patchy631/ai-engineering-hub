from __future__ import annotations

import ast
import sys
from typing import TYPE_CHECKING, Any, Callable, Literal, overload

if TYPE_CHECKING:
    from os import PathLike

    from _typeshed import ReadableBuffer

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self


class _CatchDisplay:
    """Class to temporarily catch sys.displayhook."""

    def __init__(self) -> None:
        self.output: Any | None = None

    def __enter__(self) -> Self:
        self.old_hook: Callable[[object], Any] = sys.displayhook
        sys.displayhook = self
        return self

    def __exit__(self, type, value, traceback) -> Literal[False]:
        sys.displayhook = self.old_hook
        # Returning False will cause exceptions to propagate
        return False

    def __call__(self, output: Any) -> None:
        self.output = output


@overload
def eval_block(
    code: str | Any,
    namespace: dict[str, Any] | None = ...,
    filename: str | ReadableBuffer | PathLike[Any] = ...,
    *,
    strict: Literal[False] = ...,
) -> Any | None: ...
@overload
def eval_block(
    code: str | Any,
    namespace: dict[str, Any] | None = ...,
    filename: str | ReadableBuffer | PathLike[Any] = ...,
    *,
    strict: Literal[True] = ...,
) -> Any: ...
def eval_block(
    code: str | Any,
    namespace: dict[str, Any] | None = None,
    filename: str | ReadableBuffer | PathLike[Any] = "<string>",
    *,
    strict: bool = False,
) -> Any | None:
    """
    Execute a multi-line block of code in the given namespace.

    If the final statement in the code is an expression, return
    the result of the expression.

    If ``strict``, raise a ``TypeError`` when the return value would be ``None``.
    """
    tree = ast.parse(code, filename="<ast>", mode="exec")
    if namespace is None:
        namespace = {}
    catch_display = _CatchDisplay()

    if isinstance(tree.body[-1], ast.Expr):
        to_exec, to_eval = tree.body[:-1], tree.body[-1:]
    else:
        to_exec, to_eval = tree.body, []

    for node in to_exec:
        compiled = compile(ast.Module([node], []), filename=filename, mode="exec")
        exec(compiled, namespace)

    with catch_display:
        for node in to_eval:
            compiled = compile(
                ast.Interactive([node]), filename=filename, mode="single"
            )
            exec(compiled, namespace)

    if strict:
        output = catch_display.output
        if output is None:
            msg = f"Expected a non-None value but got {output!r}"
            raise TypeError(msg)
        else:
            return output
    else:
        return catch_display.output
