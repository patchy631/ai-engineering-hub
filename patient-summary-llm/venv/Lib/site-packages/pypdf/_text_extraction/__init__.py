"""
Code related to text extraction.

Some parts are still in _page.py. In doubt, they will stay there.
"""

import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from ..generic import DictionaryObject, TextStringObject, encode_pdfdocencoding

CUSTOM_RTL_MIN: int = -1
CUSTOM_RTL_MAX: int = -1
CUSTOM_RTL_SPECIAL_CHARS: List[int] = []
LAYOUT_NEW_BT_GROUP_SPACE_WIDTHS: int = 5


class OrientationNotFoundError(Exception):
    pass


def set_custom_rtl(
    _min: Union[str, int, None] = None,
    _max: Union[str, int, None] = None,
    specials: Union[str, List[int], None] = None,
) -> Tuple[int, int, List[int]]:
    """
    Change the Right-To-Left and special characters custom parameters.

    Args:
        _min: The new minimum value for the range of custom characters that
            will be written right to left.
            If set to ``None``, the value will not be changed.
            If set to an integer or string, it will be converted to its ASCII code.
            The default value is -1, which sets no additional range to be converted.
        _max: The new maximum value for the range of custom characters that will
            be written right to left.
            If set to ``None``, the value will not be changed.
            If set to an integer or string, it will be converted to its ASCII code.
            The default value is -1, which sets no additional range to be converted.
        specials: The new list of special characters to be inserted in the
            current insertion order.
            If set to ``None``, the current value will not be changed.
            If set to a string, it will be converted to a list of ASCII codes.
            The default value is an empty list.

    Returns:
        A tuple containing the new values for ``CUSTOM_RTL_MIN``,
        ``CUSTOM_RTL_MAX``, and ``CUSTOM_RTL_SPECIAL_CHARS``.

    """
    global CUSTOM_RTL_MIN, CUSTOM_RTL_MAX, CUSTOM_RTL_SPECIAL_CHARS
    if isinstance(_min, int):
        CUSTOM_RTL_MIN = _min
    elif isinstance(_min, str):
        CUSTOM_RTL_MIN = ord(_min)
    if isinstance(_max, int):
        CUSTOM_RTL_MAX = _max
    elif isinstance(_max, str):
        CUSTOM_RTL_MAX = ord(_max)
    if isinstance(specials, str):
        CUSTOM_RTL_SPECIAL_CHARS = [ord(x) for x in specials]
    elif isinstance(specials, list):
        CUSTOM_RTL_SPECIAL_CHARS = specials
    return CUSTOM_RTL_MIN, CUSTOM_RTL_MAX, CUSTOM_RTL_SPECIAL_CHARS


def mult(m: List[float], n: List[float]) -> List[float]:
    return [
        m[0] * n[0] + m[1] * n[2],
        m[0] * n[1] + m[1] * n[3],
        m[2] * n[0] + m[3] * n[2],
        m[2] * n[1] + m[3] * n[3],
        m[4] * n[0] + m[5] * n[2] + n[4],
        m[4] * n[1] + m[5] * n[3] + n[5],
    ]


def orient(m: List[float]) -> int:
    if m[3] > 1e-6:
        return 0
    elif m[3] < -1e-6:
        return 180
    elif m[1] > 0:
        return 90
    else:
        return 270


def crlf_space_check(
    text: str,
    cmtm_prev: Tuple[List[float], List[float]],
    cmtm_matrix: Tuple[List[float], List[float]],
    memo_cmtm: Tuple[List[float], List[float]],
    cmap: Tuple[
        Union[str, Dict[int, str]], Dict[str, str], str, Optional[DictionaryObject]
    ],
    orientations: Tuple[int, ...],
    output: str,
    font_size: float,
    visitor_text: Optional[Callable[[Any, Any, Any, Any, Any], None]],
    str_widths: float,
    spacewidth: float,
    str_height: float,
) -> Tuple[str, str, List[float], List[float]]:
    cm_prev = cmtm_prev[0]
    tm_prev = cmtm_prev[1]
    cm_matrix = cmtm_matrix[0]
    tm_matrix = cmtm_matrix[1]
    memo_cm = memo_cmtm[0]
    memo_tm = memo_cmtm[1]

    m_prev = mult(tm_prev, cm_prev)
    m = mult(tm_matrix, cm_matrix)
    orientation = orient(m)
    delta_x = m[4] - m_prev[4]
    delta_y = m[5] - m_prev[5]
    # Table 108 of the 1.7 reference ("Text positioning operators")
    scale_prev_x = math.sqrt(tm_prev[0]**2 + tm_prev[1]**2)
    scale_prev_y = math.sqrt(tm_prev[2]**2 + tm_prev[3]**2)
    scale_y = math.sqrt(tm_matrix[2]**2 + tm_matrix[3]**2)
    cm_prev = m

    if orientation not in orientations:
        raise OrientationNotFoundError
    if orientation in (0, 180):
        moved_height: float = delta_y
        moved_width: float = delta_x
    elif orientation in (90, 270):
        moved_height = delta_x
        moved_width = delta_y
    try:
        if abs(moved_height) > 0.8 * min(str_height * scale_prev_y, font_size * scale_y):
            if (output + text)[-1] != "\n":
                output += text + "\n"
                if visitor_text is not None:
                    visitor_text(
                        text + "\n",
                        memo_cm,
                        memo_tm,
                        cmap[3],
                        font_size,
                    )
                text = ""
        elif (
            (moved_width >= (spacewidth + str_widths) * scale_prev_x)
            and (output + text)[-1] != " "
        ):
            text += " "
    except Exception:
        pass
    tm_prev = tm_matrix.copy()
    cm_prev = cm_matrix.copy()
    return text, output, cm_prev, tm_prev


def get_text_operands(
    operands: List[Union[str, TextStringObject]],
    cm_matrix: List[float],
    tm_matrix: List[float],
    cmap: Tuple[
        Union[str, Dict[int, str]], Dict[str, str], str, Optional[DictionaryObject]
    ],
    orientations: Tuple[int, ...]
) -> Tuple[str, bool]:
    t: str = ""
    is_str_operands = False
    m = mult(tm_matrix, cm_matrix)
    orientation = orient(m)
    if orientation in orientations and len(operands) > 0:
        if isinstance(operands[0], str):
            t = operands[0]
            is_str_operands = True
        else:
            t = ""
            tt: bytes = (
                encode_pdfdocencoding(operands[0])
                if isinstance(operands[0], str)
                else operands[0]
            )
            if isinstance(cmap[0], str):
                try:
                    t = tt.decode(cmap[0], "surrogatepass")  # apply str encoding
                except Exception:
                    # the data does not match the expectation,
                    # we use the alternative ;
                    # text extraction may not be good
                    t = tt.decode(
                        "utf-16-be" if cmap[0] == "charmap" else "charmap",
                        "surrogatepass",
                    )  # apply str encoding
            else:  # apply dict encoding
                t = "".join(
                    [cmap[0][x] if x in cmap[0] else bytes((x,)).decode() for x in tt]
                )
    return (t, is_str_operands)


def get_display_str(
    text: str,
    cm_matrix: List[float],
    tm_matrix: List[float],
    cmap: Tuple[
        Union[str, Dict[int, str]], Dict[str, str], str, Optional[DictionaryObject]
    ],
    text_operands: str,
    font_size: float,
    rtl_dir: bool,
    visitor_text: Optional[Callable[[Any, Any, Any, Any, Any], None]]
) -> Tuple[str, bool]:
    # "\u0590 - \u08FF \uFB50 - \uFDFF"
    for x in [cmap[1].get(x, x) for x in text_operands]:
        # x can be a sequence of bytes ; ex: habibi.pdf
        if len(x) == 1:
            xx = ord(x)
        else:
            xx = 1
        # fmt: off
        if (
            # cases where the current inserting order is kept
            (xx <= 0x2F)                        # punctuations but...
            or 0x3A <= xx <= 0x40               # numbers (x30-39)
            or 0x2000 <= xx <= 0x206F           # upper punctuations..
            or 0x20A0 <= xx <= 0x21FF           # but (numbers) indices/exponents
            or xx in CUSTOM_RTL_SPECIAL_CHARS   # customized....
        ):
            text = x + text if rtl_dir else text + x
        elif (  # right-to-left characters set
            0x0590 <= xx <= 0x08FF
            or 0xFB1D <= xx <= 0xFDFF
            or 0xFE70 <= xx <= 0xFEFF
            or CUSTOM_RTL_MIN <= xx <= CUSTOM_RTL_MAX
        ):
            if not rtl_dir:
                rtl_dir = True
                if visitor_text is not None:
                    visitor_text(text, cm_matrix, tm_matrix, cmap[3], font_size)
                text = ""
            text = x + text
        else:  # left-to-right
            if rtl_dir:
                rtl_dir = False
                if visitor_text is not None:
                    visitor_text(text, cm_matrix, tm_matrix, cmap[3], font_size)
                text = ""
            text = text + x
        # fmt: on
    return text, rtl_dir
