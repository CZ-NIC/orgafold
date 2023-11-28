from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from unittest import main

import magic
from humanize import naturalsize
from pandas import DataFrame
from tqdm import tqdm

from .cmd import Cmd

magic_mime = magic.Magic(mime=True)


def get_mime(file):
    return magic_mime.from_file(file).split("/")


class Folder:

    def __init__(self, path: str | Path, cmd: Cmd = None):
        self.folder = path = Path(path)
        files = list(path.rglob("*"))
        mime_on = cmd.mime or cmd.subtype or cmd.mime_type

        columns = ['suffix', 'size', 'year', 'month']
        if mime_on:
            columns.extend(('mime', 'subtype', 'mime_type'))
            files = tqdm(files)
        stats = []
        for f in files:
            if f.is_file():
                s = f.stat()
                date = datetime.fromtimestamp(f.stat().st_mtime)
                row = [f.suffix.lower() or "''", s.st_size, date.year, date.month]
                if mime_on:
                    m = get_mime(f)
                    row.extend((m[0], m[1], "/".join(m)))
                stats.append(row)
        self.stats = df = DataFrame(stats, columns=columns)

        self.suffixes = list(df.groupby(["suffix"], as_index=False).agg(
            {'size': 'count'}).itertuples(index=False, name=None))
        self.size = sum(df["size"])

    def analysis(self, suffix=False, mime=False, subtype=False, mime_type=False, year=False, month=False):
        df = self.stats
        group_by = [var for var, value in locals().items() if value is True]

        if not group_by:
            print("Nothing to analyse, append some criteria (like --suffix)")
            return
        print("Analysis: " + " ".join(group_by))

        unique_combinations = (df
                               .groupby(group_by, as_index=False)
                               .agg({'size': ['sum', 'count']})
                               .sort_values(by=('size', 'sum'), ascending=False)
                               .itertuples(index=False, name=None))
        for row in unique_combinations:
            print(f"{row[-1]}× {' '.join(str(s) for s in row[:-2])} {naturalsize(row[-2])}")

    def loop(self, target_folder: str | Path, year=False, month=False, suffix=False, mime=False, mime_subtype=False, subfolder="", recursive=True):
        """Loop files in the folder and suggest a target dir name.

        :param target_folder: Target dir.
        :param year: Append year to the subfolder. Ignored if subfolder set.
        :param month: Append month to the subfolder. Ignored if subfolder set.
        :param suffix: Append file suffix (lower case) to the subfolder. If not available, uses mime type. Ignored if subfolder set.
        :param mime: Append mime type to the subfolder. Ignored if subfolder set.
        :param mime_subtype: Append mime subtype to the subfolder. Ignored if subfolder set.
        :param subfolder: Mask for the subfolder name the file will be pointed to.
            Variables:
                $SUFFIX: file suffix (lower case) or mime type
                $MIME: mime type
                $MIME_SUBTYPE: mime subtype
                All strftime keywords, like %Y for year and %m for month.
        :param recursive:
        :yield: tuple: path to a source file, folder to be this file inserted to
        """
        for file in self.folder.glob("**/*" if recursive else "*"):
            if o := self.get_file_target(file, target_folder, year, month, suffix, mime, mime_subtype, subfolder):
                yield o

    @staticmethod
    def get_file_target(file: Path, target_folder: str | Path, year=False, month=False, suffix=False, mime=False, mime_subtype=False, subfolder=""):
        if file.exists() and file.is_file():
            mask = subfolder or "-".join(filter(bool, (year and '%Y', month and '%m',
                                                       suffix and "$SUFFIX", mime and "$MIME")))  # ex: `%Y-%m-$SUFFIX`
            # parse variables
            mask = mask.replace("$SUFFIX", file.suffix.lstrip(".").lower() or "$MIME")
            if "$MIME" in mask:
                mask = mask.replace("$MIME", get_mime(file)[0])
            if "$MIME_SUBTYPE" in mask:
                mask = mask.replace("$MIME", get_mime(file)[1])
            mask = str(datetime.fromtimestamp(file.stat().st_mtime).strftime(mask)) if "%" in mask else mask
            # suggest a target dir including possible subfolder
            return file, Path(target_folder) / mask

    def get_target_folder(self, target_folder: str | Path, year=False):
        """
        :param year: By default, we put the folder into the TARGET_FOLDER. If year=True, unpack it under the year of the youngest file.
        """
        folder = self.folder

        if year:
            files = [f for f in folder.rglob("*") if f.is_file()]
            if not files:
                return "0000"
            youngest = max(files, key=lambda s: s.stat().st_mtime)  # ignore symlinks
            return Path(target_folder) / str(datetime.fromtimestamp(youngest.stat().st_mtime).year)
        else:
            return Path(target_folder) / folder.name

    def __str__(self):
        return self.folder.name + " " + str(self.suffixes) + str(naturalsize(self.size))


@dataclass
class FolderList:
    """

    TODO this class is not used right now. The functionality:
from orgafold.merge import merge_directories

KNOWN_EXTENSIONS = ".jpg", ".jpeg", ".png", ".arw", ".nef", ".avi", ".mp4", ".m4a", ".wav", ".aif", ".jp2", ".pages", ".mp3"
# KNOWN_EXTENSIONS = ".txt",
MIN_DIR_SIZE = 2000

TARGET_FOLDER = False
folders = FolderList(SOURCE_FOLDER)

for path, target in tqdm(folders.loop(TARGET_FOLDER, year=True)):
    merge_directories(path, target, run=True, move=True, rmdir=True, only_files=True)

    """

    def __init__(self, source_folder: Path, subfolders_only: str = None):
        """
        :param source_folder:
        :param subfolders_only: find up subfolders with such name in the source_folder and pick up them only
            Ex: "Macintosh HD" ->
        TODO ignores files in the parent folder, these are taken as folders too.
        """
        iter_ = source_folder.rglob(subfolders_only) if subfolders_only else source_folder.glob("*")
        self.folders: list[Folder] = []
        for i, folder in enumerate(tqdm(iter_)):
            self.folders.append(Folder(folder))

    def loop(self, target_folder: str | Path, year=False, min_size=None, allowed_extensions=None):
        for f in self.folders:
            if f.folder.exists() \
                and (not min_size or f.size < min_size) \
                    and (not allowed_extensions or any(ext in f.suffixes for ext in allowed_extensions)):
                yield f.folder, f.get_target_folder(target_folder, year)

    def inspect_suffixes(self):
        return (sum((f.suffixes for f in self.folders), Counter()))

    def inspect_by_size(self):
        return sorted(self.folders, key=lambda f: f.size, reverse=True)

if __name__ == '__main__':
    main()
