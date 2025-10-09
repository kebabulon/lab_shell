import os
import shlex

from src.command import CommandEnv


class Shell():
    def __init__(self, log_filename="shell", cwd=os.getcwd()):
        self.env = CommandEnv(log_filename=log_filename, cwd=cwd)

    def get_prompt(self) -> str:
        return f"[{self.env.pretty_path(self.env.cwd)}] => "

    def execute(self, cmd: str) -> None:
        self.env.logger.info(cmd)

        cmd_args = shlex.split(cmd)
        if not cmd_args:
            return

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
        try:
            while True:
                cmd = input(self.get_prompt())
                try:
                    self.execute(cmd)
                except Exception as e:
                    print(f"Error: {str(e)}")
                except KeyboardInterrupt:
                    continue
        except KeyboardInterrupt:  # cleanly handle Ctrl+C signal without causing a stacktrace
            print()  # prevents ^C from being printed
