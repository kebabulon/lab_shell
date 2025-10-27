import pytest

from tests.setup import sandbox_shell


def test_shell(sandbox_shell):
    #  command not found
    with pytest.raises(NameError):
        sandbox_shell.execute("test")

    #  empty command
    sandbox_shell.execute("")
