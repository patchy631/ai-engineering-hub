# -*- coding: utf-8 -*-


class Type(object):
    """
    Represents the file type object inherited by
    specific file type matchers.
    Provides convenient accessor and helper methods.
    """
    def __init__(self, mime, extension):
        self.__mime = mime
        self.__extension = extension

    @property
    def mime(self):
        return self.__mime

    @property
    def extension(self):
        return self.__extension

    def is_extension(self, extension):
        return self.__extension is extension

    def is_mime(self, mime):
        return self.__mime is mime

    def match(self, buf):
        raise NotImplementedError
