import sys

import filetype


def guess(path):
    kind = filetype.guess(path)
    if kind is None:
        print('{}: File type determination failure.'.format(path))
    else:
        print('{}: {} ({})'.format(path, kind.extension, kind.mime))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog='filetype', description='Determine type of FILEs.'
    )
    parser.add_argument('-f', '--file', nargs='+')
    parser.add_argument(
        '-v', '--version', action='version',
        version='%(prog)s ' + filetype.version,
        help='output version information and exit'
    )

    args = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    for i in args.file:
        guess(i)


if __name__ == '__main__':
    main()
