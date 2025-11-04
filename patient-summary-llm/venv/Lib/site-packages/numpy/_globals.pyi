__all__ = ["_CopyMode", "_NoValue"]

import enum
from typing import Final, final

@final
class _CopyMode(enum.Enum):
    ALWAYS = True
    IF_NEEDED = False
    NEVER = 2

@final
class _NoValueType: ...

_NoValue: Final[_NoValueType] = ...
