from collections.abc import Callable

CommandType = Callable[[str, list[str]], None]


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
