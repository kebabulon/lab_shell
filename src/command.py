from __future__ import annotations

import os

import inspect
import pkgutil
import importlib

from collections.abc import Callable
from types import ModuleType

from src.commands import core, custom


class CommandEnv():
    def __init__(self, cwd: str = os.getcwd()):
        self.commands: dict[str, Command] = {}
        self.cwd = cwd

        self.load_commands_from_namespace(core)
        self.load_commands_from_namespace(custom)

        print(self.commands)

    def pretty_path(self, path: str) -> str:
        path = path.replace(os.path.expanduser('~'), '~', 1)
        return path

    def get_path(self, path: str) -> str:
        path = os.path.expanduser(path)

        if os.path.isabs(path):
            return path
        else:
            new_path = os.path.normpath(os.path.join(self.cwd, os.pardir))
            return new_path

    def load_command(self, command_class: Command):
        self.commands[command_class.name] = command_class

    def load_commands_from_module(self, module: ModuleType):
        for name, command_class in inspect.getmembers(module, lambda x: type(x) is Command):
            self.load_command(command_class)

    def load_commands_from_namespace(self, namespace: ModuleType):
        for module_info in pkgutil.iter_modules(namespace.__path__):
            imported_module = importlib.import_module(f"{namespace.__name__}.{module_info.name}")
            self.load_commands_from_module(imported_module)


CommandType = Callable[[CommandEnv, list[str]], None]


class Command:
    def __init__(self, function: CommandType, name: str, description: str = "", help: str = ""):
        self.function = function

        self.name = name
        self.description = description
        self.help = help

    def __call__(self, *args, **kwargs):
        self.function(*args, **kwargs)


def command(name: str, description: str = "", help: str = "") -> Callable[[CommandType], Command]:
    def decorator(function: CommandType) -> Command:
        return Command(
            function=function,
            name=name,
            description=description,
            help=help
        )

    return decorator
