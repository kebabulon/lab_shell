from src.command import command


@command(
    name="ls",
    description="print all files in directory"
)
def ls(args: list[str]) -> None:
    print(args)


# print(ls)
# print(type(ls))
