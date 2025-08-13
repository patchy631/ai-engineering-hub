"""Code in here is only used by pypdf.filters._xobj_to_image"""

import sys
from io import BytesIO
from typing import Any, Dict, List, Literal, Tuple, Union, cast

from ._utils import check_if_whitespace_only, logger_warning
from .constants import ColorSpaces
from .constants import FilterTypes as FT
from .constants import ImageAttributes as IA
from .errors import EmptyImageDataError, PdfReadError
from .generic import (
    ArrayObject,
    DecodedStreamObject,
    EncodedStreamObject,
    IndirectObject,
    NullObject,
    TextStringObject,
)

if sys.version_info[:2] >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias


try:
    from PIL import Image, UnidentifiedImageError  # noqa: F401
except ImportError:
    raise ImportError(
        "pillow is required to do image extraction. "
        "It can be installed via 'pip install pypdf[image]'"
    )

mode_str_type: TypeAlias = Literal[
    "", "1", "RGB", "2bits", "4bits", "P", "L", "RGBA", "CMYK"
]

MAX_IMAGE_MODE_NESTING_DEPTH: int = 10


def _get_imagemode(
    color_space: Union[str, List[Any], Any],
    color_components: int,
    prev_mode: mode_str_type,
    depth: int = 0,
) -> Tuple[mode_str_type, bool]:
    """
    Returns:
        Image mode, not taking into account mask (transparency).
        ColorInversion is required (like for some DeviceCMYK).

    """
    if depth > MAX_IMAGE_MODE_NESTING_DEPTH:
        raise PdfReadError(
            "Color spaces nested too deeply. If required, consider increasing MAX_IMAGE_MODE_NESTING_DEPTH."
        )
    if isinstance(color_space, NullObject):
        return "", False
    if isinstance(color_space, str):
        pass
    elif not isinstance(color_space, list):
        raise PdfReadError(
            "Cannot interpret color space", color_space
        )  # pragma: no cover
    elif color_space[0].startswith("/Cal"):  # /CalRGB and /CalGray
        color_space = "/Device" + color_space[0][4:]
    elif color_space[0] == "/ICCBased":
        icc_profile = color_space[1].get_object()
        color_components = cast(int, icc_profile["/N"])
        color_space = icc_profile.get("/Alternate", "")
    elif color_space[0] == "/Indexed":
        color_space = color_space[1].get_object()
        mode, invert_color = _get_imagemode(
            color_space, color_components, prev_mode, depth + 1
        )
        if mode in ("RGB", "CMYK"):
            mode = "P"
        return mode, invert_color
    elif color_space[0] == "/Separation":
        color_space = color_space[2]
        if isinstance(color_space, IndirectObject):
            color_space = color_space.get_object()
        mode, invert_color = _get_imagemode(
            color_space, color_components, prev_mode, depth + 1
        )
        return mode, True
    elif color_space[0] == "/DeviceN":
        original_color_space = color_space
        color_components = len(color_space[1])
        color_space = color_space[2]
        if isinstance(color_space, IndirectObject):  # pragma: no cover
            color_space = color_space.get_object()
        if color_space == "/DeviceCMYK" and color_components == 1:
            if original_color_space[1][0] != "/Black":
                logger_warning(
                    f"Color {original_color_space[1][0]} converted to Gray. Please share PDF with pypdf dev team",
                    __name__,
                )
            return "L", True
        mode, invert_color = _get_imagemode(
            color_space, color_components, prev_mode, depth + 1
        )
        return mode, invert_color

    mode_map: Dict[str, mode_str_type] = {
        "1bit": "1",  # must be zeroth position: color_components may index the values
        "/DeviceGray": "L",  # must be first position: color_components may index the values
        "palette": "P",  # must be second position: color_components may index the values
        "/DeviceRGB": "RGB",  # must be third position: color_components may index the values
        "/DeviceCMYK": "CMYK",  # must be fourth position: color_components may index the values
        "2bit": "2bits",
        "4bit": "4bits",
    }

    mode = (
        mode_map.get(color_space)
        or list(mode_map.values())[color_components]
        or prev_mode
    )

    return mode, mode == "CMYK"


def bits2byte(data: bytes, size: Tuple[int, int], bits: int) -> bytes:
    mask = (1 << bits) - 1
    byte_buffer = bytearray(size[0] * size[1])
    data_index = 0
    bit = 8 - bits
    for y in range(size[1]):
        if bit != 8 - bits:
            data_index += 1
            bit = 8 - bits
        for x in range(size[0]):
            byte_buffer[x + y * size[0]] = (data[data_index] >> bit) & mask
            bit -= bits
            if bit < 0:
                data_index += 1
                bit = 8 - bits
    return bytes(byte_buffer)


def _extended_image_frombytes(
    mode: str, size: Tuple[int, int], data: bytes
) -> Image.Image:
    try:
        img = Image.frombytes(mode, size, data)
    except ValueError as exc:
        nb_pix = size[0] * size[1]
        data_length = len(data)
        if data_length == 0:
            raise EmptyImageDataError(
                "Data is 0 bytes, cannot process an image from empty data."
            ) from exc
        if data_length % nb_pix != 0:
            raise exc
        k = nb_pix * len(mode) / data_length
        data = b"".join(bytes((x,) * int(k)) for x in data)
        img = Image.frombytes(mode, size, data)
    return img


def _handle_flate(
    size: Tuple[int, int],
    data: bytes,
    mode: mode_str_type,
    color_space: str,
    colors: int,
    obj_as_text: str,
) -> Tuple[Image.Image, str, str, bool]:
    """
    Process image encoded in flateEncode
    Returns img, image_format, extension, color inversion
    """
    extension = ".png"  # mime_type = "image/png"
    image_format = "PNG"
    lookup: Any
    base: Any
    hival: Any
    if isinstance(color_space, ArrayObject) and color_space[0] == "/Indexed":
        color_space, base, hival, lookup = (value.get_object() for value in color_space)
    if mode == "2bits":
        mode = "P"
        data = bits2byte(data, size, 2)
    elif mode == "4bits":
        mode = "P"
        data = bits2byte(data, size, 4)
    img = _extended_image_frombytes(mode, size, data)
    if color_space == "/Indexed":
        if isinstance(lookup, (EncodedStreamObject, DecodedStreamObject)):
            lookup = lookup.get_data()
        if isinstance(lookup, TextStringObject):
            lookup = lookup.original_bytes
        if isinstance(lookup, str):
            lookup = lookup.encode()
        try:
            nb, conv, mode = {  # type: ignore
                "1": (0, "", ""),
                "L": (1, "P", "L"),
                "P": (0, "", ""),
                "RGB": (3, "P", "RGB"),
                "CMYK": (4, "P", "CMYK"),
            }[_get_imagemode(base, 0, "")[0]]
        except KeyError:  # pragma: no cover
            logger_warning(
                f"Base {base} not coded please share the pdf file with pypdf dev team",
                __name__,
            )
            lookup = None
        else:
            if img.mode == "1":
                # Two values ("high" and "low").
                expected_count = 2 * nb
                actual_count = len(lookup)
                if actual_count != expected_count:
                    if actual_count < expected_count:
                        logger_warning(
                            f"Not enough lookup values: Expected {expected_count}, got {actual_count}.",
                            __name__
                        )
                        lookup += bytes([0] * (expected_count - actual_count))
                    elif not check_if_whitespace_only(lookup[expected_count:]):
                        logger_warning(
                            f"Too many lookup values: Expected {expected_count}, got {actual_count}.",
                            __name__
                        )
                    lookup = lookup[:expected_count]
                colors_arr = [lookup[:nb], lookup[nb:]]
                arr = b"".join(
                    b"".join(
                        colors_arr[1 if img.getpixel((x, y)) > 127 else 0]
                        for x in range(img.size[0])
                    )
                    for y in range(img.size[1])
                )
                img = Image.frombytes(mode, img.size, arr)
            else:
                img = img.convert(conv)
                if len(lookup) != (hival + 1) * nb:
                    logger_warning(f"Invalid Lookup Table in {obj_as_text}", __name__)
                    lookup = None
                elif mode == "L":
                    # gray lookup does not work : it is converted to a similar RGB lookup
                    lookup = b"".join([bytes([b, b, b]) for b in lookup])
                    mode = "RGB"
                # TODO : cf https://github.com/py-pdf/pypdf/pull/2039
                # this is a work around until PIL is able to process CMYK images
                elif mode == "CMYK":
                    _rgb = []
                    for _c, _m, _y, _k in (
                        lookup[n : n + 4] for n in range(0, 4 * (len(lookup) // 4), 4)
                    ):
                        _r = int(255 * (1 - _c / 255) * (1 - _k / 255))
                        _g = int(255 * (1 - _m / 255) * (1 - _k / 255))
                        _b = int(255 * (1 - _y / 255) * (1 - _k / 255))
                        _rgb.append(bytes((_r, _g, _b)))
                    lookup = b"".join(_rgb)
                    mode = "RGB"
                if lookup is not None:
                    img.putpalette(lookup, rawmode=mode)
            img = img.convert("L" if base == ColorSpaces.DEVICE_GRAY else "RGB")
    elif not isinstance(color_space, NullObject) and color_space[0] == "/ICCBased":
        # see Table 66 - Additional Entries Specific to an ICC Profile
        # Stream Dictionary
        mode2 = _get_imagemode(color_space, colors, mode)[0]
        if mode != mode2:
            img = Image.frombytes(mode2, size, data)  # reloaded as mode may have change
    if mode == "CMYK":
        extension = ".tif"
        image_format = "TIFF"
    return img, image_format, extension, False


def _handle_jpx(
    size: Tuple[int, int],
    data: bytes,
    mode: mode_str_type,
    color_space: str,
    colors: int,
) -> Tuple[Image.Image, str, str, bool]:
    """
    Process image encoded in flateEncode
    Returns img, image_format, extension, inversion
    """
    extension = ".jp2"  # mime_type = "image/x-jp2"
    img1 = Image.open(BytesIO(data), formats=("JPEG2000",))
    mode, invert_color = _get_imagemode(color_space, colors, mode)
    if mode == "":
        mode = cast(mode_str_type, img1.mode)
        invert_color = mode in ("CMYK",)
    if img1.mode == "RGBA" and mode == "RGB":
        mode = "RGBA"
    # we need to convert to the good mode
    if img1.mode == mode or {img1.mode, mode} == {"L", "P"}:  # compare (unordered) sets
        # L and P are indexed modes which should not be changed.
        img = img1
    elif {img1.mode, mode} == {"RGBA", "CMYK"}:
        # RGBA / CMYK are 4bytes encoding where
        # the encoding should be corrected
        img = Image.frombytes(mode, img1.size, img1.tobytes())
    else:  # pragma: no cover
        img = img1.convert(mode)
    # for CMYK conversion :
    # https://stcom/questions/38855022/conversion-from-cmyk-to-rgb-with-pillow-is-different-from-that-of-photoshop
    # not implemented for the moment as I need to get properly the ICC
    if img.mode == "CMYK":
        img = img.convert("RGB")
    image_format = "JPEG2000"
    return img, image_format, extension, invert_color


def _apply_decode(
    img: Image.Image,
    x_object_obj: Dict[str, Any],
    lfilters: FT,
    color_space: Union[str, List[Any], Any],
    invert_color: bool,
) -> Image.Image:
    # CMYK image and other color spaces without decode
    # requires reverting scale (cf p243,2§ last sentence)
    decode = x_object_obj.get(
        IA.DECODE,
        ([1.0, 0.0] * len(img.getbands()))
        if (
            (img.mode == "CMYK" and lfilters in (FT.DCT_DECODE, FT.JPX_DECODE))
            or (invert_color and img.mode == "L")
        )
        else None,
    )
    if (
        isinstance(color_space, ArrayObject)
        and color_space[0].get_object() == "/Indexed"
    ):
        decode = None  # decode is meaningless if Indexed
    if (
        isinstance(color_space, ArrayObject)
        and color_space[0].get_object() == "/Separation"
    ):
        decode = [1.0, 0.0] * len(img.getbands())
    if decode is not None and not all(decode[i] == i % 2 for i in range(len(decode))):
        lut: List[int] = []
        for i in range(0, len(decode), 2):
            dmin = decode[i]
            dmax = decode[i + 1]
            lut.extend(
                round(255.0 * (j / 255.0 * (dmax - dmin) + dmin)) for j in range(256)
            )
        img = img.point(lut)
    return img


def _get_mode_and_invert_color(
    x_object_obj: Dict[str, Any], colors: int, color_space: Union[str, List[Any], Any]
) -> Tuple[mode_str_type, bool]:
    if (
        IA.COLOR_SPACE in x_object_obj
        and x_object_obj[IA.COLOR_SPACE] == ColorSpaces.DEVICE_RGB
    ):
        # https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes
        mode: mode_str_type = "RGB"
    if x_object_obj.get("/BitsPerComponent", 8) < 8:
        mode, invert_color = _get_imagemode(
            f"{x_object_obj.get('/BitsPerComponent', 8)}bit", 0, ""
        )
    else:
        mode, invert_color = _get_imagemode(
            color_space,
            2
            if (
                colors == 1
                and (
                    not isinstance(color_space, NullObject)
                    and "Gray" not in color_space
                )
            )
            else colors,
            "",
        )
    return mode, invert_color
