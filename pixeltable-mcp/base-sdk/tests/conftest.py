import atexit
import os
import shutil
import sys
import tempfile
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Must be set before pixeltable starts, so tests never touch a real database.
# Its postgres outlives the tests and exits by itself once this directory is gone.
_pixeltable_home = tempfile.mkdtemp(prefix="pxt-test-")
os.environ["PIXELTABLE_HOME"] = _pixeltable_home
atexit.register(shutil.rmtree, _pixeltable_home, ignore_errors=True)

# mcp 2.x removed FastMCP. The tool functions are plain Python, so stub the decorator
# to keep them testable; the server itself needs mcp<2 until tools.py is migrated.
try:
    import mcp.server.fastmcp  # noqa: F401
except ImportError:
    _fastmcp = types.ModuleType("mcp.server.fastmcp")
    _fastmcp.FastMCP = lambda name: types.SimpleNamespace(tool=lambda: lambda func: func)
    sys.modules["mcp.server.fastmcp"] = _fastmcp
