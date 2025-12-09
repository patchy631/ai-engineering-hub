"""Font constants and classes for "layout" mode text operations"""

from dataclasses import dataclass, field
from typing import Any, Dict, Sequence, Union, cast

from ..._codecs import adobe_glyphs
from ...errors import ParseError
from ...generic import IndirectObject
from ._font_widths import STANDARD_WIDTHS


@dataclass
class Font:
    """
    A font object formatted for use during "layout" mode text extraction

    Attributes:
        subtype (str): font subtype
        space_width (int | float): width of a space character
        encoding (str | Dict[int, str]): font encoding
        char_map (dict): character map
        font_dictionary (dict): font dictionary
        width_map (Dict[str, int]): mapping of characters to widths
        interpretable (bool): Default True. If False, the font glyphs cannot
            be translated to characters, e.g. Type3 fonts that do not define
            a '/ToUnicode' mapping.

    """

    subtype: str
    space_width: Union[int, float]
    encoding: Union[str, Dict[int, str]]
    char_map: Dict[Any, Any]
    font_dictionary: Dict[Any, Any]
    width_map: Dict[str, int] = field(default_factory=dict, init=False)
    interpretable: bool = True

    def __post_init__(self) -> None:
        # Type3 fonts that do not specify a "/ToUnicode" mapping cannot be
        # reliably converted into character codes unless all named chars
        # in /CharProcs map to a standard adobe glyph. See § 9.10.2 of the
        # PDF 1.7 standard.
        if self.subtype == "/Type3" and "/ToUnicode" not in self.font_dictionary:
            self.interpretable = all(
                cname in adobe_glyphs
                for cname in self.font_dictionary.get("/CharProcs") or []
            )

        if not self.interpretable:  # save some overhead if font is not interpretable
            return

        # TrueType fonts have a /Widths array mapping character codes to widths
        if isinstance(self.encoding, dict) and "/Widths" in self.font_dictionary:
            first_char = self.font_dictionary.get("/FirstChar", 0)
            self.width_map = {
                self.encoding.get(idx + first_char, chr(idx + first_char)): width
                for idx, width in enumerate(self.font_dictionary["/Widths"])
            }

        # CID fonts have a /W array mapping character codes to widths stashed in /DescendantFonts
        if "/DescendantFonts" in self.font_dictionary:
            d_font: Dict[Any, Any]
            for d_font_idx, d_font in enumerate(
                self.font_dictionary["/DescendantFonts"]
            ):
                while isinstance(d_font, IndirectObject):
                    d_font = d_font.get_object()
                self.font_dictionary["/DescendantFonts"][d_font_idx] = d_font
                ord_map = {
                    ord(_target): _surrogate
                    for _target, _surrogate in self.char_map.items()
                    if isinstance(_target, str)
                }
                # /W width definitions have two valid formats which can be mixed and matched:
                #   (1) A character start index followed by a list of widths, e.g.
                #       `45 [500 600 700]` applies widths 500, 600, 700 to characters 45-47.
                #   (2) A character start index, a character stop index, and a width, e.g.
                #       `45 65 500` applies width 500 to characters 45-65.
                skip_count = 0
                _w = d_font.get("/W", [])
                for idx, w_entry in enumerate(_w):
                    w_entry = w_entry.get_object()
                    if skip_count:
                        skip_count -= 1
                        continue
                    if not isinstance(w_entry, (int, float)):  # pragma: no cover
                        # We should never get here due to skip_count above. Add a
                        # warning and or use reader's "strict" to force an ex???
                        continue
                    # check for format (1): `int [int int int int ...]`
                    w_next_entry = _w[idx + 1].get_object()
                    if isinstance(w_next_entry, Sequence):
                        start_idx, width_list = w_entry, w_next_entry
                        self.width_map.update(
                            {
                                ord_map[_cidx]: _width
                                for _cidx, _width in zip(
                                    range(
                                        cast(int, start_idx),
                                        cast(int, start_idx) + len(width_list),
                                        1,
                                    ),
                                    width_list,
                                )
                                if _cidx in ord_map
                            }
                        )
                        skip_count = 1
                    # check for format (2): `int int int`
                    elif isinstance(w_next_entry, (int, float)) and isinstance(
                        _w[idx + 2].get_object(), (int, float)
                    ):
                        start_idx, stop_idx, const_width = (
                            w_entry,
                            w_next_entry,
                            _w[idx + 2].get_object(),
                        )
                        self.width_map.update(
                            {
                                ord_map[_cidx]: const_width
                                for _cidx in range(
                                    cast(int, start_idx), cast(int, stop_idx + 1), 1
                                )
                                if _cidx in ord_map
                            }
                        )
                        skip_count = 2
                    else:
                        # Note: this doesn't handle the case of out of bounds (reaching the end of the width definitions
                        # while expecting more elements). This raises an IndexError which is sufficient.
                        raise ParseError(
                            f"Invalid font width definition. Next elements: {w_entry}, {w_next_entry}, {_w[idx + 2]}"
                        )  # pragma: no cover

        if not self.width_map and "/BaseFont" in self.font_dictionary:
            for key in STANDARD_WIDTHS:
                if self.font_dictionary["/BaseFont"].startswith(f"/{key}"):
                    self.width_map = STANDARD_WIDTHS[key]
                    break

    def word_width(self, word: str) -> float:
        """Sum of character widths specified in PDF font for the supplied word"""
        return sum(
            [self.width_map.get(char, self.space_width * 2) for char in word], 0.0
        )

    @staticmethod
    def to_dict(font_instance: "Font") -> Dict[str, Any]:
        """Dataclass to dict for json.dumps serialization."""
        return {
            k: getattr(font_instance, k) for k in font_instance.__dataclass_fields__
        }
