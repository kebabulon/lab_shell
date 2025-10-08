import os
from datetime import datetime

from argparse import ArgumentParser
from src.command import command, CommandEnv


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

    listdir_itterator = os.listdir(dir_path)

    if not argv.l:
        print(*listdir_itterator)  # TODO: logging lol
    else:
        for file in listdir_itterator:
            file_stat = os.stat(file)
            modification_time = datetime.utcfromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            # TODO: create array, then create a table string out of it with proper spacing
            print(file_stat.st_size, modification_time, file)


# print(ls)
# print(type(ls))
