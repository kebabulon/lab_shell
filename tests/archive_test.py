import pytest

import os
from shutil import ReadError

from tests.setup import sandbox_shell
from tests.setup import clear_or_create_test_sandbox
from tests.setup import create_file, create_dir

from src.path import tree
from src.constants import TEST_SANDBOX_DIR


@pytest.mark.usefixtures("clear_or_create_test_sandbox")
def test_zip_and_unzip(sandbox_shell):
    create_file(os.path.join(TEST_SANDBOX_DIR, 'file'), "file1\n")

    dir = create_dir(os.path.join(TEST_SANDBOX_DIR, 'dir'))

    subdir = create_dir(os.path.join(dir, 'subdir'))
    create_file(os.path.join(subdir, 'file1'), "file1_subdir\n")
    create_file(os.path.join(subdir, 'file2'), "file2_subdir\n")

    subdir_archive = os.path.join(TEST_SANDBOX_DIR, 'subdir.zip')

    file1_extracted = os.path.join(TEST_SANDBOX_DIR, 'file1')
    file2_extracted = os.path.join(TEST_SANDBOX_DIR, 'file2')

    #  cannot zip file
    with pytest.raises(NotADirectoryError):
        sandbox_shell.execute("zip file")

    #  not a zip archive
    with pytest.raises(ReadError):
        sandbox_shell.execute("unzip file")

    #  destination exists
    with pytest.raises(NotADirectoryError):
        sandbox_shell.execute("zip file dir/subdir/file1")

    #  zip directory
    sandbox_shell.execute("zip dir/subdir")
    assert os.path.exists(subdir_archive)

    #  unzip directory
    sandbox_shell.execute("unzip subdir.zip")
    with open(file1_extracted, 'r') as f:
        assert f.read() == "file1_subdir\n"
    with open(file2_extracted, 'r') as f:
        assert f.read() == "file2_subdir\n"


@pytest.mark.usefixtures("clear_or_create_test_sandbox")
def test_tar_and_untar(sandbox_shell):
    create_file(os.path.join(TEST_SANDBOX_DIR, 'file'), "file1\n")

    dir = create_dir(os.path.join(TEST_SANDBOX_DIR, 'dir'))

    subdir = create_dir(os.path.join(dir, 'subdir'))
    create_file(os.path.join(subdir, 'file1'), "file1_subdir\n")
    create_file(os.path.join(subdir, 'file2'), "file2_subdir\n")

    subdir_archive = os.path.join(TEST_SANDBOX_DIR, 'subdir.tar')

    file1_extracted = os.path.join(TEST_SANDBOX_DIR, 'file1')
    file2_extracted = os.path.join(TEST_SANDBOX_DIR, 'file2')

    #  cannot zip file
    with pytest.raises(NotADirectoryError):
        sandbox_shell.execute("tar file")

    #  not a zip archive
    with pytest.raises(ReadError):
        sandbox_shell.execute("untar file")

    #  destination exists
    with pytest.raises(NotADirectoryError):
        sandbox_shell.execute("tar file dir/subdir/file1")

    #  zip directory
    sandbox_shell.execute("tar dir/subdir")
    assert os.path.exists(subdir_archive)

    #  unzip directory
    sandbox_shell.execute("untar subdir.tar")
    with open(file1_extracted, 'r') as f:
        assert f.read() == "file1_subdir\n"
    with open(file2_extracted, 'r') as f:
        assert f.read() == "file2_subdir\n"
