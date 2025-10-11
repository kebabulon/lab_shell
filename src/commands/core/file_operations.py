import os
import shutil

from argparse import ArgumentParser
from src.command import command, CommandEnv
from src.path import validate_path


@command(
    name="cp",
    description="copy file/directory",
    help="""
        source - file/directory to copy
        dest - destination to copy file/directory to

        -r - recursively copy the contents of the directory
    """
)
def cmd_cp(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('source')
    parser.add_argument('dest')
    parser.add_argument('-r', action='store_true')
    argv = parser.parse_args(args)

    source_path = env.get_path(argv.source)
    validate_path(source_path)

    dest_path = env.get_path(argv.dest)

    log_dest_path = dest_path
    if os.path.isdir(dest_path):
        log_dest_path = os.path.join(dest_path, os.path.basename(source_path))

    if os.path.isfile(source_path):
        try:
            shutil.copy2(source_path, dest_path)
        except PermissionError:
            raise PermissionError("No permission")

    elif os.path.isdir(source_path):
        if not argv.r:
            raise IsADirectoryError("Unable to copy directory without '-r' flag present")

        try:
            shutil.copytree(source_path, dest_path)
        except PermissionError:
            raise PermissionError("No permission")
        except FileExistsError:
            raise FileExistsError(f"Destination is a file {dest_path}")

    env.log_success(f"Successfully copied {source_path} to {log_dest_path}")


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

    log_dest_path = dest_path
    if os.path.isdir(dest_path):
        log_dest_path = os.path.join(dest_path, os.path.basename(source_path))

    try:
        shutil.move(source_path, dest_path)
    except PermissionError:
        raise PermissionError("No permission")
    except FileExistsError:
        raise FileExistsError(f"Destination is a file {dest_path}")

    env.log_success(f"Successfully moved {source_path} to {log_dest_path}")
