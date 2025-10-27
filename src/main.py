import readline  # provides line editing and history features for `input()`

from src.shell import Shell


def main() -> None:
    """
    Точкой входа в приложение. Создает Shell и запускает оболочку в интерактивном виде
    :return: Данная функция ничего не возвращает
    """

    readline.set_auto_history(True)

    shell = Shell()
    shell.run()


if __name__ == "__main__":
    main()
