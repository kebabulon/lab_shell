import os
import stat
from pwd import getpwuid
from grp import getgrgid

import datetime
from typing import NamedTuple

from src.path import tree

from argparse import ArgumentParser
from src.command import command, CommandEnv
from src.path import validate_path


class TableRow(NamedTuple):
    permissions: str
    user: str
    group: str
    size: str
    modification_time: str
    name: str


def local_timezone() -> datetime.tzinfo | None:
    now = datetime.datetime.now()
    local_now = now.astimezone()
    return local_now.tzinfo


def is_hidden(path: str) -> bool:
    if path[0] == '.':
        return True
    return False


@command(
    name="ls",
    description="list all files in directory",
    help="""
        path - path to list files in

        -l - list files in table format
    """
)
def cmd_ls(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('path', nargs='?', default=env.cwd)
    parser.add_argument('-l', action='store_true')
    argv = parser.parse_args(args)

    dir_path = env.get_path(argv.path)
    validate_path(dir_path)

    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"Not a directory {dir_path}")

    if not argv.l:
        env.print(" ".join([file for file in os.listdir(dir_path) if not is_hidden(file)]))
    else:
        table: list[TableRow] = []

        max_user_len = 0
        max_group_len = 0
        max_size_len = 0

        for file in os.scandir(dir_path):
            if is_hidden(file.name):
                continue

            file_stat = file.stat(follow_symlinks=True)

            row = TableRow(
                permissions=stat.filemode(file_stat.st_mode),
                user=getpwuid(file_stat.st_uid).pw_name,
                group=getgrgid(file_stat.st_gid).gr_name,
                size=str(file_stat.st_size),
                modification_time=datetime.datetime.fromtimestamp(file_stat.st_mtime, local_timezone()).strftime('%Y-%m-%d %H:%M:%S'),
                name=file.name,
            )
            table.append(row)

            max_user_len = max(max_user_len, len(row.user))
            max_group_len = max(max_group_len, len(row.group))
            max_size_len = max(max_size_len, len(row.size))

        for row in table:
            env.print(f"{row.permissions} {row.user:<{max_user_len}} {row.group:<{max_group_len}} {row.size:<{max_size_len}} {row.modification_time} {row.name}")

    env.log_success()


@command(
    name="cd",
    description="change current directory",
    help="""
        path - path to change current directory to
    """
)
def cmd_cd(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('path', nargs='?', default='~')
    argv = parser.parse_args(args)

    dir_path = env.get_path(argv.path)
    validate_path(dir_path)

    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"Not a directory {dir_path}")

    env.cwd = dir_path

    env.log_success()


@command(
    name="cat",
    description="print contents of file",
    help="""
        file - file to print contents of
    """
)
def cmd_cat(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('file')
    argv = parser.parse_args(args)

    file_path = env.get_path(argv.file)
    validate_path(file_path)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Not a file {file_path}")

    try:
        with open(file_path, 'r') as f:
            contents = f.read()
            contents = contents.rstrip('\n')
            env.print(contents)
    except UnicodeDecodeError:  # binary file
        raise ValueError("Not a text file or a non-unicode encoding")
    except PermissionError:
        raise PermissionError("No permission")

    env.log_success()


@command(
    name="tree",
    description="print directory as a sorted tree",
    help="""
        path - path to print tree of
    """
)
def cmd_tree(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('path', nargs='?', default=env.cwd)
    parser.add_argument('-l', action='store_true')
    argv = parser.parse_args(args)

    dir_path = env.get_path(argv.path)
    validate_path(dir_path)

    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"Not a directory {dir_path}")

    tree_result = tree(dir_path)
    env.print(tree_result)

    env.log_success()
