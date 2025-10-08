import os
import shlex

from src.command import CommandEnv


def prettify_path(path: str) -> str:
    path = path.replace(os.path.expanduser('~'), '~', 1)
    return path


class Shell():
    def __init__(self):
        self.env = CommandEnv()

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

        try:
            command_function(self.env, cmd_args[1:])
        except Exception as e:
            # TODO: loooog
            print(f"{type(e).__name__} -> {str(e)}")

    def run(self) -> None:
        while cmd := input(self.get_prompt()):
            try:
                self.execute(cmd)
            except KeyboardInterrupt:
                continue
