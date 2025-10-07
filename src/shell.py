import os

import shlex

from types import ModuleType

import inspect
import pkgutil
import importlib
from src.commands import core, custom

# from src.command import CommandType
from src.command import Command


def prettify_path(path: str) -> str:
    path = path.replace(os.path.expanduser('~'), '~', 1)
    return path


class ShellEnv():
    def __init__(self, cwd: str = os.getcwd()):
        self.commands: dict[str, Command] = {}
        self.cwd = cwd

        self.load_commands_from_namespace(core)
        self.load_commands_from_namespace(custom)

        print(self.commands)

    def load_command(self, command_class: Command):
        self.commands[command_class.name] = command_class

    def load_commands_from_module(self, module: ModuleType):
        for name, command_class in inspect.getmembers(module, lambda x: type(x) is Command):
            self.load_command(command_class)

    def load_commands_from_namespace(self, namespace: ModuleType):
        for module_info in pkgutil.iter_modules(namespace.__path__):
            imported_module = importlib.import_module(f"{namespace.__name__}.{module_info.name}")
            self.load_commands_from_module(imported_module)


class Shell():
    def __init__(self):
        self.env = ShellEnv()

    def get_prompt(self) -> str:
        return f"<{self.env.cwd}> => "

    def execute(self, cmd: str) -> None:
        cmd_args = shlex.split(cmd)
        if not cmd_args:
            return

        command_function = self.env.commands.get(cmd_args[0])
        if not command_function:
            print("error")  # TODO: logging + actual printing
            return

        command_function(cmd_args[1:])

    def run(self) -> None:
        while cmd := input(self.get_prompt()):
            try:
                self.execute(cmd)
            except KeyboardInterrupt:
                continue
