import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from build import build


class PublicShowcaseTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.public = Path(self.temp.name) / "public"
        self.output = Path(self.temp.name) / "showcase"
        (self.public / "ttf").mkdir(parents=True)
        (self.public / "web").mkdir()
        (self.public / "licenses").mkdir()
        (self.public / "licenses/IBM-Plex-OFL-1.1.txt").write_bytes(b"public notice")
        for family in ("Mono", "Sans", "Serif"):
            for style in ("Regular", "Bold", "Italic", "BoldItalic"):
                stem = f"Codex{family}-{style}"
                (self.public / "ttf" / f"{stem}.ttf").write_bytes(b"\x00\x01\x00\x00" + stem.encode())
                (self.public / "web" / f"{stem}.woff2").write_bytes(b"wOF2" + stem.encode())

    def test_only_requested_public_files_and_notice_are_staged(self):
        (self.public / "ttf/private.ttf").write_bytes(b"private")
        (self.public / "web/private.woff2").write_bytes(b"private")
        self.output.mkdir()
        (self.output / "stale.zip").touch()
        build(self.public, self.output)
        self.assertFalse((self.output / "stale.zip").exists())
        self.assertEqual(len(list((self.output / "fonts").iterdir())), 12)
        self.assertFalse((self.output / "fonts/private.woff2").exists())
        self.assertEqual((self.output / "OFL.txt").read_bytes(), b"public notice")
        with ZipFile(self.output / "Codex-typefaces.zip") as archive:
            self.assertEqual(len(archive.namelist()), 13)
            self.assertNotIn("private.ttf", archive.namelist())
            self.assertEqual(archive.read("OFL.txt"), b"public notice")
            for path in (self.public / "ttf").glob("Codex*.ttf"):
                self.assertEqual(archive.read(path.name), path.read_bytes())

    def test_mislabeled_woff2_does_not_replace_a_good_stage(self):
        self.output.mkdir()
        (self.output / "index.html").write_text("last good build")
        (self.public / "web/CodexSerif-Italic.woff2").write_bytes(b"\x00\x01\x00\x00")
        with self.assertRaisesRegex(ValueError, "CodexSerif-Italic"):
            build(self.public, self.output)
        self.assertEqual((self.output / "index.html").read_text(), "last good build")


if __name__ == "__main__":
    unittest.main()
