import pytest

import os

from tests.setup import sandbox_shell
from tests.setup import clear_or_create_test_sandbox
from tests.setup import create_file, create_dir

from src.path import tree
from src.constants import TEST_SANDBOX_DIR


@pytest.mark.usefixtures("clear_or_create_test_sandbox")
def test_ls(sandbox_shell):
    create_file(os.path.join(TEST_SANDBOX_DIR, 'file1'), "file1\n")

    dir = create_dir(os.path.join(TEST_SANDBOX_DIR, 'dir'))
    create_file(os.path.join(dir, 'file1'), "file1_dir\n")
    create_file(os.path.join(dir, 'file2'), "file2_dir\n")

    subdir = create_dir(os.path.join(dir, 'subdir'))
    create_file(os.path.join(subdir, 'file1'), "file1_subdir\n")

    # not a directory
    with pytest.raises(NotADirectoryError):
        sandbox_shell.execute("ls file1")

    # ls current directory
    result = sandbox_shell.execute("ls")
    assert "file1" in result and "dir" in result

    # ls path
    result = sandbox_shell.execute("ls dir")
    assert "file1" in result and "file2" in result and "subdir" in result

    # ls -l argument
    sandbox_shell.execute("ls -l")


@pytest.mark.usefixtures("clear_or_create_test_sandbox")
def test_cd(sandbox_shell):
    create_file(os.path.join(TEST_SANDBOX_DIR, 'file1'), "file1\n")

    dir = create_dir(os.path.join(TEST_SANDBOX_DIR, 'dir'))
    subdir = create_dir(os.path.join(dir, 'subdir'))

    # not a directory
    with pytest.raises(NotADirectoryError):
        sandbox_shell.execute("cd file1")

    # cd into current directory
    sandbox_shell.execute("cd .")
    assert sandbox_shell.env.cwd == TEST_SANDBOX_DIR

    # cd into relative path
    sandbox_shell.execute("cd dir")
    assert sandbox_shell.env.cwd == dir

    # cd to parent directory
    sandbox_shell.execute("cd ..")
    assert sandbox_shell.env.cwd == TEST_SANDBOX_DIR

    # cd to absolute path
    sandbox_shell.execute(f"cd {subdir}")
    assert sandbox_shell.env.cwd == subdir

    # cd to root
    sandbox_shell.execute("cd /")
    assert sandbox_shell.env.cwd == '/'


@pytest.mark.usefixtures("clear_or_create_test_sandbox")
def test_cat(sandbox_shell):
    create_file(os.path.join(TEST_SANDBOX_DIR, 'file1'), "line1\nline2\n")
    create_dir(os.path.join(TEST_SANDBOX_DIR, 'dir'))

    binary_file = os.path.join(TEST_SANDBOX_DIR, 'binary_file')
    with open(binary_file, 'wb') as f:
        f.write(b'\xAA\xBB\xCC')

    # not a file
    with pytest.raises(FileNotFoundError):
        sandbox_shell.execute("cat dir")

    # not a text file
    with pytest.raises(ValueError):
        sandbox_shell.execute("cat binary_file")

    # cat file
    result = sandbox_shell.execute("cat file1")
    assert result == "line1\nline2\n"


@pytest.mark.usefixtures("clear_or_create_test_sandbox")
def test_tree(sandbox_shell):
    create_file(os.path.join(TEST_SANDBOX_DIR, 'file1'), "file1\n")

    dir = create_dir(os.path.join(TEST_SANDBOX_DIR, 'dir'))
    create_file(os.path.join(dir, 'file1'), "file1_dir\n")
    create_file(os.path.join(dir, 'file2'), "file2_dir\n")

    subdir = create_dir(os.path.join(dir, 'subdir'))
    create_file(os.path.join(subdir, 'file1'), "file1_subdir\n")

    # not a directory
    with pytest.raises(NotADirectoryError):
        sandbox_shell.execute("tree file1")

    # tree directory
    result = sandbox_shell.execute("tree dir")
    assert "file1" in result and "file2" in result and "subdir" in result
