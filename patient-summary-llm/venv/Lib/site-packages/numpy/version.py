
"""
Module to expose more detailed version info for the installed `numpy`
"""
version = "2.2.3"
__version__ = version
full_version = version

git_revision = "a27456108104ac11e8564c2f18710997f3a55eb9"
release = 'dev' not in version and '+' not in version
short_version = version.split("+")[0]
