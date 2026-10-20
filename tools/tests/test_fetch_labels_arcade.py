"""tools/fetch-labels.py arcade route, offline: Neo Geo, CPS1 and CPS2 sets asked by file name (ADR 0099).

    python3 -m unittest tools/tests/test_fetch_labels_arcade.py
"""
import json
import urllib.parse

from tools.tests import test_fetch_labels as base

fl, PNG = base.fl, base.PNG

TITLES = {("NEOGEO", "mslug"): "Metal Slug - Super Vehicle-001", ("CPS1", "ffight"): "Final Fight (World, set 1)",
          ("CPS2", "ddtod"): "Dungeons & Dragons: Tower of Doom (Europe 940412)"}
FLYER_ONLY = {"response": {"jeu": {"medias": [
    {"type": "ss", "region": "wor", "url": "https://x.test/shot.png"},
    {"type": "flyer", "region": "jp", "url": "https://x.test/flyer-jp.png"},
    {"type": "flyer", "region": "wor", "url": "https://x.test/flyer-wor.png"}]}}}
LABEL_AND_FLYER = {"response": {"jeu": {"medias": [
    {"type": "flyer", "region": "wor", "url": "https://x.test/flyer.png"},
    {"type": "support-texture", "region": "wor", "url": "https://x.test/label.png"}]}}}


class Arcade(base.Base):
    ss_http = base.NesSnes.ss_http
    run_ss = base.NesSnes.run_ss

    def setUp(self):
        super().setUp()
        old = fl._ARCADE_TITLES
        fl._ARCADE_TITLES = dict(TITLES)
        self.addCleanup(setattr, fl, "_ARCADE_TITLES", old)

    def asked(self):
        return [urllib.parse.parse_qs(urllib.parse.urlparse(u).query)
                for u in self.http.calls if u.startswith(fl.SS_API + "jeuInfos.php")]

    def downloads(self):
        return [u.split("?")[0] for u in self.http.calls if u.startswith("https://x.test/")]

    def test_the_three_arcade_shelves_list_zips_under_their_screenscraper_ids(self):
        self.assertEqual(fl.ARCADE, {"NEOGEO", "CPS1", "CPS2"})
        for system, sysid in (("NEOGEO", 142), ("CPS1", 6), ("CPS2", 7)):
            self.assertEqual(fl.SYSTEMS[system][1:], ({".zip"}, [], sysid))

    def test_a_set_is_asked_by_its_file_name_under_its_board_and_lands_in_its_labels(self):
        self.rom("CPS1", "ffight.zip", b"PK\x05\x06" + bytes(18))
        stats = self.run_ss("CPS1", {}, {}, (200, json.dumps(FLYER_ONLY).encode(), None),
                            ["--card", self.card, "--only", "CPS1"])
        self.assertEqual((stats["matched"], stats["written"], stats["unknown"]), (1, 1, 0))
        self.assertEqual(self.label("CPS1", "ffight"), PNG)
        (q,) = self.asked()
        self.assertEqual((q["romnom"], q["systemeid"], q["romtype"]), (["ffight.zip"], ["6"], ["rom"]))
        self.assertEqual(self.downloads(), ["https://x.test/flyer-wor.png"])

    def test_a_cart_label_scan_wins_over_the_flyer(self):
        self.rom("NEOGEO", "mslug.zip", b"PK\x05\x06" + bytes(18))
        self.run_ss("NEOGEO", {}, {}, (200, json.dumps(LABEL_AND_FLYER).encode(), None),
                    ["--card", self.card, "--only", "NEOGEO"])
        self.assertEqual(self.downloads(), ["https://x.test/label.png"])

    def test_a_zip_that_is_not_a_set_of_the_board_is_never_asked(self):
        self.rom("CPS2", "ffight.zip", b"PK")
        stats = self.run_ss("CPS2", {}, {}, (200, json.dumps(FLYER_ONLY).encode(), None),
                            ["--card", self.card, "--only", "CPS2"])
        self.assertEqual((stats["unknown"], stats["written"]), (1, 0))
        self.assertEqual(self.asked(), [])

    def test_a_set_with_no_media_is_missing_and_not_asked_again(self):
        self.rom("CPS2", "ddtod.zip", b"PK")
        empty = (200, json.dumps({"response": {"jeu": {"medias": []}}}).encode(), None)
        for _ in range(2):
            stats = self.run_ss("CPS2", {}, {}, empty, ["--card", self.card, "--only", "CPS2"])
        self.assertEqual(stats["missing"], 1)
        self.assertEqual(self.asked(), [])

    def test_a_name_search_and_a_logo_go_by_the_sets_full_title(self):
        self.assertEqual(fl.bare_title("mslug", "NEOGEO"), "Metal Slug - Super Vehicle-001")
        self.assertEqual(fl.title_key("ddtod", "CPS2"), "dungeonsanddragonstowerofdoom")
        out = fl.attempts("ffight", "CPS1")
        self.assertEqual([(a[0], a[1]) for a in out], [(6, "Final Fight")])
        self.assertEqual(fl.bare_title("ffight", "NES"), "ffight")
