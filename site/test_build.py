import tempfile
import unittest
from hashlib import sha256
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
        (self.public / "README.txt").write_text("Codex")
        (self.public / "sources.json").write_text("{}")
        for family in ("Mono", "Sans", "Serif"):
            for style in ("Regular", "Italic", "Medium", "MediumItalic", "Bold", "BoldItalic"):
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
        self.assertEqual(len(list((self.output / "fonts").iterdir())), 18)
        self.assertFalse((self.output / "fonts/private.woff2").exists())
        self.assertEqual((self.output / "OFL.txt").read_bytes(), b"public notice")
        with ZipFile(self.output / "Codex-typefaces.zip") as archive:
            self.assertEqual(len(archive.namelist()), 40)
            self.assertFalse(any("private" in name for name in archive.namelist()))
            self.assertEqual(archive.read("licenses/IBM-Plex-OFL-1.1.txt"), b"public notice")
            manifest = archive.read("SHA256SUMS").decode().splitlines()
            checksums = {name: digest for digest, name in (line.split("  ") for line in manifest)}
            self.assertEqual(set(checksums), set(archive.namelist()) - {"SHA256SUMS"})
            for name, checksum in checksums.items():
                self.assertEqual(archive.read(name), (self.public / name).read_bytes())
                self.assertEqual(checksum, sha256(archive.read(name)).hexdigest())
        css = (self.output / "fonts.css").read_text()
        for family in ("Mono", "Sans", "Serif"):
            self.assertIn(f'Codex{family}-MediumItalic.woff2") format("woff2"); font-style: italic; font-weight: 500;', css)
        self.assertIn('value="MediumItalic" data-weight="500" data-slant="italic"', (self.output / "index.html").read_text())

    def test_mislabeled_woff2_does_not_replace_a_good_stage(self):
        self.output.mkdir()
        (self.output / "index.html").write_text("last good build")
        (self.public / "web/CodexSerif-Italic.woff2").write_bytes(b"\x00\x01\x00\x00")
        with self.assertRaisesRegex(ValueError, "CodexSerif-Italic"):
            build(self.public, self.output)
        self.assertEqual((self.output / "index.html").read_text(), "last good build")


if __name__ == "__main__":
    unittest.main()
