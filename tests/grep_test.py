import pytest

import os

from tests.setup import sandbox_shell
from tests.setup import clear_or_create_test_sandbox
from tests.setup import create_file, create_dir

from src.constants import TEST_SANDBOX_DIR


@pytest.mark.usefixtures("clear_or_create_test_sandbox")
def test_grep(sandbox_shell):
    create_file(os.path.join(TEST_SANDBOX_DIR, 'file1'), "python c c#\n")

    dir = create_dir(os.path.join(TEST_SANDBOX_DIR, 'dir'))

    subdir = create_dir(os.path.join(dir, 'subdir'))
    create_file(os.path.join(subdir, 'file2'), "c++ goose goose\n")
    create_file(os.path.join(subdir, 'file3'), "goose\n")

    #  no -r flag present
    with pytest.raises(IsADirectoryError):
        sandbox_shell.execute("grep goose dir")

    #  grep file
    result = sandbox_shell.execute("grep c file1")
    assert result.count('"c"') == 2

    #  grep directory
    result = sandbox_shell.execute("grep c -r .")
    assert result.count('"c"') == 3

    result = sandbox_shell.execute("grep goose -r dir")
    assert result.count('"goose"') == 3

    # no patterns found
    result = sandbox_shell.execute("grep test -r .")
    result = result.rstrip('\n')
    assert result == ''
