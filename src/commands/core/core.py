import os

from argparse import ArgumentParser
from src.command import command


@command(
    name="ls",
    description="list all files in directory",
    help="""
        -l - list files in table format
    """
)
def ls(cwd: str, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('filename', nargs='?', default=cwd)
    parser.add_argument('-l', action='store_true')
    argv = parser.parse_args(args)

    if not argv.l:
        print(*os.listdir(argv.filename))


# print(ls)
# print(type(ls))
