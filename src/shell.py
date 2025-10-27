import os
import shlex

from src.path import pretty_path
from src.command import CommandEnv
from src.constants import DEBUG
from src.constants import COMMAND_HISTORY_PATH

from src.commands.core import file_operations
from src.commands.core import navigation

from src.commands.plugins import archive
from src.commands.plugins import grep
from src.commands.plugins import shell_commands


class Shell():
    def __init__(self, log_filename="shell", cwd=os.getcwd()):
        self.env = self.load_env(CommandEnv(log_filename=log_filename, cwd=cwd))

    def get_prompt(self) -> str:
        return f"[{pretty_path(self.env.cwd)}] => "

    def load_env(self, env: CommandEnv) -> CommandEnv:
        """
        Загружает команды в командное окружение
        :param env: Командное окружение
        :return: Командное окружение с командами
        """
        env.load_commands_from_module(file_operations)
        env.load_commands_from_module(navigation)

        env.load_commands_from_module(archive)
        env.load_commands_from_module(grep)
        env.load_commands_from_module(shell_commands)

        return env

    def execute(self, cmd: str) -> str:
        """
        Запускает команду
        :param cmd: Название команды и агрументы к ней
        :return: Возвращает результат выполнения команды
        """
        self.env.logger.info(cmd)
        with open(COMMAND_HISTORY_PATH, 'a') as f:
            f.write(cmd + '\n')

        cmd_args = shlex.split(cmd)
        if not cmd_args:
            return ""

        self.env.command_output = ""

        command_function = self.env.commands.get(cmd_args[0])
        if not command_function:
            self.env.log_and_raise_exception(NameError(f"Command not found: {cmd_args[0]}"))

        try:
            command_function(self.env, cmd_args[1:])
        except Exception as e:
            self.env.log_and_raise_exception(e)

        return self.env.command_output

    def run(self) -> None:
        """
        Запускает оболочку в интерактивном режиме
        :return: Данная функция ничего не возвращает
        """
        try:
            while True:
                cmd = input(self.get_prompt())

                if cmd == "exit":
                    break

                try:
                    self.execute(cmd)
                except Exception as e:
                    if DEBUG:
                        raise e
                    print(f"Error: {str(e)}")
                except KeyboardInterrupt:
                    continue
        except KeyboardInterrupt:  # cleanly handle Ctrl+C signal without causing a stacktrace
            print()  # prevents ^C from being printed
