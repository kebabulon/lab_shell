# import os
import shutil

from argparse import ArgumentParser
from src.command import command, CommandEnv
from src.path import validate_path


@command(
    name="mv",
    description="move/rename file/directory",
    help="""
        source - file/directory to move/rename
        dest - destination to move/rename file/directory to
    """
)
def cmd_mv(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('source')
    parser.add_argument('dest')
    argv = parser.parse_args(args)

    source_path = env.get_path(argv.source)
    validate_path(source_path)

    dest_path = env.get_path(argv.dest)

    try:
        shutil.move(source_path, dest_path)
    except PermissionError:
        raise PermissionError("No permission")

    # TODO: log here
