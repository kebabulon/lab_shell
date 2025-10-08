import os
import shlex

from src.command import CommandEnv


class Shell():
    def __init__(self, log_filename="shell", cwd=os.getcwd()):
        self.env = CommandEnv(log_filename=log_filename, cwd=cwd)

    def get_prompt(self) -> str:
        return f"<{self.env.pretty_path(self.env.cwd)}> => "

    def execute(self, cmd: str) -> None:
        self.env.logger.info(cmd)

        cmd_args = shlex.split(cmd)
        if not cmd_args:
            return

        command_function = self.env.commands.get(cmd_args[0])
        if not command_function:
            self.env.log_and_print_error(f"Command not found: {cmd_args[0]}")
            return

        self.env.command_output = ""

        try:
            command_function(self.env, cmd_args[1:])
        except Exception as e:
            self.env.log_and_print_error(f"{str(e)}")

        return self.env.command_output

    def run(self) -> None:
        while cmd := input(self.get_prompt()):
            try:
                self.execute(cmd)
            except KeyboardInterrupt:
                continue
