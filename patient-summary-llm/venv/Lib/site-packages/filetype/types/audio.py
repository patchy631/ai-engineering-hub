# -*- coding: utf-8 -*-

from __future__ import absolute_import

from .base import Type


class Midi(Type):
    """
    Implements the Midi audio type matcher.
    """
    MIME = 'audio/midi'
    EXTENSION = 'midi'

    def __init__(self):
        super(Midi, self).__init__(
            mime=Midi.MIME,
            extension=Midi.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 3 and
                buf[0] == 0x4D and
                buf[1] == 0x54 and
                buf[2] == 0x68 and
                buf[3] == 0x64)


class Mp3(Type):
    """
    Implements the MP3 audio type matcher.
    """
    MIME = 'audio/mpeg'
    EXTENSION = 'mp3'

    def __init__(self):
        super(Mp3, self).__init__(
            mime=Mp3.MIME,
            extension=Mp3.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 2 and
                ((buf[0] == 0x49 and
                  buf[1] == 0x44 and
                  buf[2] == 0x33) or
                 (buf[0] == 0xFF and
                  buf[1] == 0xF2) or
                 (buf[0] == 0xFF and
                  buf[1] == 0xF3) or
                 (buf[0] == 0xFF and
                  buf[1] == 0xFB)))


class M4a(Type):
    """
    Implements the M4A audio type matcher.
    """
    MIME = 'audio/mp4'
    EXTENSION = 'm4a'

    def __init__(self):
        super(M4a, self).__init__(
            mime=M4a.MIME,
            extension=M4a.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 10 and
                ((buf[4] == 0x66 and
                    buf[5] == 0x74 and
                    buf[6] == 0x79 and
                    buf[7] == 0x70 and
                    buf[8] == 0x4D and
                    buf[9] == 0x34 and
                    buf[10] == 0x41) or
                (buf[0] == 0x4D and
                    buf[1] == 0x34 and
                    buf[2] == 0x41 and
                    buf[3] == 0x20)))


class Ogg(Type):
    """
    Implements the OGG audio type matcher.
    """
    MIME = 'audio/ogg'
    EXTENSION = 'ogg'

    def __init__(self):
        super(Ogg, self).__init__(
            mime=Ogg.MIME,
            extension=Ogg.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 3 and
                buf[0] == 0x4F and
                buf[1] == 0x67 and
                buf[2] == 0x67 and
                buf[3] == 0x53)


class Flac(Type):
    """
    Implements the FLAC audio type matcher.
    """
    MIME = 'audio/x-flac'
    EXTENSION = 'flac'

    def __init__(self):
        super(Flac, self).__init__(
            mime=Flac.MIME,
            extension=Flac.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 3 and
                buf[0] == 0x66 and
                buf[1] == 0x4C and
                buf[2] == 0x61 and
                buf[3] == 0x43)


class Wav(Type):
    """
    Implements the WAV audio type matcher.
    """
    MIME = 'audio/x-wav'
    EXTENSION = 'wav'

    def __init__(self):
        super(Wav, self).__init__(
            mime=Wav.MIME,
            extension=Wav.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 11 and
                buf[0] == 0x52 and
                buf[1] == 0x49 and
                buf[2] == 0x46 and
                buf[3] == 0x46 and
                buf[8] == 0x57 and
                buf[9] == 0x41 and
                buf[10] == 0x56 and
                buf[11] == 0x45)


class Amr(Type):
    """
    Implements the AMR audio type matcher.
    """
    MIME = 'audio/amr'
    EXTENSION = 'amr'

    def __init__(self):
        super(Amr, self).__init__(
            mime=Amr.MIME,
            extension=Amr.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 11 and
                buf[0] == 0x23 and
                buf[1] == 0x21 and
                buf[2] == 0x41 and
                buf[3] == 0x4D and
                buf[4] == 0x52 and
                buf[5] == 0x0A)


class Aac(Type):
    """Implements the Aac audio type matcher."""

    MIME = 'audio/aac'
    EXTENSION = 'aac'

    def __init__(self):
        super(Aac, self).__init__(
            mime=Aac.MIME,
            extension=Aac.EXTENSION
        )

    def match(self, buf):
        return (buf[:2] == bytearray([0xff, 0xf1]) or
                buf[:2] == bytearray([0xff, 0xf9]))


class Aiff(Type):
    """
    Implements the AIFF audio type matcher.
    """
    MIME = 'audio/x-aiff'
    EXTENSION = 'aiff'

    def __init__(self):
        super(Aiff, self).__init__(
            mime=Aiff.MIME,
            extension=Aiff.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 11 and
                buf[0] == 0x46 and
                buf[1] == 0x4F and
                buf[2] == 0x52 and
                buf[3] == 0x4D and
                buf[8] == 0x41 and
                buf[9] == 0x49 and
                buf[10] == 0x46 and
                buf[11] == 0x46)
