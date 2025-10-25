import pytest

import os
import shutil

from src.constants import TEST_SANDBOX_DIR, UNDO_HISTORY_PATH
from src.shell import Shell


@pytest.fixture()
def sandbox_shell() -> Shell:
    shell = Shell(log_filename="test_shell", cwd=TEST_SANDBOX_DIR)
    return shell


@pytest.fixture()
def clear_or_create_test_sandbox() -> None:
    if os.path.exists(TEST_SANDBOX_DIR):
        shutil.rmtree(TEST_SANDBOX_DIR)
    os.makedirs(TEST_SANDBOX_DIR, exist_ok=True)


@pytest.fixture()
def clear_undo_history() -> None:
    if os.path.exists(UNDO_HISTORY_PATH):
        os.remove(UNDO_HISTORY_PATH)


def create_file(file_path: str, contents: str = "") -> str:
    with open(file_path, 'w') as f:
        f.write(contents)
    return file_path


def create_dir(dir_path: str) -> str:
    os.makedirs(dir_path)
    return dir_path
