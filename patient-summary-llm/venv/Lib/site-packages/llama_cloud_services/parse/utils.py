from enum import Enum

# Asyncio error messages
nest_asyncio_err = "cannot be called from a running event loop"
nest_asyncio_msg = "The event loop is already running. Add `import nest_asyncio; nest_asyncio.apply()` to your code to fix this issue."


class ResultType(str, Enum):
    """The result type for the parser."""

    TXT = "text"
    MD = "markdown"
    JSON = "json"
    STRUCTURED = "structured"


class ParsingMode(str, Enum):
    """The parsing mode for the parser."""

    parse_page_without_llm = "parse_page_without_llm"
    parse_page_with_llm = "parse_page_with_llm"
    parse_page_with_lvm = "parse_page_with_lvm"
    parse_page_with_agent = "parse_page_with_agent"
    parse_document_with_llm = "parse_document_with_llm"


class Language(str, Enum):
    BAZA = "abq"
    ADYGHE = "ady"
    AFRIKAANS = "af"
    ANGIKA = "ang"
    ARABIC = "ar"
    ASSAMESE = "as"
    AVAR = "ava"
    AZERBAIJANI = "az"
    BELARUSIAN = "be"
    BULGARIAN = "bg"
    BIHARI = "bh"
    BHOJPURI = "bho"
    BENGALI = "bn"
    BOSNIAN = "bs"
    SIMPLIFIED_CHINESE = "ch_sim"
    TRADITIONAL_CHINESE = "ch_tra"
    CHECHEN = "che"
    CZECH = "cs"
    WELSH = "cy"
    DANISH = "da"
    DARGWA = "dar"
    GERMAN = "de"
    ENGLISH = "en"
    SPANISH = "es"
    ESTONIAN = "et"
    PERSIAN_FARSI = "fa"
    FRENCH = "fr"
    IRISH = "ga"
    GOAN_KONKANI = "gom"
    HINDI = "hi"
    CROATIAN = "hr"
    HUNGARIAN = "hu"
    INDONESIAN = "id"
    INGUSH = "inh"
    ICELANDIC = "is"
    ITALIAN = "it"
    JAPANESE = "ja"
    KABARDIAN = "kbd"
    KANNADA = "kn"
    KOREAN = "ko"
    KURDISH = "ku"
    LATIN = "la"
    LAK = "lbe"
    LEZGHIAN = "lez"
    LITHUANIAN = "lt"
    LATVIAN = "lv"
    MAGAHI = "mah"
    MAITHILI = "mai"
    MAORI = "mi"
    MONGOLIAN = "mn"
    MARATHI = "mr"
    MALAY = "ms"
    MALTESE = "mt"
    NEPALI = "ne"
    NEWARI = "new"
    DUTCH = "nl"
    NORWEGIAN = "no"
    OCCITAN = "oc"
    PALI = "pi"
    POLISH = "pl"
    PORTUGUESE = "pt"
    ROMANIAN = "ro"
    RUSSIAN = "ru"
    SERBIAN_CYRILLIC = "rs_cyrillic"
    SERBIAN_LATIN = "rs_latin"
    NAGPURI = "sck"
    SLOVAK = "sk"
    SLOVENIAN = "sl"
    ALBANIAN = "sq"
    SWEDISH = "sv"
    SWAHILI = "sw"
    TAMIL = "ta"
    TABASSARAN = "tab"
    TELUGU = "te"
    THAI = "th"
    TAJIK = "tjk"
    TAGALOG = "tl"
    TURKISH = "tr"
    UYGHUR = "ug"
    UKRAINIAN = "uk"
    URDU = "ur"
    UZBEK = "uz"
    VIETNAMESE = "vi"


SUPPORTED_FILE_TYPES = [
    ".pdf",
    # document and presentations
    ".602",
    ".abw",
    ".cgm",
    ".cwk",
    ".doc",
    ".docx",
    ".docm",
    ".dot",
    ".dotm",
    ".hwp",
    ".key",
    ".lwp",
    ".mw",
    ".mcw",
    ".pages",
    ".pbd",
    ".ppt",
    ".pptm",
    ".pptx",
    ".pot",
    ".potm",
    ".potx",
    ".rtf",
    ".sda",
    ".sdd",
    ".sdp",
    ".sdw",
    ".sgl",
    ".sti",
    ".sxi",
    ".sxw",
    ".stw",
    ".sxg",
    ".txt",
    ".uof",
    ".uop",
    ".uot",
    ".vor",
    ".wpd",
    ".wps",
    ".xml",
    ".zabw",
    ".epub",
    # images
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".svg",
    ".tiff",
    ".webp",
    # web
    ".htm",
    ".html",
    # spreadsheets
    ".xlsx",
    ".xls",
    ".xlsm",
    ".xlsb",
    ".xlw",
    ".csv",
    ".dif",
    ".sylk",
    ".slk",
    ".prn",
    ".numbers",
    ".et",
    ".ods",
    ".fods",
    ".uos1",
    ".uos2",
    ".dbf",
    ".wk1",
    ".wk2",
    ".wk3",
    ".wk4",
    ".wks",
    ".123",
    ".wq1",
    ".wq2",
    ".wb1",
    ".wb2",
    ".wb3",
    ".qpw",
    ".xlr",
    ".eth",
    ".tsv",
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".m4a",
    ".wav",
    ".webm",
]
