import os
import shutil

from argparse import ArgumentParser
from src.command import command, CommandEnv, Command


def archive_command(format: str) -> Command:
    @command(
        name=format,
        description=f"create {format} archive of directory",
        help=f"""
            source - directory to {format}
            dest - destination of {format} archived directory
        """
    )
    def cmd_archive(env: CommandEnv, args: list[str]) -> None:
        parser = ArgumentParser(exit_on_error=False)
        parser.add_argument('source')
        parser.add_argument('dest', nargs='?')
        argv = parser.parse_args(args)

        source_path = env.get_path(argv.source)
        if not os.path.isdir(source_path):
            raise NotADirectoryError(f"Not a directory {source_path}")

        if not argv.dest:
            dest_path = source_path
        else:
            dest_path = env.get_path(argv.dest)

        dest_path_with_format = dest_path + '.' + format
        if os.path.exists(dest_path_with_format):
            raise FileExistsError(f"Destination exists {dest_path_with_format}")

        try:
            shutil.make_archive(
                base_name=dest_path,
                format=format,
                root_dir=source_path
            )
        except PermissionError:
            raise PermissionError("No permission")

        env.log_success(f"Successfully {format} archived {source_path} to {dest_path_with_format}")

    return cmd_archive


cmd_zip = archive_command('zip')
cmd_tar = archive_command('tar')


def extract_command(format: str) -> Command:
    @command(
        name=f"un{format}",
        description=f"un{format} archive",
        help=f"""
            source - file to un{format}
        """
    )
    def cmd_extract(env: CommandEnv, args: list[str]) -> None:
        parser = ArgumentParser(exit_on_error=False)
        parser.add_argument('source')
        argv = parser.parse_args(args)

        source_path = env.get_path(argv.source)
        if not os.path.isfile(source_path):
            raise IsADirectoryError(f"Not a file {source_path}")

        try:
            shutil.unpack_archive(
                filename=source_path,
                extract_dir=env.cwd
            )
        except PermissionError:
            raise PermissionError("No permission")
        # TODO: maybe add more exceptions here? shutil.ReadError

    return cmd_extract


cmd_unzip = extract_command('zip')
cmd_untar = extract_command('tar')
