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

    if not os.path.isdir(dir_path):
        raise FileNotFoundError(f"No such file or dir {dir_path}")

    # TODO: check if path is valid before listing
    listdir_itterator = os.listdir(dir_path)

    if not argv.l:
        env.print(" ".join(listdir_itterator))
    else:
        for file in listdir_itterator:
            # TODO: this does not follow symlinks... probably good?
            file_path = os.path.join(dir_path, file)
            file_stat = os.stat(file_path)
            modification_time = datetime.utcfromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            # TODO: create array, then create a table string out of it with proper spacing
            env.print(f"{file_stat.st_size} {modification_time} {file}")
