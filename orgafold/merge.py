import shutil
from pathlib import Path
import subprocess


def merge_file(source_file: Path, target_directory: Path, run=False, move=False):
    """ Merge file to a directory.

    :param run: Dry run only?
    :param move: Move or copy
    """
    if source_file.is_file():
        target_file = target_directory / source_file.name
        if run:
            try:
                target_directory.mkdir(parents=True, exist_ok=True)
            except (FileExistsError, NotADirectoryError):  # one of parent directories is a file
                # XX our folder might get renamed to handle this
                print(f"Cannot copy to {target_file}")
                return

        # rename on file name collision
        while target_file.exists():
            name, suffix = target_file.stem, target_file.suffix

            # extract parenthesis
            try:
                number = int(name.split("(")[-1].split(")")[0])
                name = name.rsplit("(", 1)[0].strip()
            except ValueError:
                number = 1

            # add number to the parenthesis
            new_name = f"{name} ({number + 1}){suffix}"
            target_file = target_file.with_name(new_name)

        # insert file to the target
        match run, move:
            case True, True:
                shutil.move(source_file, target_file)
            case True, False:
                shutil.copy2(source_file, target_file)
            case False | None, _:
                print(f"Would {'move' if move else 'copy'}", source_file, "→", target_file)


def merge_directories(source_directory: Path, target_directory: Path, run=False, move=False, rmdir=False, only_files=False):
    """
    :param run: Dry run only?
    :param move: Move or copy
    :param rmdir: Delete from the source_directory empty dirs after moving the files out.
    :param only_files: Only insert files to the target_directory, ignore their directory structure.
    """

    for source_file in source_directory.rglob("*"):
        if not only_files:  # keep subdirs structure
            target_directory /= source_file.parent.relative_to(source_directory)
        merge_file(source_file, target_directory, run, move)

    # remove empty subdirectories
    if run and move and rmdir:
        subprocess.run(["find", str(source_directory), "-type", "d", "-empty", "-delete"])
