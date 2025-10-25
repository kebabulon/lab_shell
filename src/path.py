import os


def pretty_path(path: str) -> str:
    path = path.replace(os.path.expanduser('~'), '~', 1)
    return path


def validate_path(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(f"No such file or dir {path}")


space =  '    '
branch = '│   '
tee =    '├── '
last =   '└── '


def tree(path: str, prefix: str = '') -> str:
    result = '.\n' if prefix == '' else ''

    files = sorted(os.listdir(path))

    for i in range(len(files)):
        file_name = files[i]
        file_path = os.path.join(path, file_name)

        pointer = last if i == len(files) - 1 else tee
        result += prefix + pointer + file_name + '\n'

        if os.path.isdir(file_path):
            extension = branch if pointer == tee else space
            result += tree(file_path, prefix=prefix + extension)

    return result
