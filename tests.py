from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import main, mock, TestCase

from inquirer.events import KeyEventGenerator

from orgafold.__main__ import fetch_config, process
from orgafold.cmd import Cmd
from orgafold.dialoguer import checkboxes, radio


@dataclass
class Config1:
    p1: bool = True
    p2: bool = False
    p3: bool = True


class Config2:
    def __init__(self):
        self.p1: bool = True
        self.p2: bool = False
        self.p3: bool = True


class TestDialogue(TestCase):
    def _input(self, *keys):
        """ Mock inquirer input """
        def deescape(k):
            for a, b in (("Down", "\x1b[B"), ("Space", "\x20")):
                k = k.replace(a, b)
            return k
        keys = iter([deescape(k) for k in keys or ()] + ["\n"])

        def init(o):
            o._key_gen = lambda: next(keys)
        return mock.patch.object(KeyEventGenerator, '__init__', init)

    def _objects(self):
        yield from (Config1(), Config2())

    def test_radio(self):
        for o in self._objects():
            with self._input("Down"):
                radio(o)
            self.assertListEqual([False, True, False], list(vars(o).values()))

            with self._input():
                radio(o, ["p3"])
            self.assertListEqual([False, True, True], list(vars(o).values()))

            with self._input():
                radio(o, [("Label1", "p1")])
            self.assertListEqual([True, True, True], list(vars(o).values()))

    def test_checkboxes(self):
        for o in self._objects():
            with self._input("Down", "Space"):
                checkboxes(o)
            self.assertListEqual([True, True, True], list(vars(o).values()))

            with self._input("Space"):
                checkboxes(o)
            self.assertListEqual([False, True, True], list(vars(o).values()))

            with self._input("Down", "Space"):
                checkboxes(o, ("p2", "p3"))
            self.assertListEqual([False, True, False], list(vars(o).values()))

            with self._input("Down", "Space"):
                checkboxes(o, (("Label2", "p2"), ("Label3", "p3")))
            self.assertListEqual([False, True, True], list(vars(o).values()))


class TestOrgafold(TestCase):
    def setUp(self):
        self.tempdir = TemporaryDirectory()
        for f in ("a.txt", "b.txt", "c.gif"):
            Path(self.tempdir.name, f).write_text("testing")

    def tearDown(self):
        self.tempdir.cleanup()

    def _fetch(self, flags):
        cmd = Cmd()
        fetch_config(cmd, f"{self.tempdir.name} {flags}")
        return cmd

    def test_analysis(self):
        cmd = self._fetch("--suffix")
        stdout = StringIO()
        with redirect_stdout(stdout):
            process(cmd)
        self.assertEqual("""Analysis: suffix
2× .txt 14 Bytes
1× .gif 7 Bytes""", stdout.getvalue().rstrip())

    def test_dry(self):
        cmd = self._fetch("--suffix --copy --dry --run")
        stdout = StringIO()
        with redirect_stdout(stdout):
            process(cmd)
        self.assertEqual(3, len([line for line in stdout.getvalue().splitlines() if line.startswith("Would copy")]))

    def test_copy(self):
        with TemporaryDirectory() as target:
            cmd = self._fetch(f"--suffix --copy --run --output {target}")
            process(cmd)
            # successfully copied
            self.assertListEqual(['gif', 'gif/c.gif', 'txt', 'txt/a.txt', 'txt/b.txt'],
                                 sorted([str(f.relative_to(target)) for f in Path(target).rglob("*")]))
            # and not moved
            tempdir = Path(self.tempdir.name)
            self.assertListEqual(['a.txt', 'b.txt', 'c.gif'], sorted(
                [str(f.relative_to(tempdir)) for f in tempdir.rglob("*")]))


if __name__ == "__main__":
    main()