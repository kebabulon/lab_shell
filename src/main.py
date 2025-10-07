import readline  # provides line editing and history features for `input()`

from src.shell import Shell


def main() -> None:
    """
    Обязательнная составляющая программ, которые сдаются. Является точкой входа в приложение
    :return: Данная функция ничего не возвращает
    """

    readline.set_auto_history(True)

    shell = Shell()
    shell.run()


if __name__ == "__main__":
    main()
