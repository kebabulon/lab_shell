import os
import shutil
import shlex

from argparse import ArgumentParser
from src.command import command, CommandEnv
from src.path import validate_path

from src.constants import TRASH_DIR
from src.constants import UNDO_HISTORY_PATH


def safety_check_root(source: str) -> None:
    if os.path.splitroot(source)[2] == '':
        raise PermissionError("Unable to operate with root directory")


def safety_check_parent_directory(source: str, dest: str) -> None:
    if not source.endswith(os.path.sep):
        source += os.path.sep
    if not dest.endswith(os.path.sep):
        dest += os.path.sep

    if dest.startswith(source):
        raise PermissionError("Unable to operate with parent directory")


def get_next_undo_count() -> int:
    if not os.path.exists(UNDO_HISTORY_PATH):
        return 1

    with open(UNDO_HISTORY_PATH, 'r') as f:
        lines = f.readlines()

    return len(lines) + 1


def get_undo_prefix() -> str:
    return f"{get_next_undo_count()}_"


def add_undo_command(name: str, args: list[str]) -> None:
    args.insert(0, name)

    with open(UNDO_HISTORY_PATH, 'a') as f:
        f.write(f"{shlex.join(args)}\n")


def copy_and_trash_overwritten_function(undo_prefix: str, dest_path: str, undo_paths: list[str], add_all_paths: bool):
    def _copy_and_trash_overwritten(src: str, dst: str, *, follow_symlinks=True):
        dst_exists = os.path.exists(dst)

        if dst_exists:
            rel_ovewritten_trash_path = os.path.relpath(dst, dest_path)
            ovewritten_trash_dir = undo_prefix + os.path.basename(dest_path)
            ovewritten_trash_path = os.path.join(TRASH_DIR, ovewritten_trash_dir, rel_ovewritten_trash_path)

            os.makedirs(os.path.dirname(ovewritten_trash_path), exist_ok=True)
            shutil.copy2(dst, ovewritten_trash_path)

        if not dst_exists or add_all_paths:
            undo_paths.append(dst)

        shutil.copy2(src, dst, follow_symlinks=follow_symlinks)

    return _copy_and_trash_overwritten


def remove_directory_if_empty(path: str) -> None:
    if not os.listdir(path):
        os.rmdir(path)


def move_and_overwrite(source: str, dest: str) -> None:
    if os.path.isfile(source):
        shutil.copy2(source, dest)
        os.remove(source)

    elif os.path.isdir(source):
        shutil.copytree(source, dest, dirs_exist_ok=True)
        shutil.rmtree(source)


@command(
    name="cp",
    description="copy file/directory",
    help="""
        source - file/directory to copy
        dest - destination to copy file/directory to

        -r - recursively copy the contents of the directory
    """
)
def cmd_cp(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('source')
    parser.add_argument('dest')
    parser.add_argument('-r', action='store_true')
    argv = parser.parse_args(args)

    source_path = env.get_path(argv.source)
    validate_path(source_path)
    safety_check_root(source_path)

    dest_path = env.get_path(argv.dest)
    if os.path.isdir(dest_path):
        dest_path = os.path.join(dest_path, os.path.basename(source_path))

    safety_check_parent_directory(source_path, dest_path)

    if not os.path.exists(TRASH_DIR):
        os.makedirs(TRASH_DIR, exist_ok=True)

    undo_prefix = get_undo_prefix()
    undo_paths: list[str] = [dest_path]

    copy_and_trash_overwritten = copy_and_trash_overwritten_function(
        undo_prefix=undo_prefix,
        dest_path=dest_path,
        undo_paths=undo_paths,
        add_all_paths=False  # we don't need to remove files that are going to be overwritten anyway during undo
    )

    # TODO: maybe use copy_and_trash_overwritten for single file copies aswell?
    if os.path.isfile(source_path):
        try:
            if os.path.isfile(dest_path):
                ovewritten_trash_name = undo_prefix + os.path.basename(dest_path)
                ovewritten_trash_path = os.path.join(TRASH_DIR, ovewritten_trash_name)

                shutil.copy2(dest_path, ovewritten_trash_path)

            shutil.copy2(source_path, dest_path)
        except PermissionError:
            raise PermissionError("No permission")

    if os.path.isdir(source_path):
        if not argv.r:
            raise IsADirectoryError("Unable to copy directory without '-r' flag present")

        try:
            shutil.copytree(source_path, dest_path, dirs_exist_ok=True, copy_function=copy_and_trash_overwritten)
        except PermissionError:
            raise PermissionError("No permission")
        except FileExistsError:
            raise FileExistsError(f"Destination is a file {dest_path}")

    add_undo_command('cp', undo_paths)

    env.log_success(f"Successfully copied {source_path} to {dest_path}")


@command(
    name="mv",
    description="move/rename file/directory",
    help="""
        source - file/directory to move/rename
        dest - destination to move/rename file/directory to
    """
)
def cmd_mv(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('source')
    parser.add_argument('dest')
    argv = parser.parse_args(args)

    source_path = env.get_path(argv.source)
    validate_path(source_path)
    safety_check_root(source_path)
    safety_check_parent_directory(source_path, env.cwd)

    dest_path = env.get_path(argv.dest)
    if os.path.isdir(dest_path):
        dest_path = os.path.join(dest_path, os.path.basename(source_path))

    safety_check_parent_directory(source_path, dest_path)

    if not os.path.exists(TRASH_DIR):
        os.makedirs(TRASH_DIR, exist_ok=True)

    undo_prefix = get_undo_prefix()
    undo_paths: list[str] = [source_path, dest_path]

    copy_and_trash_overwritten = copy_and_trash_overwritten_function(
        undo_prefix=undo_prefix,
        dest_path=dest_path,
        undo_paths=undo_paths,
        add_all_paths=True  # we need to move all files back to where they were during undo
    )

    if os.path.isfile(source_path):
        try:
            if os.path.isfile(dest_path):
                ovewritten_trash_name = undo_prefix + os.path.basename(dest_path)
                ovewritten_trash_path = os.path.join(TRASH_DIR, ovewritten_trash_name)

                shutil.copy2(dest_path, ovewritten_trash_path)

                shutil.copy2(source_path, dest_path)
                os.remove(source_path)
            else:
                os.rename(source_path, dest_path)
        except PermissionError:
            raise PermissionError("No permission")

    if os.path.isdir(source_path):
        try:
            if not os.path.exists(dest_path):
                shutil.move(source_path, dest_path)
            else:
                #  dont use shutil.move because it cant overwrite, which is different compared to GNU's mv behaviour
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True, copy_function=copy_and_trash_overwritten)
                shutil.rmtree(source_path)
        except PermissionError:
            raise PermissionError("No permission")
        except FileExistsError:
            raise FileExistsError(f"Destination is a file {dest_path}")

    add_undo_command('mv', undo_paths)

    env.log_success(f"Successfully moved {source_path} to {dest_path}")


@command(
    name="rm",
    description="move file/directory to trash",
    help="""
        source - file/directory to trash

        -r - recursively trash the contents of the directory
        -f - forcibly trash directory without prompting the user
        --test - do not perform trashing, only raise exceptions
    """
)
def cmd_rm(env: CommandEnv, args: list[str]) -> None:
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('source')
    parser.add_argument('-r', action='store_true')
    parser.add_argument('-f', action='store_true')
    parser.add_argument('--test', action='store_true')
    argv = parser.parse_args(args)

    source_path = env.get_path(argv.source)
    validate_path(source_path)
    safety_check_root(source_path)
    safety_check_parent_directory(source_path, env.cwd)

    if os.path.isdir(source_path):
        if not argv.r:
            raise IsADirectoryError("Unable to trash directory without '-r' flag present")

        if not argv.f:
            while (confirm_prompt := input(f"Are you sure you want to trash {source_path}? [y/n] ")) not in ["y", "n"]:
                env.print("Invalid response")

            if confirm_prompt == "n":
                env.log_success("User did not confirm prompt. Done nothing")
                return

    if not os.path.exists(TRASH_DIR):
        os.makedirs(TRASH_DIR, exist_ok=True)

    undo_prefix = get_undo_prefix()

    trashed_source_name = undo_prefix + os.path.basename(source_path)
    trashed_source_path = os.path.join(TRASH_DIR, trashed_source_name)

    if not argv.test:
        try:
            shutil.move(source_path, trashed_source_path)
        except PermissionError:
            raise PermissionError("No permission")

        env.log_success(f"Successfully moved {source_path} to {trashed_source_path}")
    else:
        env.log_success("Test flag present. Done nothing")

    add_undo_command('rm', [source_path])


@command(
    name="undo",
    description="undo last cp, mv, rm command"
)
def cmd_undo(env: CommandEnv, args: list[str]) -> None:
    if not os.path.exists(UNDO_HISTORY_PATH):
        lines = []
    else:
        with open(UNDO_HISTORY_PATH, 'r') as f:
            lines = f.readlines()

    if not lines:
        env.print("No more commands to undo!")
        env.log_success("No commands to undo. Done nothing")
        return

    undo_count = len(lines)
    undo_prefix = f"{undo_count}_"

    undo_args = shlex.split(lines.pop())

    match undo_args.pop(0):
        case 'cp':
            dest_path = undo_args.pop(0)
            files_to_remove = undo_args

            if os.path.isfile(dest_path):
                os.remove(dest_path)
            else:
                for file in files_to_remove:
                    os.remove(file)
                    remove_directory_if_empty(os.path.dirname(file))

                if os.path.exists(dest_path):
                    remove_directory_if_empty(dest_path)

            overwritten_name = undo_prefix + os.path.basename(dest_path)
            overwritten_path = os.path.join(TRASH_DIR, overwritten_name)

            if os.path.exists(overwritten_path):
                move_and_overwrite(overwritten_path, dest_path)

            env.log_success(f"Successfully undone cp {dest_path}")
        case 'mv':
            source_path = undo_args.pop(0)

            dest_path = undo_args.pop(0)
            files_to_move = undo_args

            if os.path.isfile(dest_path):
                shutil.move(dest_path, source_path)

            elif os.path.isdir(dest_path):
                if files_to_move:
                    for file in files_to_move:
                        rel_source_file_path = os.path.relpath(file, dest_path)
                        source_file_path = os.path.join(source_path, rel_source_file_path)

                        os.makedirs(os.path.dirname(source_file_path), exist_ok=True)

                        shutil.move(file, source_file_path)
                        remove_directory_if_empty(os.path.dirname(file))

                    if os.path.exists(dest_path):
                        remove_directory_if_empty(dest_path)
                else:  # no files_to_move, that means that directory just got renamed
                    shutil.move(dest_path, source_path)

            overwritten_name = undo_prefix + os.path.basename(dest_path)
            overwritten_path = os.path.join(TRASH_DIR, overwritten_name)

            if os.path.exists(overwritten_path):
                move_and_overwrite(overwritten_path, dest_path)

            env.log_success(f"Successfully undone mv {source_path} {dest_path}")
        case 'rm':
            source_path = undo_args.pop(0)

            removed_name = undo_prefix + os.path.basename(source_path)
            removed_path = os.path.join(TRASH_DIR, removed_name)

            shutil.move(removed_path, source_path)

    with open(UNDO_HISTORY_PATH, 'w') as f:
        f.writelines(lines)
