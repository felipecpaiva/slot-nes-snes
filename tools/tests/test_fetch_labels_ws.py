"""tools/fetch-labels.py WonderSwan route, offline: one WS shelf, two No-Intro dats, and the ScreenScraper id
picked per ROM by the footer colour flag.

    python3 -m unittest tools/tests/test_fetch_labels_ws.py
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import tempfile
import unittest
import urllib.parse
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("fetch_labels", os.path.join(HERE, "..", "fetch-labels.py"))
fl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fl)

PNG = fl.PNG + b"label" * 40
SS_ENV = {"SS_DEVID": "d", "SS_DEVPASSWORD": "p"}
JEU = {"response": {"jeu": {"medias": [{"type": "support-texture", "region": "jp", "url": "https://x.test/m.png"}]}}}


def crc(b):
    return f"{zlib.crc32(b) & 0xffffffff:08X}"


def cart(fill, colour):
    rom = bytearray(fill * 0x10000)
    rom[-9] = colour
    return bytes(rom)


def dat_text(*games):
    return "".join(f'game (\n\tname "{n}"\n\trom ( name "{n}.x" size 1 crc {c} )\n)\n' for n, c in games)


class Http:
    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def get(self, url):
        self.calls.append(url)
        for prefix, r in self.routes.items():
            if url.startswith(prefix):
                return r
        return 404, b"", None


class WonderSwan(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.card = os.path.join(self.tmp, "card")
        os.makedirs(os.path.join(self.card, "Games", "WS"))

    def rom(self, name, data):
        fl.spit(os.path.join(self.card, "Games", "WS", name), data)

    def test_one_ws_shelf_reads_both_bandai_dats_and_both_extensions(self):
        self.assertEqual(fl.SYSTEMS["WS"][:2], ("wonderswan", {".ws", ".wsc"}))
        self.assertEqual(fl.SYSTEMS["WS"][2], ["Bandai - WonderSwan", "Bandai - WonderSwan Color"])
        self.assertEqual((fl.SYSTEMS["WS"][3], fl.WS_COLOR_ID), (45, 46))
        self.assertNotIn("WS", fl.ART_SYSTEMS)

    def test_a_colour_footer_asks_screenscraper_for_46_and_a_mono_one_for_45_both_found_by_crc(self):
        mono, colour = cart(b"m", 0), cart(b"c", 1)
        self.rom("Gunpey.ws", mono)
        self.rom("Final Fantasy.wsc", colour)
        dats = {fl.DAT + urllib.parse.quote("Bandai - WonderSwan") + ".dat":
                (200, dat_text(("Gunpey (Japan)", crc(mono))).encode(), None),
                fl.DAT + urllib.parse.quote("Bandai - WonderSwan Color") + ".dat":
                (200, dat_text(("Final Fantasy (Japan)", crc(colour))).encode(), None),
                fl.SS_API + "jeuInfos.php": (200, json.dumps(JEU).encode(), None),
                "https://x.test/": (200, PNG, None)}
        http = Http(dats)
        ctx = fl.Ctx(http=http, env=dict(SS_ENV, SLOT_LABELS_CACHE=os.path.join(self.tmp, "cache")),
                     sleep=lambda s: None)
        with contextlib.redirect_stdout(io.StringIO()):
            stats = fl.main(["--card", self.card, "--only", "WS"], ctx)
        self.assertEqual((stats["matched"], stats["written"]), (2, 2))
        asked = {urllib.parse.parse_qs(urllib.parse.urlsplit(u).query)["romnom"][0]:
                 urllib.parse.parse_qs(urllib.parse.urlsplit(u).query)["systemeid"][0]
                 for u in http.calls if "jeuInfos.php" in u}
        self.assertEqual(asked, {"Gunpey (Japan).bin": "45", "Final Fantasy (Japan).bin": "46"})
        for stem in ("Gunpey", "Final Fantasy"):
            self.assertEqual(fl.slurp(os.path.join(self.card, "Labels", "WS", stem + ".png")), PNG)


if __name__ == "__main__":
    unittest.main()
