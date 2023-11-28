import logging

from fire import Fire

from .dialoguer import checkboxes, radio

from .cmd import Cmd
from .merge import merge_file
from .orgafold import Folder

logger = logging.getLogger(__name__)


def process(cmd: Cmd):
    for inode in cmd.inodes:
        if inode.is_dir():
            folder = Folder(inode, cmd)
            if cmd.analyse:
                folder.analysis(cmd.suffix, cmd.mime, cmd.subtype, cmd.mime_type, cmd.year, cmd.month)
            if cmd.run or cmd.dry:
                for file, target_dir in folder.loop(cmd.output or folder.folder, suffix=cmd.suffix, year=cmd.year, month=cmd.month, mime=cmd.mime, recursive=cmd.recursive):
                    merge_file(file, target_dir, run=cmd.run, move=cmd.move)
        elif inode.is_file():
            if not cmd.output:
                logger.warn("Set --output to process single files")
            else:
                file, target_dir = Folder.get_file_target(
                    inode, cmd.output, suffix=cmd.suffix, year=cmd.year, month=cmd.month, mime=cmd.mime)
                merge_file(file, target_dir, run=cmd.run, move=cmd.move)
        else:
            logger.warn("Not implemented handling with %s", inode)


def fetch_config(cmd: Cmd, sysargv: bool | str=False, interactive=False):
    """Populate cmd object.

    :param cmd:
    :param sysargv: True to fetch with Fire from sysargv. String to pass the command toe Fire.
    :param interactive: Change cmd interactively.
    :return: False, if the user wants to interrupt.
    """
    if sysargv:
        Fire(cmd.refresh, None if sysargv is True else sysargv)
    if interactive:
        params = "suffix", "year", "month", "mime", "subtype", "mime_type", "recursive", "move", "copy"

        # Asks the user for new cmd
        if not checkboxes(cmd, params, title="Choose aggregation"):
            return False

        # Check their answer
        if cmd.move and cmd.copy:
            print("Cannot move and copy together!")
            return fetch_config(cmd, sysargv, interactive)

        # Decide the new action
        cmd.analyse, cmd.dry, cmd.run = True, False, False
        if (cmd.move or cmd.copy) and not radio(cmd, [("Just analyse", 'analyse'),
                                                ("Dry run", 'dry'),
                                                (f"Run: {'move' if cmd.move else 'copy'} inodes", 'run')], title="Action"):
            return False
    return True


def main():
    cmd = Cmd()
    fetch_config(cmd, True)
    while True:
        process(cmd)
        if not cmd.interactive or not fetch_config(cmd, False, True):
            break


if __name__ == "__main__":
    main()
