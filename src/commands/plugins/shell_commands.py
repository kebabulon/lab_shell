import os

from textwrap import indent, dedent

from argparse import ArgumentParser
from src.command import command, CommandEnv

from src.constants import COMMAND_HISTORY_PATH


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
        open(COMMAND_HISTORY_PATH, 'a').close()

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
