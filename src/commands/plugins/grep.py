import os

import re

from argparse import ArgumentParser
from src.command import command, CommandEnv
from src.path import validate_path

from src.constants import GREP_MATCH_PADDING


def find_patterns_in_file(pattern: str, file: str, ignore_case: bool) -> str:
    found = ""
    line_count = 0

    flag = re.NOFLAG
    if ignore_case:
        flag = re.IGNORECASE

    try:
        with open(file, 'r') as f:
            for line in f:
                line_count += 1
                line = line.rstrip('\n')
                for match in re.finditer(pattern, line, flag):
                    left_pad = line[max(0, match.start(0) - GREP_MATCH_PADDING):match.start(0)]
                    if match.start(0) - GREP_MATCH_PADDING > 0:
                        left_pad = '...' + left_pad

                    right_pad = line[match.end(0):min(match.end(0) + GREP_MATCH_PADDING, len(line))]
                    if match.end(0) + GREP_MATCH_PADDING < len(line):
                        right_pad = right_pad + '...'

                    match_str = f'{left_pad}"{match.group(0)}"{right_pad}'

                    found_str = f"{file}:{line_count} -> {match_str}\n"
                    found += found_str
        return found
    except UnicodeDecodeError:  # binary file, skip
        return ""


@command(
    name="grep",
    description="find lines matching pattern in files",
    help="""
        pattern - regex pattern used for searching
        path - file/directory to search in

        -r - recursively search contents of directory
        -i - case insensitive search
    """
)
def cmd_grep(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('pattern')
    parser.add_argument('path')
    parser.add_argument('-r', action='store_true')
    parser.add_argument('-i', action='store_true')
    argv = parser.parse_args(args)

    path = env.get_path(argv.path)
    validate_path(path)

    found = ""

    try:
        if os.path.isfile(path):
            found = find_patterns_in_file(argv.pattern, path, argv.i)
        elif os.path.isdir(path):
            if not argv.r:
                raise IsADirectoryError("Unable to recursively search directory without '-r' flag present")

            for root, dirs, files in os.walk(path):
                for file in files:
                    found += find_patterns_in_file(argv.pattern, os.path.join(root, file), argv.i)
    except PermissionError:
        raise PermissionError("No permission")

    found = found.rstrip('\n')
    if found:
        env.print(found)
        env.log_success()
    else:
        env.log_success("No patterns found")
