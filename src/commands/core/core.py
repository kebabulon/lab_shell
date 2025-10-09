import os
import stat
from pwd import getpwuid
from grp import getgrgid

from datetime import datetime
from typing import NamedTuple

from argparse import ArgumentParser
from src.command import command, CommandEnv

from src.path import pretty_path


class TableRow(NamedTuple):
    permissions: str
    user: str
    group: str
    size: str
    modification_time: str
    name: str


@command(
    name="ls",
    description="list all files in directory",
    help="""
        -l - list files in table format
    """
)
def ls(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('dir', nargs='?', default=env.cwd)
    parser.add_argument('-l', action='store_true')
    argv = parser.parse_args(args)

    dir_path = env.get_path(argv.dir)

    if not os.path.isdir(dir_path):
        raise FileNotFoundError(f"No such file or dir {pretty_path(dir_path)}")

    if not argv.l:
        env.print(" ".join(os.listdir(dir_path)))
    else:
        table: list[TableRow] = []

        max_user_len = 0
        max_group_len = 0
        max_size_len = 0

        for file in os.scandir(dir_path):
            file_stat = file.stat(follow_symlinks=True)

            row = TableRow(
                permissions=stat.filemode(file_stat.st_mode),
                user=getpwuid(file_stat.st_uid).pw_name,
                group=getgrgid(file_stat.st_gid).gr_name,
                size=str(file_stat.st_size),
                modification_time=datetime.utcfromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                name=file.name,
            )
            table.append(row)

            max_user_len = max(max_user_len, len(row.user))
            max_group_len = max(max_group_len, len(row.group))
            max_size_len = max(max_size_len, len(row.size))

        for row in table:
            env.print(f"{row.permissions} {row.user:<{max_user_len}} {row.group:<{max_group_len}} {row.size:<{max_size_len}} {row.modification_time} {row.name}")


@command(
    name="cd",
    description="change current directory"
)
def cd(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('dir', nargs='?', default='~')
    argv = parser.parse_args(args)

    dir_path = env.get_path(argv.dir)

    if not os.path.isdir(dir_path):
        raise FileNotFoundError(f"No such file or dir {pretty_path(dir_path)}")

    env.cwd = dir_path
