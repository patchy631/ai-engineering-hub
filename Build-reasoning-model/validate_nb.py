import nbformat
from nbformat import ValidationError
from pathlib import Path

for p in Path('.').rglob('*.ipynb'):
    nb = nbformat.read(str(p), as_version=4)
    try:
        nbformat.validate(nb)
        print('VALID ->', p)
    except ValidationError as e:
        print('INVALID ->', p, e)
