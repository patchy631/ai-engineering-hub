import binascii
from binascii import unhexlify
from math import ceil
from typing import Any, Dict, List, Tuple, Union, cast

from ._codecs import adobe_glyphs, charset_encoding
from ._utils import logger_error, logger_warning
from .generic import (
    DecodedStreamObject,
    DictionaryObject,
    StreamObject,
    is_null_or_none,
)


# code freely inspired from @twiggy ; see #711
def build_char_map(
    font_name: str, space_width: float, obj: DictionaryObject
) -> Tuple[str, float, Union[str, Dict[int, str]], Dict[Any, Any], DictionaryObject]:
    """
    Determine information about a font.

    Args:
        font_name: font name as a string
        space_width: default space width if no data is found.
        obj: XObject or Page where you can find a /Resource dictionary

    Returns:
        Font sub-type, space_width criteria (50% of width), encoding, map character-map, font-dictionary.
        The font-dictionary itself is suitable for the curious.

    """
    ft: DictionaryObject = obj["/Resources"]["/Font"][font_name]  # type: ignore
    font_subtype, font_halfspace, font_encoding, font_map = build_char_map_from_dict(
        space_width, ft
    )
    return font_subtype, font_halfspace, font_encoding, font_map, ft


def build_char_map_from_dict(
    space_width: float, ft: DictionaryObject
) -> Tuple[str, float, Union[str, Dict[int, str]], Dict[Any, Any]]:
    """
    Determine information about a font.

    Args:
        space_width: default space with if no data found
             (normally half the width of a character).
        ft: Font Dictionary

    Returns:
        Font sub-type, space_width criteria(50% of width), encoding, map character-map.
        The font-dictionary itself is suitable for the curious.

    """
    font_type = cast(str, ft["/Subtype"].get_object())
    encoding, map_dict = get_encoding(ft)

    space_key_char = get_actual_str_key(" ", encoding, map_dict)
    font_width_map = build_font_width_map(ft, space_width * 2.0)
    half_space_width = compute_space_width(font_width_map, space_key_char) / 2.0

    return (
        font_type,
        half_space_width,
        encoding,
        # https://github.com/python/mypy/issues/4374
        map_dict
    )


# used when missing data, e.g. font def missing
unknown_char_map: Tuple[str, float, Union[str, Dict[int, str]], Dict[Any, Any]] = (
    "Unknown",
    9999,
    dict(zip(range(256), ["�"] * 256)),
    {},
)


_predefined_cmap: Dict[str, str] = {
    "/Identity-H": "utf-16-be",
    "/Identity-V": "utf-16-be",
    "/GB-EUC-H": "gbk",
    "/GB-EUC-V": "gbk",
    "/GBpc-EUC-H": "gb2312",
    "/GBpc-EUC-V": "gb2312",
    "/GBK-EUC-H": "gbk",
    "/GBK-EUC-V": "gbk",
    "/GBK2K-H": "gb18030",
    "/GBK2K-V": "gb18030",
    "/ETen-B5-H": "cp950",
    "/ETen-B5-V": "cp950",
    "/ETenms-B5-H": "cp950",
    "/ETenms-B5-V": "cp950",
    "/UniCNS-UTF16-H": "utf-16-be",
    "/UniCNS-UTF16-V": "utf-16-be",
    "/UniGB-UTF16-H": "gb18030",
    "/UniGB-UTF16-V": "gb18030",
    # UCS2 in code
}

# manually extracted from http://mirrors.ctan.org/fonts/adobe/afm/Adobe-Core35_AFMs-229.tar.gz
_default_fonts_space_width: Dict[str, int] = {
    "/Courier": 600,
    "/Courier-Bold": 600,
    "/Courier-BoldOblique": 600,
    "/Courier-Oblique": 600,
    "/Helvetica": 278,
    "/Helvetica-Bold": 278,
    "/Helvetica-BoldOblique": 278,
    "/Helvetica-Oblique": 278,
    "/Helvetica-Narrow": 228,
    "/Helvetica-NarrowBold": 228,
    "/Helvetica-NarrowBoldOblique": 228,
    "/Helvetica-NarrowOblique": 228,
    "/Times-Roman": 250,
    "/Times-Bold": 250,
    "/Times-BoldItalic": 250,
    "/Times-Italic": 250,
    "/Symbol": 250,
    "/ZapfDingbats": 278,
}


def get_encoding(
    ft: DictionaryObject
) -> Tuple[Union[str, Dict[int, str]], Dict[Any, Any]]:
    encoding = _parse_encoding(ft)
    map_dict, int_entry = _parse_to_unicode(ft)

    # Apply rule from PDF ref 1.7 §5.9.1, 1st bullet:
    #   if cmap not empty encoding should be discarded
    #   (here transformed into identity for those characters)
    # If encoding is a string it is expected to be an identity translation.
    if isinstance(encoding, dict):
        for x in int_entry:
            if x <= 255:
                encoding[x] = chr(x)

    return encoding, map_dict


def _parse_encoding(
    ft: DictionaryObject
) -> Union[str, Dict[int, str]]:
    encoding: Union[str, List[str], Dict[int, str]] = []
    if "/Encoding" not in ft:
        if "/BaseFont" in ft and cast(str, ft["/BaseFont"]) in charset_encoding:
            encoding = dict(
                zip(range(256), charset_encoding[cast(str, ft["/BaseFont"])])
            )
        else:
            encoding = "charmap"
        return encoding
    enc: Union(str, DictionaryObject) = ft["/Encoding"].get_object()  # type: ignore
    if isinstance(enc, str):
        try:
            # already done : enc = NameObject.unnumber(enc.encode()).decode()
            # for #xx decoding
            if enc in charset_encoding:
                encoding = charset_encoding[enc].copy()
            elif enc in _predefined_cmap:
                encoding = _predefined_cmap[enc]
            elif "-UCS2-" in enc:
                encoding = "utf-16-be"
            else:
                raise Exception("not found")
        except Exception:
            logger_error(f"Advanced encoding {enc} not implemented yet", __name__)
            encoding = enc
    elif isinstance(enc, DictionaryObject) and "/BaseEncoding" in enc:
        try:
            encoding = charset_encoding[cast(str, enc["/BaseEncoding"])].copy()
        except Exception:
            logger_error(
                f"Advanced encoding {encoding} not implemented yet",
                __name__,
            )
            encoding = charset_encoding["/StandardEncoding"].copy()
    else:
        encoding = charset_encoding["/StandardEncoding"].copy()
    if "/Differences" in enc:
        x: int = 0
        o: Union[int, str]
        for o in cast(DictionaryObject, cast(DictionaryObject, enc)["/Differences"]):
            if isinstance(o, int):
                x = o
            else:  # isinstance(o,str):
                try:
                    if x < len(encoding):
                        encoding[x] = adobe_glyphs[o]  # type: ignore
                except Exception:
                    encoding[x] = o  # type: ignore
                x += 1
    if isinstance(encoding, list):
        encoding = dict(zip(range(256), encoding))
    return encoding


def _parse_to_unicode(
    ft: DictionaryObject
) -> Tuple[Dict[Any, Any], List[int]]:
    # will store all translation code
    # and map_dict[-1] we will have the number of bytes to convert
    map_dict: Dict[Any, Any] = {}

    # will provide the list of cmap keys as int to correct encoding
    int_entry: List[int] = []

    if "/ToUnicode" not in ft:
        if ft.get("/Subtype", "") == "/Type1":
            return _type1_alternative(ft, map_dict, int_entry)
        else:
            return {}, []
    process_rg: bool = False
    process_char: bool = False
    multiline_rg: Union[
        None, Tuple[int, int]
    ] = None  # tuple = (current_char, remaining size) ; cf #1285 for example of file
    cm = prepare_cm(ft)
    for line in cm.split(b"\n"):
        process_rg, process_char, multiline_rg = process_cm_line(
            line.strip(b" \t"),
            process_rg,
            process_char,
            multiline_rg,
            map_dict,
            int_entry,
        )

    return map_dict, int_entry


def get_actual_str_key(
    value_char: str, encoding: Union[str, Dict[int, str]], map_dict: Dict[Any, Any]
) -> str:
    key_dict = {}
    if isinstance(encoding, dict):
        key_dict = {value: chr(key) for key, value in encoding.items() if value == value_char}
    else:
        key_dict = {value: key for key, value in map_dict.items() if value == value_char}
    key_char = key_dict.get(value_char, value_char)
    return key_char


def prepare_cm(ft: DictionaryObject) -> bytes:
    tu = ft["/ToUnicode"]
    cm: bytes
    if isinstance(tu, StreamObject):
        cm = cast(DecodedStreamObject, ft["/ToUnicode"]).get_data()
    else:  # if (tu is None) or cast(str, tu).startswith("/Identity"):
        # the full range 0000-FFFF will be processed
        cm = b"beginbfrange\n<0000> <0001> <0000>\nendbfrange"
    if isinstance(cm, str):
        cm = cm.encode()
    # we need to prepare cm before due to missing return line in pdf printed
    # to pdf from word
    cm = (
        cm.strip()
        .replace(b"beginbfchar", b"\nbeginbfchar\n")
        .replace(b"endbfchar", b"\nendbfchar\n")
        .replace(b"beginbfrange", b"\nbeginbfrange\n")
        .replace(b"endbfrange", b"\nendbfrange\n")
        .replace(b"<<", b"\n{\n")  # text between << and >> not used but
        .replace(b">>", b"\n}\n")  # some solution to find it back
    )
    ll = cm.split(b"<")
    for i in range(len(ll)):
        j = ll[i].find(b">")
        if j >= 0:
            if j == 0:
                # string is empty: stash a placeholder here (see below)
                # see https://github.com/py-pdf/pypdf/issues/1111
                content = b"."
            else:
                content = ll[i][:j].replace(b" ", b"")
            ll[i] = content + b" " + ll[i][j + 1 :]
    cm = (
        (b" ".join(ll))
        .replace(b"[", b" [ ")
        .replace(b"]", b" ]\n ")
        .replace(b"\r", b"\n")
    )
    return cm


def process_cm_line(
    line: bytes,
    process_rg: bool,
    process_char: bool,
    multiline_rg: Union[None, Tuple[int, int]],
    map_dict: Dict[Any, Any],
    int_entry: List[int],
) -> Tuple[bool, bool, Union[None, Tuple[int, int]]]:
    if line == b"" or line[0] == 37:  # 37 = %
        return process_rg, process_char, multiline_rg
    line = line.replace(b"\t", b" ")
    if b"beginbfrange" in line:
        process_rg = True
    elif b"endbfrange" in line:
        process_rg = False
    elif b"beginbfchar" in line:
        process_char = True
    elif b"endbfchar" in line:
        process_char = False
    elif process_rg:
        try:
            multiline_rg = parse_bfrange(line, map_dict, int_entry, multiline_rg)
        except binascii.Error as error:
            logger_warning(f"Skipping broken line {line!r}: {error}", __name__)
    elif process_char:
        parse_bfchar(line, map_dict, int_entry)
    return process_rg, process_char, multiline_rg


def parse_bfrange(
    line: bytes,
    map_dict: Dict[Any, Any],
    int_entry: List[int],
    multiline_rg: Union[None, Tuple[int, int]],
) -> Union[None, Tuple[int, int]]:
    lst = [x for x in line.split(b" ") if x]
    closure_found = False
    if multiline_rg is not None:
        fmt = b"%%0%dX" % (map_dict[-1] * 2)
        a = multiline_rg[0]  # a, b not in the current line
        b = multiline_rg[1]
        for sq in lst[0:]:
            if sq == b"]":
                closure_found = True
                break
            map_dict[
                unhexlify(fmt % a).decode(
                    "charmap" if map_dict[-1] == 1 else "utf-16-be",
                    "surrogatepass",
                )
            ] = unhexlify(sq).decode("utf-16-be", "surrogatepass")
            int_entry.append(a)
            a += 1
    else:
        a = int(lst[0], 16)
        b = int(lst[1], 16)
        nbi = max(len(lst[0]), len(lst[1]))
        map_dict[-1] = ceil(nbi / 2)
        fmt = b"%%0%dX" % (map_dict[-1] * 2)
        if lst[2] == b"[":
            for sq in lst[3:]:
                if sq == b"]":
                    closure_found = True
                    break
                map_dict[
                    unhexlify(fmt % a).decode(
                        "charmap" if map_dict[-1] == 1 else "utf-16-be",
                        "surrogatepass",
                    )
                ] = unhexlify(sq).decode("utf-16-be", "surrogatepass")
                int_entry.append(a)
                a += 1
        else:  # case without list
            c = int(lst[2], 16)
            fmt2 = b"%%0%dX" % max(4, len(lst[2]))
            closure_found = True
            while a <= b:
                map_dict[
                    unhexlify(fmt % a).decode(
                        "charmap" if map_dict[-1] == 1 else "utf-16-be",
                        "surrogatepass",
                    )
                ] = unhexlify(fmt2 % c).decode("utf-16-be", "surrogatepass")
                int_entry.append(a)
                a += 1
                c += 1
    return None if closure_found else (a, b)


def parse_bfchar(line: bytes, map_dict: Dict[Any, Any], int_entry: List[int]) -> None:
    lst = [x for x in line.split(b" ") if x]
    map_dict[-1] = len(lst[0]) // 2
    while len(lst) > 1:
        map_to = ""
        # placeholder (see above) means empty string
        if lst[1] != b".":
            map_to = unhexlify(lst[1]).decode(
                "charmap" if len(lst[1]) < 4 else "utf-16-be", "surrogatepass"
            )  # join is here as some cases where the code was split
        map_dict[
            unhexlify(lst[0]).decode(
                "charmap" if map_dict[-1] == 1 else "utf-16-be", "surrogatepass"
            )
        ] = map_to
        int_entry.append(int(lst[0], 16))
        lst = lst[2:]


def build_font_width_map(
    ft: DictionaryObject, default_font_width: float
) -> Dict[Any, float]:
    font_width_map: Dict[Any, float] = {}
    st: int = 0
    en: int = 0
    try:
        default_font_width = _default_fonts_space_width[cast(str, ft["/BaseFont"].get_object())] * 2.0
    except KeyError:
        pass
    if "/DescendantFonts" in ft:  # ft["/Subtype"].startswith("/CIDFontType"):
        # §9.7.4.3 of the 1.7 reference ("Glyph Metrics in CIDFonts")
        # Widths for a CIDFont are defined using the DW and W entries.
        # DW2 and W2 are for vertical use. Vertical type is not implemented.
        ft1 = ft["/DescendantFonts"][0].get_object()  # type: ignore
        if "/DW" in ft1:
            font_width_map["default"] = cast(float, ft1["/DW"].get_object())
        else:
            font_width_map["default"] = default_font_width
        if "/W" in ft1:
            w = ft1["/W"].get_object()
        else:
            w = []
        while len(w) > 0:
            st = w[0] if isinstance(w[0], int) else w[0].get_object()
            second = w[1].get_object()
            if isinstance(second, int):
                # C_first C_last same_W
                en = second
                width = w[2].get_object()
                if not isinstance(width, (int, float)):
                    logger_warning(f"Expected numeric value for width, got {width}. Ignoring it.", __name__)
                    w = w[3:]
                    continue
                for c_code in range(st, en + 1):
                    font_width_map[chr(c_code)] = width
                w = w[3:]
            elif isinstance(second, list):
                # Starting_C [W1 W2 ... Wn]
                c_code = st
                for ww in second:
                    width = ww.get_object()
                    font_width_map[chr(c_code)] = width
                    c_code += 1
                w = w[2:]
            else:
                logger_warning(
                    "unknown widths : \n" + (ft1["/W"]).__repr__(),
                    __name__,
                )
                break
    elif "/Widths" in ft:
        w = ft["/Widths"].get_object()
        if "/FontDescriptor" in ft and "/MissingWidth" in cast(
            DictionaryObject, ft["/FontDescriptor"]
        ):
            font_width_map["default"] = ft["/FontDescriptor"]["/MissingWidth"].get_object()  # type: ignore
        else:
            # will consider width of char as avg(width)
            m = 0
            cpt = 0
            for xx in w:
                xx = xx.get_object()
                if xx > 0:
                    m += xx
                    cpt += 1
            font_width_map["default"] = m / max(1, cpt)
        st = cast(int, ft["/FirstChar"])
        en = cast(int, ft["/LastChar"])
        for c_code in range(st, en + 1):
            try:
                width = w[c_code - st].get_object()
                font_width_map[chr(c_code)] = width
            except (IndexError, KeyError):
                # The PDF structure is invalid. The array is too small
                # for the specified font width.
                pass
    if is_null_or_none(font_width_map.get("default")):
        font_width_map["default"] = default_font_width if default_font_width else 0.0
    return font_width_map


def compute_space_width(
    font_width_map: Dict[Any, float], space_char: str
) -> float:
    try:
        sp_width = font_width_map[space_char]
        if sp_width == 0:
            raise ValueError("Zero width")
    except (KeyError, ValueError):
        sp_width = (
            font_width_map["default"] / 2.0
        )  # if using default we consider space will be only half size

    return sp_width


def compute_font_width(
    font_width_map: Dict[Any, float],
    char: str
) -> float:
    char_width: float = 0.0
    try:
        char_width = font_width_map[char]
    except KeyError:
        char_width = (
            font_width_map["default"]
        )

    return char_width


def _type1_alternative(
    ft: DictionaryObject,
    map_dict: Dict[Any, Any],
    int_entry: List[int],
) -> Tuple[Dict[Any, Any], List[int]]:
    if "/FontDescriptor" not in ft:
        return map_dict, int_entry
    ft_desc = cast(DictionaryObject, ft["/FontDescriptor"]).get("/FontFile")
    if is_null_or_none(ft_desc):
        return map_dict, int_entry
    assert ft_desc is not None, "mypy"
    txt = ft_desc.get_object().get_data()
    txt = txt.split(b"eexec\n")[0]  # only clear part
    txt = txt.split(b"/Encoding")[1]  # to get the encoding part
    lines = txt.replace(b"\r", b"\n").split(b"\n")
    for li in lines:
        if li.startswith(b"dup"):
            words = [_w for _w in li.split(b" ") if _w != b""]
            if len(words) > 3 and words[3] != b"put":
                continue
            try:
                i = int(words[1])
            except ValueError:  # pragma: no cover
                continue
            try:
                v = adobe_glyphs[words[2].decode()]
            except KeyError:
                if words[2].startswith(b"/uni"):
                    try:
                        v = chr(int(words[2][4:], 16))
                    except ValueError:  # pragma: no cover
                        continue
                else:
                    continue
            map_dict[chr(i)] = v
            int_entry.append(i)
    return map_dict, int_entry
