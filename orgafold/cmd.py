import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class Cmd:
    """ Config instructrions from CLI """

    def refresh(self, *input: list[Path], output: str = None,
                suffix=False, year=False, month=False, mime=False, subtype=False, mime_type=False,
                recursive=False,
                run: bool = False,  dry: bool = False,
                move: bool = False, copy=False,
                analyse: bool = False,
                interactive: bool = False):
        """ Quickly navigate through a high number of files, perhaps obtained after a disk recovery.

        Loops all the directories and expands them merged into a target directory. Does not overwrite file.
        Ex:
        SOURCE '/src', TARGET '/target'
        /src/blah1/file1 -> /target/2019/file1
        /src/blah1/file2 -> /target/2019/file2
        /src/blah2/file1 -> /target/2019/file1 (2)
        /src/blah2/foo/file3 -> /target/2019/foo/file3
        Note: I think we will not transfer symlinks.
        To delete them, you can use `find FOLDER -type l -delete; find FOLDER -type d -empty -delete`

        :param output: The directory we merge the inodes to. If not set, the input directory will be used.
        :param suffix: Append file suffix (lower case) to the subfolder. If not available, uses mime type. Ignored if subfolder set.
        :param year: Append year to the subfolder. Ignored if subfolder set.
        :param month: Append month to the subfolder. Ignored if subfolder set.
        :param mime: Append mime type part to the subfolder. Ignored if subfolder set.
        :param subtype: Append mime subtype part to the subfolder. Ignored if subfolder set.
        :param mime_type: Append whole mime type to the subfolder. Ignored if subfolder set.
        :param recursive:
        :param run: Perform operation (if dry is not set).
        :param dry: Dry run only.
        :param move: Move or copy? If false, copy is used.
        :param copy: If move not set, copy.
        :param analyse: By default True, if run and dry stays False. Print input inodes analysis.
        :param interactive: Allow changing the params at the runtime. Handy if you do multiple analysis, without the need of the re-analysing (mime types etc).
        """

        # Read input
        if not input:  # read ex. from a `find` program output
            input = (line.strip() for line in sys.stdin)
        try:
            self.inodes = inodes = [Path(s) for s in input]
        except KeyboardInterrupt:
            raise ValueError("No input. See --help")

        # Set parameters
        if dry:
            run = None
        if move and copy:  # We use move only. If copy is set to True, move stays False which is what we want.
            logger.error("Cannot move and copy together.")
            raise ValueError("Cannot move and copy together.")

        output = Path(output) if output else None
        analyse = analyse or (not run and not dry)

        # Print welcome info
        if run or dry:
            print(f"Organising {' '.join(str(s) for s in (inodes[:3] + ['...'] if len(inodes) > 3 else inodes))},"
                  f" {'move' if move else 'copy'} inodes")
            if dry:
                print("Dry run only")

        self.output, self.suffix, self.year, self.month, self.mime, self.subtype, self.mime_type, self.recursive, self.run, self.dry, self.move, self.copy, self.analyse = output, suffix, year, month, mime, subtype, mime_type, recursive, run,  dry, move, copy, analyse
        self.interactive = interactive
