"""tools/fetch-labels.py for the Neo Geo CD (ADR 0107), offline: the system entry, discs by name with the cover
and the disc scan, and no disc hashed.

    python3 -m unittest tools/tests/test_fetch_labels_neocd.py
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
STEM = "Crossed Swords II (Japan) (En,Ja)"


def crossed_swords():
    return {"id": "3790", "noms": [{"region": "jp", "text": "Crossed Swords II"}],
            "systeme": {"id": "70", "text": "Neo-Geo CD"},
            "medias": [{"type": "box-2D", "region": "jp", "url": "https://x.test/cover.png", "format": "png"},
                       {"type": "support-2D", "region": "jp", "url": "https://x.test/disc.png", "format": "png"}]}


class NeoGeoCd(Base):
    def search(self, stems, args=("--by-name",)):
        for stem in stems:
            self.rom("NEOCD", stem, b"chd" * 10)
        h = t.NesSnes.ss_http(self, {})
        h.prefix = {fl.SS_API + "ssuserInfos.php": (200, b"{}", None),
                    fl.SS_API + "jeuRecherche.php": (200, json.dumps({"response": {"jeux": [crossed_swords()]}}).encode(),
                                                     None),
                    fl.SS_API + "jeuInfos.php": (404, b"", None),
                    "https://x.test/cover.png": (200, COVER, None), "https://x.test/disc.png": (200, DISC, None),
                    "https://x.test/": (200, PNG, None)}
        ctx = fl.Ctx(http=h, env=dict(SS_ENV, SLOT_LABELS_CACHE=os.path.join(self.tmp, "cache")), sleep=lambda s: None)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            stats = fl.main(["--card", self.card, "--only", "NEOCD", *args], ctx)
        self.out, self.http = out.getvalue(), h
        return stats

    def asked(self, api):
        return [c for c in self.http.calls if c.startswith(fl.SS_API + api)]

    def test_the_neo_geo_cd_names_its_library_folder_screenscraper_id_and_thumbnails_folder(self):
        self.assertEqual(fl.SYSTEMS["NEOCD"], ("neogeocd", {".cue", ".chd"}, [], 70))
        self.assertEqual(fl.DISC["NEOCD"], "SNK - Neo Geo CD")
        self.assertIn("NEOCD", fl.BY_NAME_DISCS)
        self.assertNotIn("NEOCD", fl.ART_SYSTEMS)

    def test_a_disc_by_name_takes_the_cover_and_the_disc_scan_under_70_and_is_never_hashed(self):
        stats = self.search([STEM + ".chd"])
        self.assertEqual(stats["by_name"], 1)
        self.assertEqual(self.label("NEOCD", STEM), COVER)
        self.assertEqual(self.label("NEOCD", "disc/" + STEM), DISC)
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(self.asked("jeuRecherche.php")[0]).query)
        self.assertEqual(q["systemeid"], ["70"])
        self.assertFalse(any("crc=" in c for c in self.asked("jeuInfos.php")))
        self.assertFalse(os.path.isdir(os.path.join(self.tmp, "cache", "crc")), "no disc was hashed")

    def test_without_by_name_nothing_is_asked_and_the_run_names_the_system(self):
        self.search([STEM + ".chd"], args=())
        self.assertEqual(self.asked("jeuRecherche.php"), [])
        self.assertIn("NEOCD: 1 games go by name only, rerun with --by-name", self.out)
        self.assertIsNone(self.label("NEOCD", STEM))
