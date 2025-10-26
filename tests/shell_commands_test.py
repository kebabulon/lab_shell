import pytest

from argparse import ArgumentError

from tests.setup import sandbox_shell
from tests.setup import clear_or_create_test_sandbox, clear_command_history


@pytest.mark.usefixtures("clear_command_history")
def test_history(sandbox_shell):
    #  history last command
    sandbox_shell.execute("ls")
    result = sandbox_shell.execute("history 1")
    assert "ls" in result and "1" in result

    #  history with no argument
    result = sandbox_shell.execute("history")
    assert "ls" in result and "1" in result and "history 1" in result

    #  n is not a number
    with pytest.raises(ArgumentError):
        sandbox_shell.execute("history test")

    #  n is not a positive number
    with pytest.raises(ValueError):
        sandbox_shell.execute("history 0")
    with pytest.raises(ValueError):
        sandbox_shell.execute("history -1")


def test_help(sandbox_shell):
    #  command doesnt exists
    with pytest.raises(NameError):
        sandbox_shell.execute("help test")

    #  help command
    sandbox_shell.execute("help ls")
    sandbox_shell.execute("help help")
