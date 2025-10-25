import pytest

import os

from tests.setup import sandbox_shell
from tests.setup import clear_or_create_test_sandbox, clear_undo_history
from tests.setup import create_file, create_dir

from src.path import tree
from src.constants import TEST_SANDBOX_DIR


@pytest.mark.usefixtures("clear_or_create_test_sandbox")
@pytest.mark.usefixtures("clear_undo_history")
def test_cp_and_undo(sandbox_shell):
    create_file(os.path.join(TEST_SANDBOX_DIR, 'file1'), "file1\n")
    file2 = create_file(os.path.join(TEST_SANDBOX_DIR, 'file2'), "file2\n")

    dir = create_dir(os.path.join(TEST_SANDBOX_DIR, 'dir'))
    create_file(os.path.join(dir, 'file1'), "file1_dir\n")
    create_file(os.path.join(dir, 'file2'), "file2_dir\n")

    subdir = create_dir(os.path.join(dir, 'subdir'))
    file1_subdir = create_file(os.path.join(subdir, 'file1'), "file1_subdir\n")

    subdir2 = create_dir(os.path.join(TEST_SANDBOX_DIR, 'subdir'))
    create_file(os.path.join(subdir2, 'file1'), "file1_subdir2\n")

    file3 = os.path.join(TEST_SANDBOX_DIR, 'file3')
    dir_copy = os.path.join(TEST_SANDBOX_DIR, 'dir_copy')

    # no -r flag present
    with pytest.raises(IsADirectoryError):
        sandbox_shell.execute("cp dir dir3")

    #  copy file
    sandbox_shell.execute("cp file1 file3")
    with open(file3, 'r') as f:
        assert f.read() == "file1\n"

    #  copy and overwrite existing file
    sandbox_shell.execute("cp file1 file2")
    with open(file2, 'r') as f:
        assert f.read() == "file1\n"

    #  copy directory
    sandbox_shell.execute("cp -r dir dir_copy")
    assert tree(dir) == tree(dir_copy)

    #  copy and overwrite directory
    sandbox_shell.execute("cp -r subdir dir")
    assert tree(subdir2) == tree(subdir)
    with open(file1_subdir, 'r') as f:
        assert f.read() == "file1_subdir2\n"

    #
    # undo
    #

    #  copy and overwrite directory undo
    sandbox_shell.execute("undo")
    with open(file1_subdir, 'r') as f:
        assert f.read() == "file1_subdir\n"

    #  copy directory undo
    sandbox_shell.execute("undo")
    assert not os.path.exists(dir_copy)

    #  copy and overwrite existing file undo
    sandbox_shell.execute("undo")
    with open(file2, 'r') as f:
        assert f.read() == "file2\n"

    #  copy file undo
    sandbox_shell.execute("undo")
    assert not os.path.exists(file3)


@pytest.mark.usefixtures("clear_or_create_test_sandbox")
@pytest.mark.usefixtures("clear_undo_history")
def test_mv_and_undo(sandbox_shell):
    file1 = create_file(os.path.join(TEST_SANDBOX_DIR, 'file1'), "file1\n")
    file2 = create_file(os.path.join(TEST_SANDBOX_DIR, 'file2'), "file2\n")

    dir = create_dir(os.path.join(TEST_SANDBOX_DIR, 'dir'))
    create_file(os.path.join(dir, 'file1'), "file1_dir\n")
    create_file(os.path.join(dir, 'file2'), "file2_dir\n")

    subdir = create_dir(os.path.join(dir, 'subdir'))
    create_file(os.path.join(subdir, 'file1'), "file1_subdir\n")

    subdir2 = create_dir(os.path.join(TEST_SANDBOX_DIR, 'subdir'))
    file1_subdir2 = create_file(os.path.join(subdir2, 'file1'), "file1_subdir2\n")

    file3 = os.path.join(TEST_SANDBOX_DIR, 'file3')
    dir_move = os.path.join(TEST_SANDBOX_DIR, 'dir_move')

    dir_move_subdir = os.path.join(dir_move, 'subdir')
    file1_subdir_move = os.path.join(dir_move_subdir, 'file1')

    #  move file
    sandbox_shell.execute("mv file1 file3")
    with open(file3, 'r') as f:
        assert f.read() == "file1\n"
    assert not os.path.exists(file1)

    #  move and overwrite existing file
    sandbox_shell.execute("mv file3 file2")
    with open(file2, 'r') as f:
        assert f.read() == "file1\n"
    assert not os.path.exists(file3)

    #  move directory
    dir_tree = tree(dir)
    sandbox_shell.execute("mv dir dir_move")
    assert dir_tree == tree(dir_move)
    assert not os.path.exists(dir)

    #  move and overwrite directory
    subdir2_tree = tree(subdir2)
    sandbox_shell.execute("mv subdir dir_move")
    assert subdir2_tree == tree(dir_move_subdir)
    with open(file1_subdir_move, 'r') as f:
        assert f.read() == "file1_subdir2\n"
    assert not os.path.exists(subdir2)

    #
    # undo
    #

    #  move and overwrite directory undo
    sandbox_shell.execute("undo")
    with open(file1_subdir_move, 'r') as f:
        assert f.read() == "file1_subdir\n"
    with open(file1_subdir2, 'r') as f:
        assert f.read() == "file1_subdir2\n"

    #  move directory undo
    sandbox_shell.execute("undo")
    assert not os.path.exists(dir_move)
    assert dir_tree == tree(dir)

    #  move and overwrite existing file undo
    sandbox_shell.execute("undo")
    with open(file2, 'r') as f:
        assert f.read() == "file2\n"
    with open(file3, 'r') as f:
        assert f.read() == "file1\n"

    #  move file undo
    sandbox_shell.execute("undo")
    assert not os.path.exists(file3)
    with open(file1, 'r') as f:
        assert f.read() == "file1\n"


@pytest.mark.usefixtures("clear_or_create_test_sandbox")
@pytest.mark.usefixtures("clear_undo_history")
def test_rm_and_undo(sandbox_shell):
    file1 = create_file(os.path.join(TEST_SANDBOX_DIR, 'file1'), "file1\n")

    dir = create_dir(os.path.join(TEST_SANDBOX_DIR, 'dir'))
    create_file(os.path.join(dir, 'file1'), "file1_dir\n")
    create_file(os.path.join(dir, 'file2'), "file2_dir\n")

    subdir = create_dir(os.path.join(dir, 'subdir'))
    create_file(os.path.join(subdir, 'file1'), "file1_subdir\n")

    dir2 = create_dir(os.path.join(TEST_SANDBOX_DIR, 'dir2'))
    create_file(os.path.join(dir2, 'file1'), "file1_dir2\n")

    dir_tree = tree(dir)
    dir2_tree = tree(dir2)

    # no -r flag present
    with pytest.raises(IsADirectoryError):
        sandbox_shell.execute("rm --test -f dir")

    # prevent root trashing
    with pytest.raises(PermissionError):
        sandbox_shell.execute("rm --test -f /")

    # prevent parent directory trashing
    with pytest.raises(PermissionError):
        sandbox_shell.execute("rm --test -f ..")

    #  rm file
    sandbox_shell.execute("rm file1")
    assert not os.path.exists(file1)

    #  rm directory
    sandbox_shell.execute("rm -rf dir2")
    assert not os.path.exists(dir2)

    #  rm directory with sub directories
    sandbox_shell.execute("rm -rf dir")
    assert not os.path.exists(dir)

    #
    # undo
    #

    #  rm directory with sub directories undo
    sandbox_shell.execute("undo")
    assert dir_tree == tree(dir)

    #  rm directory undo
    sandbox_shell.execute("undo")
    assert dir2_tree == tree(dir2)

    #  rm file undo
    sandbox_shell.execute("undo")
    with open(file1, 'r') as f:
        assert f.read() == "file1\n"
