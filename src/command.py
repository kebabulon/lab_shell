from __future__ import annotations

import os
import logging

import inspect
import pkgutil
import importlib

from collections.abc import Callable
from types import ModuleType

from src.commands import core, plugins


class CommandEnv():
    def __init__(self, log_filename: str, cwd: str):
        self.commands: dict[str, Command] = {}
        self.cwd = cwd
        self.command_output = ""

        self.setup_logger(log_filename)

        self.load_commands_from_namespace(core)
        self.load_commands_from_namespace(plugins)

    def get_path(self, path: str) -> str:
        path = os.path.expanduser(path)

        if not os.path.isabs(path):
            path = os.path.join(self.cwd, path)

        return os.path.normpath(path)

    def print(self, message: str):
        print(message)
        self.command_output += message + '\n'

    def setup_logger(self, log_filename: str):
        self.logger = logging.getLogger(log_filename)
        self.logger.setLevel(logging.INFO)

        if not self.logger.hasHandlers():
            file_handler = logging.FileHandler(
                f"{log_filename}.log",
                mode="a",
                encoding="utf-8"
            )
            formatter = logging.Formatter(
                "[{asctime}] {message}",
                style="{",
                datefmt="%Y-%m-%d %H:%M",
            )
            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)

    def log_success(self, message: str = "Success"):
        self.logger.info(message)

    def log_and_raise_exception(self, exception: Exception):
        message = f"Error: {str(exception)}"
        self.command_output += message + '\n'
        self.logger.error(message)
        raise exception

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
