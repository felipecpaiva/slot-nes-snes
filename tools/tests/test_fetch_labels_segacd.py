"""tools/fetch-labels.py for Sega CD (ADR 0104), offline: the system entry, discs by name with the cover and the
disc scan, a two-disc set as one game, and no disc hashed.

    python3 -m unittest tools/tests/test_fetch_labels_segacd.py
"""
import contextlib
import io
import json
import os
import urllib.parse

from tools.tests import test_fetch_labels as t
from tools.tests.test_fetch_labels import PNG, SS_ENV, Base, fl

COVER = fl.PNG + b"cover" * 20
DISC = fl.PNG + b"disc" * 20


def lunar(name="Lunar - The Silver Star"):
    return {"id": "1984", "noms": [{"region": "us", "text": name}], "systeme": {"id": "20", "text": "Mega-CD"},
            "medias": [{"type": "box-2D", "region": "us", "url": "https://x.test/cover.png", "format": "png"},
                       {"type": "support-2D", "region": "us", "url": "https://x.test/disc.png", "format": "png"},
                       {"type": "ss", "region": "us", "url": "https://x.test/shot.png", "format": "png"}]}


class SegaCd(Base):
    def search(self, stems, args=("--by-name",)):
        for stem in stems:
            self.rom("SEGACD", stem, b"chd" * 10)
        h = t.NesSnes.ss_http(self, {})
        h.prefix = {fl.SS_API + "ssuserInfos.php": (200, b"{}", None),
                    fl.SS_API + "jeuRecherche.php": (200, json.dumps({"response": {"jeux": [lunar()]}}).encode(), None),
                    fl.SS_API + "jeuInfos.php": (404, b"", None),
                    "https://x.test/cover.png": (200, COVER, None), "https://x.test/disc.png": (200, DISC, None),
                    "https://x.test/": (200, PNG, None)}
        ctx = fl.Ctx(http=h, env=dict(SS_ENV, SLOT_LABELS_CACHE=os.path.join(self.tmp, "cache")), sleep=lambda s: None)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            stats = fl.main(["--card", self.card, "--only", "SEGACD", *args], ctx)
        self.out, self.http = out.getvalue(), h
        return stats

    def asked(self, api):
        return [c for c in self.http.calls if c.startswith(fl.SS_API + api)]

    def test_sega_cd_names_its_library_folder_screenscraper_id_and_thumbnails_folder(self):
        self.assertEqual(fl.SYSTEMS["SEGACD"], ("segacd", {".chd", ".cue", ".m3u", ".iso"}, [], 20))
        self.assertEqual(fl.DISC_SYSTEMS["SEGACD"], "Sega - Mega-CD - Sega CD")
        self.assertNotIn("SEGACD", fl.ART_SYSTEMS)

    def test_a_disc_by_name_takes_the_cover_and_the_disc_scan_under_20_and_is_never_hashed(self):
        stats = self.search(["Lunar - The Silver Star (USA).chd"])
        self.assertEqual(stats["by_name"], 1)
        self.assertEqual(self.label("SEGACD", "Lunar - The Silver Star (USA)"), COVER)
        self.assertEqual(self.label("SEGACD", "disc/Lunar - The Silver Star (USA)"), DISC)
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(self.asked("jeuRecherche.php")[0]).query)
        self.assertEqual(q["systemeid"], ["20"])
        self.assertFalse(any("crc=" in c for c in self.asked("jeuInfos.php")))
        self.assertFalse(os.path.isdir(os.path.join(self.tmp, "cache", "crc")), "no disc was hashed")

    def test_a_two_disc_set_is_one_game_under_its_title(self):
        stats = self.search(["Lunar - The Silver Star (USA) (Disc 1).chd", "Lunar - The Silver Star (USA) (Disc 2).chd"])
        self.assertEqual(stats["by_name"], 1)
        self.assertEqual(self.label("SEGACD", "Lunar - The Silver Star (USA)"), COVER)
        self.assertIsNone(self.label("SEGACD", "Lunar - The Silver Star (USA) (Disc 1)"))

    def test_without_by_name_nothing_is_asked_and_the_run_says_why(self):
        self.search(["Lunar - The Silver Star (USA).chd"], args=())
        self.assertEqual(self.asked("jeuRecherche.php"), [])
        self.assertIn("go by name only, rerun with --by-name", self.out)
        self.assertIsNone(self.label("SEGACD", "Lunar - The Silver Star (USA)"))

    def test_a_game_with_both_labels_is_skipped(self):
        for sub in ("", "disc"):
            d = os.path.join(self.card, "Labels", "SEGACD", sub)
            os.makedirs(d, exist_ok=True)
            fl.spit(os.path.join(d, "Lunar - The Silver Star (USA).png"), PNG)
        stats = self.search(["Lunar - The Silver Star (USA).chd"])
        self.assertEqual((stats["skipped"], stats["by_name"]), (1, 0))
        self.assertEqual(self.asked("jeuRecherche.php"), [])
