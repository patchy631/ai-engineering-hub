from __future__ import annotations

from typing import TYPE_CHECKING, Generator, Optional, cast

from pypdf._utils import parse_iso8824_date
from pypdf.constants import FileSpecificationDictionaryEntries
from pypdf.errors import PdfReadError
from pypdf.generic import ArrayObject, DictionaryObject, StreamObject

if TYPE_CHECKING:
    import datetime


class EmbeddedFile:
    """
    Container holding the information on an embedded file.

    Attributes are evaluated lazily if possible.

    Further information on embedded files can be found in section 7.11 of the PDF 2.0 specification.
    """
    def __init__(self, name: str, pdf_object: DictionaryObject) -> None:
        """
        Args:
            name: The (primary) name as provided in the name tree.
            pdf_object: The corresponding PDF object to allow retrieving further data.
        """
        self.name = name
        self.pdf_object = pdf_object

    @property
    def alternative_name(self) -> Optional[str]:
        """Retrieve the alternative name (file specification)."""
        for key in [FileSpecificationDictionaryEntries.UF, FileSpecificationDictionaryEntries.F]:
            # PDF 2.0 reference, table 43:
            #   > A PDF reader shall use the value of the UF key, when present, instead of the F key.
            if key in self.pdf_object:
                return cast(str, self.pdf_object[key].get_object())
        return None

    @property
    def description(self) -> Optional[str]:
        """Retrieve the description."""
        return self.pdf_object.get(FileSpecificationDictionaryEntries.DESC)

    @property
    def associated_file_relationship(self) -> str:
        """Retrieve the relationship of the referring document to this embedded file."""
        return self.pdf_object.get("/AFRelationship", "/Unspecified")

    @property
    def _embedded_file(self) -> StreamObject:
        """Retrieve the actual embedded file stream."""
        if "/EF" not in self.pdf_object:
            raise PdfReadError(f"/EF entry not found: {self.pdf_object}")
        ef = cast(DictionaryObject, self.pdf_object["/EF"])
        for key in [FileSpecificationDictionaryEntries.UF, FileSpecificationDictionaryEntries.F]:
            if key in ef:
                return cast(StreamObject, ef[key].get_object())
        raise PdfReadError(f"No /(U)F key found in file dictionary: {ef}")

    @property
    def _params(self) -> DictionaryObject:
        """Retrieve the file-specific parameters."""
        return self._embedded_file.get("/Params", DictionaryObject()).get_object()

    @property
    def subtype(self) -> Optional[str]:
        """Retrieve the subtype. This is a MIME media type, prefixed by a slash."""
        return self._embedded_file.get("/Subtype")

    @property
    def content(self) -> bytes:
        """Retrieve the actual file content."""
        return self._embedded_file.get_data()

    @property
    def size(self) -> Optional[int]:
        """Retrieve the size of the uncompressed file in bytes."""
        return self._params.get("/Size")

    @property
    def creation_date(self) -> Optional[datetime.datetime]:
        """Retrieve the file creation datetime."""
        return parse_iso8824_date(self._params.get("/CreationDate"))

    @property
    def modification_date(self) -> Optional[datetime.datetime]:
        """Retrieve the datetime of the last file modification."""
        return parse_iso8824_date(self._params.get("/ModDate"))

    @property
    def checksum(self) -> Optional[bytes]:
        """Retrieve the MD5 checksum of the (uncompressed) file."""
        return self._params.get("/CheckSum")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"

    @classmethod
    def _load_from_names(cls, names: ArrayObject) -> Generator[EmbeddedFile, None, None]:
        """
        Convert the given name tree into class instances.

        Args:
            names: The name tree to load the data from.

        Returns:
            Iterable of class instances for the files found.
        """
        # This is a name tree of the format [name_1, reference_1, name_2, reference_2, ...]
        for i, name in enumerate(names):
            if not isinstance(name, str):
                # Skip plain strings and retrieve them as `direct_name` by index.
                file_dictionary = name.get_object()
                direct_name = names[i - 1].get_object()
                yield EmbeddedFile(name=direct_name, pdf_object=file_dictionary)

    @classmethod
    def _load(cls, catalog: DictionaryObject) -> Generator[EmbeddedFile, None, None]:
        """
        Load the embedded files for the given document catalog.

        This method and its signature are considered internal API and thus not exposed publicly for now.

        Args:
            catalog: The document catalog to load from.

        Returns:
            Iterable of class instances for the files found.
        """
        try:
            container = cast(
                DictionaryObject,
                cast(DictionaryObject, catalog["/Names"])["/EmbeddedFiles"],
            )
        except KeyError:
            return

        if "/Kids" in container:
            for kid in cast(ArrayObject, container["/Kids"].get_object()):
                # There might be further (nested) kids here.
                # Wait for an example before evaluating an implementation.
                kid = kid.get_object()
                if "/Names" in kid:
                    yield from cls._load_from_names(cast(ArrayObject, kid["/Names"]))
        if "/Names" in container:
            yield from cls._load_from_names(cast(ArrayObject, container["/Names"]))
