import os


def pretty_path(path: str) -> str:
    path = path.replace(os.path.expanduser('~'), '~', 1)
    return path


def validate_path(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(f"No such file or dir {pretty_path(path)}")
