import os


def pretty_path(path: str) -> str:
    path = path.replace(os.path.expanduser('~'), '~', 1)
    return path
