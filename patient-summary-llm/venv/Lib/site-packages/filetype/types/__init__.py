# -*- coding: utf-8 -*-

from __future__ import absolute_import

from . import archive
from . import audio
from . import application
from . import document
from . import font
from . import image
from . import video
from .base import Type  # noqa

# Supported image types
IMAGE = (
    image.Dwg(),
    image.Xcf(),
    image.Jpeg(),
    image.Jpx(),
    image.Apng(),
    image.Png(),
    image.Gif(),
    image.Webp(),
    image.Tiff(),
    image.Cr2(),
    image.Bmp(),
    image.Jxr(),
    image.Psd(),
    image.Ico(),
    image.Heic(),
    image.Dcm(),
    image.Avif(),
)

# Supported video types
VIDEO = (
    video.M3gp(),
    video.Mp4(),
    video.M4v(),
    video.Mkv(),
    video.Mov(),
    video.Avi(),
    video.Wmv(),
    video.Mpeg(),
    video.Webm(),
    video.Flv(),
)

# Supported audio types
AUDIO = (
    audio.Aac(),
    audio.Midi(),
    audio.Mp3(),
    audio.M4a(),
    audio.Ogg(),
    audio.Flac(),
    audio.Wav(),
    audio.Amr(),
    audio.Aiff(),
)

# Supported font types
FONT = (font.Woff(), font.Woff2(), font.Ttf(), font.Otf())

# Supported archive container types
ARCHIVE = (
    archive.Br(),
    archive.Rpm(),
    archive.Dcm(),
    archive.Epub(),
    archive.Zip(),
    archive.Tar(),
    archive.Rar(),
    archive.Gz(),
    archive.Bz2(),
    archive.SevenZ(),
    archive.Pdf(),
    archive.Exe(),
    archive.Swf(),
    archive.Rtf(),
    archive.Nes(),
    archive.Crx(),
    archive.Cab(),
    archive.Eot(),
    archive.Ps(),
    archive.Xz(),
    archive.Sqlite(),
    archive.Deb(),
    archive.Ar(),
    archive.Z(),
    archive.Lzop(),
    archive.Lz(),
    archive.Elf(),
    archive.Lz4(),
    archive.Zstd(),
)

# Supported archive container types
APPLICATION = (
    application.Wasm(),
)

# Supported document types
DOCUMENT = (
    document.Doc(),
    document.Docx(),
    document.Odt(),
    document.Xls(),
    document.Xlsx(),
    document.Ods(),
    document.Ppt(),
    document.Pptx(),
    document.Odp(),
)


# Expose supported type matchers
TYPES = list(IMAGE + AUDIO + VIDEO + FONT + DOCUMENT + ARCHIVE + APPLICATION)
