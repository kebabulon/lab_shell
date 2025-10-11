import os
import shutil

from argparse import ArgumentParser
from src.command import command, CommandEnv
from src.path import validate_path

from src.constants import ROOT_DIR

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
        raise FileExistsError(f"Destination is a file {log_dest_path}")

    env.log_success(f"Successfully moved {source_path} to {log_dest_path}")


@command(
    name="rm",
    description="move file/directory to trash",
    help="""
        source - file/directory to trash

        -r - recursively move the contents of the directory
        --test - do not perform trashing, only raise exceptions
    """
)
def cmd_rm(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('source')
    parser.add_argument('-r', action='store_true')
    parser.add_argument('--test', action='store_true')
    argv = parser.parse_args(args)

    source_path = env.get_path(argv.source)
    validate_path(source_path)

    if os.path.splitroot(source_path)[2] == '':
        raise PermissionError("Unable to trash root directory")
    if source_path in env.cwd:
        raise PermissionError("Unable to trash parent directory")

    if os.path.isdir(source_path):
        if not argv.r:
            raise IsADirectoryError("Unable to trash directory without '-r' flag present")

        while (confirm_prompt := input("Are you sure you want to trash directory? [y/n] ")) not in ["y", "n"]:
            env.print("Invalid response")

        if confirm_prompt == "n":
            env.log_success("User did not confirm prompt. Done nothing")
            return

    trash_path = os.path.join(ROOT_DIR, ".trash")
    if not os.path.exists(trash_path):
        os.mkdir(trash_path)

    log_dest_path = os.path.join(trash_path, os.path.basename(source_path))

    if not argv.test:
        try:
            shutil.move(source_path, trash_path)
        except PermissionError:
            raise PermissionError("No permission")
        except FileExistsError:
            raise FileExistsError(f"Destination is a file {log_dest_path}")

        env.log_success(f"Successfully moved {source_path} to {log_dest_path}")
    else:
        env.log_success("Test flag present. Done nothing")
