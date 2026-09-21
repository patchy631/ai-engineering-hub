from typing import Any, Dict, List, Union, Generator
from contextlib import contextmanager

# Asyncio error messages
nest_asyncio_err = "cannot be called from a running event loop"
nest_asyncio_msg = (
    "The event loop is already running. "
    "Add `import nest_asyncio; nest_asyncio.apply()` to your code to fix this issue."
)


def is_jupyter() -> bool:
    """Check if we're running in a Jupyter environment."""
    try:
        from IPython import get_ipython

        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"
    except (ImportError, AttributeError):
        return False


@contextmanager
def augment_async_errors() -> Generator[None, None, None]:
    """Context manager to add helpful information for errors due to nested event loops."""
    try:
        yield
    except RuntimeError as e:
        if nest_asyncio_err in str(e):
            raise RuntimeError(nest_asyncio_msg)
        raise


JSONType = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
JSONObjectType = Dict[str, JSONType]
