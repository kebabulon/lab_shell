import os
import shutil
import shlex

from textwrap import indent, dedent

from argparse import ArgumentParser
from src.command import command, CommandEnv

from src.constants import TRASH_DIR
from src.constants import UNDO_HISTORY_PATH
from src.constants import COMMAND_HISTORY_PATH


def remove_directory_if_empty(path: str) -> None:
    if not os.listdir(path):
        os.rmdir(path)


def move_and_overwrite(source: str, dest: str) -> None:
    if os.path.isfile(source):
        shutil.copy2(source, dest)
        os.remove(source)

    elif os.path.isdir(source):
        shutil.copytree(source, dest, dirs_exist_ok=True)
        shutil.rmtree(source)


@command(
    name="undo",
    description="undo last cp, mv, rm command"
)
def cmd_undo(env: CommandEnv, args: list[str]) -> None:
    if not os.path.exists(UNDO_HISTORY_PATH):
        lines = []
    else:
        with open(UNDO_HISTORY_PATH, 'r') as f:
            lines = f.readlines()

    if not lines:
        env.print("No more commands to undo!")
        env.log_success("No commands to undo. Done nothing")
        return

    undo_count = len(lines)
    undo_prefix = f"{undo_count}_"

    undo_args = shlex.split(lines.pop())

    match undo_args.pop(0):
        case 'cp':
            dest_path = undo_args.pop(0)
            files_to_remove = undo_args

            if os.path.isfile(dest_path):
                os.remove(dest_path)
            else:
                for file in files_to_remove:
                    os.remove(file)
                    remove_directory_if_empty(os.path.dirname(file))

            overwritten_name = undo_prefix + os.path.basename(dest_path)
            overwritten_path = os.path.join(TRASH_DIR, overwritten_name)

            if os.path.exists(overwritten_path):
                move_and_overwrite(overwritten_path, dest_path)

            env.log_success(f"Successfully undone cp {dest_path}")
        case 'mv':
            source_path = undo_args.pop(0)

            dest_path = undo_args.pop(0)
            files_to_move = undo_args

            if os.path.isfile(dest_path):
                shutil.move(dest_path, source_path)

            elif os.path.isdir(dest_path):
                if files_to_move:
                    for file in files_to_move:
                        rel_source_file_path = os.path.relpath(file, dest_path)
                        source_file_path = os.path.join(source_path, rel_source_file_path)

                        os.makedirs(os.path.dirname(source_file_path), exist_ok=True)

                        shutil.move(file, source_file_path)
                        remove_directory_if_empty(os.path.dirname(file))
                else:  # no files_to_move, that means that directory just got renamed
                    shutil.move(dest_path, source_path)

            overwritten_name = undo_prefix + os.path.basename(dest_path)
            overwritten_path = os.path.join(TRASH_DIR, overwritten_name)

            if os.path.exists(overwritten_path):
                move_and_overwrite(overwritten_path, dest_path)

            env.log_success(f"Successfully undone mv {source_path} {dest_path}")
        case 'rm':
            source_path = undo_args.pop(0)

            removed_name = undo_prefix + os.path.basename(source_path)
            removed_path = os.path.join(TRASH_DIR, removed_name)

            shutil.move(removed_path, source_path)

    with open(UNDO_HISTORY_PATH, 'w') as f:
        f.writelines(lines)


@command(
    name="history",
    description="print N last commands",
    help="""
        n - amount number of last commands to print
    """
)
def cmd_history(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('n', type=int, nargs='?', default=10)
    argv = parser.parse_args(args)

    if argv.n <= 0:
        raise ValueError("n must be a natural number")

    if not os.path.exists(COMMAND_HISTORY_PATH):
        lines = []
    else:
        with open(COMMAND_HISTORY_PATH, 'r') as f:
            lines = f.readlines()

    max_number = len(str(len(lines) - 1))

    last_commands = ""
    for i in range(max(0, len(lines) - argv.n), len(lines) - 1):  # len(lines) - 1 because the last command is history
        last_commands += f" {i + 1:<{max_number}} {lines[i]}"
    last_commands = last_commands.rstrip('\n')

    env.print(last_commands)

    env.log_success()


@command(
    name="help",
    description="print help message for a given command",
    help="""
        command - name of a command to print help for
    """
)
def cmd_help(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('command', nargs='?', default="help")
    argv = parser.parse_args(args)

    if argv.command not in env.commands:
        raise NameError(f"No such command {argv.command}")
    command = env.commands[argv.command]

    env.print()
    env.print(f"{command.name} - {command.description}")
    env.print(indent(dedent(command.help), "  "))

    env.log_success()
