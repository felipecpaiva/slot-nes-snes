"""tools/fetch-labels.py --by-name, offline: the title normaliser, the sibling choice, a sibling copy on a card
and over a fake adb, and ScreenScraper jeuRecherche through a fake HTTP layer.

    python3 -m unittest tools/tests/test_fetch_labels_by_name.py
"""
import contextlib
import io
import json
import os
import urllib.parse

from tools.tests import test_fetch_labels as t
from tools.tests.test_fetch_labels import PNG, SS_ENV, Base, FakeAdb, crc, fl

BRETT = "Brett Hull Hockey 95"
OTHER = fl.PNG + b"other" * 20


def jeux(*games):
    return (200, json.dumps({"response": {"jeux": list(games)}}).encode(), None)


def game(gid, *names, system="1", medias=True):
    g = {"id": gid, "noms": [{"region": r, "text": t} for r, t in names], "systeme": {"id": system, "text": "Megadrive"}}
    if medias:
        g["medias"] = [{"type": "ss", "region": "us", "url": "https://x.test/shot.png", "format": "png"},
                       {"type": "support-texture", "region": "eu", "url": "https://x.test/eu.png", "format": "png"},
                       {"type": "support-texture", "region": "us", "url": "https://x.test/us.png", "format": "png"}]
    return g


class Names(Base):
    def test_goodtools_and_no_intro_names_meet_on_one_title(self):
        same = [("MD", "Brett Hull Hockey 95 (JUE) [b1]", "Brett Hull Hockey '95 (USA)"),
                ("MD", "Jungle Strike (UEJ) [p1][!]", "Jungle Strike (USA, Europe)"),
                ("GBA", "0468 - MegaMan Battle Network 2 (U)(Mode7)", "Mega Man Battle Network 2 (USA)"),
                ("GBC", "Super Mario Land (W) (V1.1) (Color Hack) [C]", "Super Mario Land (World) (Rev 1)"),
                ("NES", "'89 Dennou Kyuusei Uranai (J)", "89 Dennou Kyuusei Uranai (Japan)"),
                ("NES", "Takahashi Meijin no Bouken Shima (J) [T-Spa.99]", "Takahashi Meijin no Bouken Shima (Japan)"),
                ("SNES", "Legend of Zelda, The - A Link to the Past (U) [!]", "The Legend of Zelda - A Link to the Past"),
                ("GBC", "Pokémon Pinball (U) [C][!]", "Pokemon Pinball"),
                ("NES", "1943 - The Battle of Midway (U)", "1943: The Battle of Midway")]
        for system, a, b in same:
            self.assertEqual(fl.title_key(a, system), fl.title_key(b, system), (a, b))
            self.assertTrue(fl.title_key(a, system))
        self.assertEqual(fl.bare_title("0468 - MegaMan Battle Network 2 (U)(Mode7)", "GBA"), "MegaMan Battle Network 2")
        self.assertEqual(fl.bare_title("1943 - The Battle of Midway (U)", "NES"), "1943 - The Battle of Midway")
        self.assertNotEqual(fl.title_key("Sonic the Hedgehog 2 (W)"), fl.title_key("Sonic the Hedgehog (W)"))
        self.assertNotEqual(fl.title_key("Brett Hull Hockey (U)"), fl.title_key(BRETT))

    def test_regions_then_a_clean_dump_choose_the_sibling(self):
        self.assertEqual(fl.region_tags("Jungle Strike (UEJ) [p1][!]"), {"USA", "Europe", "Japan"})
        self.assertEqual(fl.region_tags("Super Mario Land (W) (V1.1) (Color Hack) [C]"), {"World"})
        self.assertEqual([fl.dump_rank(s) for s in ("A (U) [!]", "A (U)", "A (U) [b1]", "A (J) [T-Spa.99]",
                                                    "A (UEJ) [p1][!]", "A (U) [h1C]", "A (U) [C]")], [2, 1, 0, 0, 0, 0, 1])
        names = ["Jungle Strike (J).png", "Jungle Strike (UE) [b1].png", "Jungle Strike (UE) [!].png"]
        self.assertEqual(fl.pick_sibling("Jungle Strike (UEJ) [p1][!]", names), "Jungle Strike (UE) [!].png")
        self.assertEqual(fl.pick_sibling("Jungle Strike (J) [b1]", names), "Jungle Strike (J).png", "region first")


class Sibling(Base):
    ss_http = t.NesSnes.ss_http
    run_ss = t.NesSnes.run_ss

    def card_labels(self, system, **files):
        d = os.path.join(self.card, "Labels", system)
        os.makedirs(d, exist_ok=True)
        for name, body in files.items():
            fl.spit(os.path.join(d, name), body)

    def test_an_unknown_crc_copies_the_best_sibling_and_its_shell_line_without_any_request(self):
        self.rom("MD", f"{BRETT} (J) [b1].bin", b"bad" * 100)
        self.rom("MD", "Nothing Like It (U).bin", b"zzz" * 100)
        self.card_labels("MD", **{f"{BRETT} (U) [!].png": PNG, f"{BRETT} (J).png": OTHER, f"._{BRETT}.png": b"junk"})
        fl.spit(os.path.join(self.card, "Labels", "cart_shell.txt"), f"{BRETT} (J) = megadrive 26242a solid\n", "w")
        report = os.path.join(self.tmp, "r.tsv")
        stats = self.run_tool(self.dat("MD", ("Other (USA)", "DEADBEEF")),
                              ["--card", self.card, "--only", "MD", "--by-name", "--report", report])
        self.assertEqual(self.label("MD", f"{BRETT} (J) [b1]"), OTHER, "the Japanese sibling, sharing the region")
        self.assertEqual((stats["unknown"], stats["sibling"], stats["name_skipped"]), (2, 1, 1))
        self.assertIn(f"matched by sibling  MD/{BRETT} (J) [b1] <- {BRETT} (J)", self.out)
        self.assertEqual([c for c in self.http.calls if not c.startswith(fl.DAT)], [])
        shell = fl.slurp(os.path.join(self.card, "Labels", "cart_shell.txt"), "r")
        self.assertIn(f"{BRETT} (J) [b1] = megadrive 26242a solid", shell)
        self.assertEqual(fl.slurp(report, "r").splitlines(), [
            "system\tstem\toutcome\tsource", f"MD\t{BRETT} (J) [b1]\tsibling\t{BRETT} (J)",
            "MD\tNothing Like It (U)\tnot searched\tno SS_DEVID/SS_DEVPASSWORD"])

    def test_a_label_written_earlier_in_the_run_is_a_sibling_and_a_dry_run_writes_nothing(self):
        good = b"g" * 64
        self.rom("NES", "Tetris (U) [!].nes", good)
        self.rom("NES", "Tetris (U) [h1].nes", b"h" * 64)
        r = self.dat("NES", ("Tetris (USA)", crc(good)))
        routes = dict(r)
        self.run_ss("NES", routes, {}, (200, json.dumps({"response": {"jeu": {"medias": [
            {"type": "support-texture", "region": "us", "url": "https://x.test/m.png"}]}}}).encode(), None),
            ["--card", self.card, "--only", "NES", "--by-name", "--dry-run"])
        self.assertFalse(os.path.exists(os.path.join(self.card, "Labels")))
        self.assertIn("matched by sibling  NES/Tetris (U) [h1] <- Tetris (U) [!]", self.out)
        self.run_ss("NES", routes, {}, (200, json.dumps({"response": {"jeu": {"medias": [
            {"type": "support-texture", "region": "us", "url": "https://x.test/m.png"}]}}}).encode(), None),
            ["--card", self.card, "--only", "NES", "--by-name"])
        self.assertEqual(self.label("NES", "Tetris (U) [h1]"), PNG)
        self.assertFalse(any("jeuRecherche" in c for c in self.http.calls))

    def test_default_run_never_copies(self):
        self.rom("MD", f"{BRETT} (J) [b1].bin", b"bad" * 100)
        self.card_labels("MD", **{f"{BRETT} (J).png": OTHER})
        stats = self.run_tool(self.dat("MD", ("Other (USA)", "DEADBEEF")), ["--card", self.card, "--only", "MD"])
        self.assertEqual((stats["unknown"], stats["sibling"]), (1, 0))
        self.assertIsNone(self.label("MD", f"{BRETT} (J) [b1]"))
        self.assertNotIn("by sibling", self.out)

    def test_device_sibling_is_pulled_into_the_cache_and_only_the_new_label_is_pushed(self):
        sd = "/mnt/sdcard"
        lib = os.path.join(self.tmp, "lib")
        os.makedirs(os.path.join(lib, "megadrive"))
        adb = FakeAdb({f"{sd}/Games/MD/{BRETT} (J) [b1].bin": b"", f"{sd}/Labels/MD/{BRETT} (J).png": OTHER})
        stats = self.run_tool(self.dat("MD", ("Other (USA)", "DEADBEEF")),
                              ["--device", "--library", lib, "--only", "MD", "--by-name"], adb=adb)
        self.assertIn("(not in the library)", self.out)
        self.assertEqual(stats["sibling"], 1)
        self.assertEqual(adb.pushed, [f"{sd}/Labels/MD/{BRETT} (J) [b1].png"])
        self.assertEqual(adb.files[f"{sd}/Labels/MD/{BRETT} (J) [b1].png"], OTHER)
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "cache", "device", "MD", f"{BRETT} (J).png")))
        adb.files.pop(f"{sd}/Labels/MD/{BRETT} (J) [b1].png")
        pulls = len([c for c in adb.cmds if c[0] == "pull"])
        self.run_tool(self.dat("MD", ("Other (USA)", "DEADBEEF")),
                      ["--device", "--library", lib, "--only", "MD", "--by-name"], adb=adb)
        self.assertEqual(len([c for c in adb.cmds if c[0] == "pull"]), pulls, "the cache is preferred")


class Search(Base):
    def search(self, answer, stem=f"{BRETT} (JUE) [b1]", args=(), infos=(404, b"", None), media=(200, PNG, None)):
        self.rom("MD", stem + ".bin", b"bad" * 100)
        h = t.NesSnes.ss_http(self, self.dat("MD", ("Other (USA)", "DEADBEEF")))
        h.prefix = {fl.SS_API + "ssuserInfos.php": (200, b"{}", None), fl.SS_API + "jeuRecherche.php": answer,
                    fl.SS_API + "jeuInfos.php": infos,
                    "https://x.test/us.png": media, "https://x.test/": (200, OTHER, None)}
        report = os.path.join(self.tmp, "r.tsv")
        ctx = fl.Ctx(http=h, env=dict(SS_ENV, SLOT_LABELS_CACHE=os.path.join(self.tmp, "cache")), sleep=lambda s: None)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            stats = fl.main(["--card", self.card, "--only", "MD", "--by-name", "--report", report, *args], ctx)
        self.out, self.http, self.report = out.getvalue(), h, fl.slurp(report, "r").splitlines()[1:]
        return stats

    def asked(self):
        return [c for c in self.http.calls if c.startswith(fl.SS_API + "jeuRecherche.php")]

    def test_an_exact_title_in_any_region_is_taken_with_the_crc_paths_media(self):
        stats = self.search(jeux(game("31337", ("ss", "Brett Hull Hockey '95"), ("jp", "Brett Hull Hockey 95 J"))))
        self.assertEqual(stats["by_name"], 1)
        self.assertEqual(self.label("MD", f"{BRETT} (JUE) [b1]"), PNG, "support-texture, us first")
        self.assertEqual(self.report, [f"MD\t{BRETT} (JUE) [b1]\tname\tss:31337"])
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(self.asked()[0]).query)
        self.assertEqual((q["recherche"], q["systemeid"]), ([BRETT], ["1"]))
        self.assertNotIn("secret", self.out)
        self.search(jeux(game("31337", ("ss", "Brett Hull Hockey '95"))))
        self.assertEqual(self.asked(), [], "a rerun answers from the cache")

    def test_a_near_title_is_no_confident_match_and_downloads_nothing(self):
        stats = self.search(jeux(game("1", ("us", "Brett Hull Hockey")), game("2", ("us", "NHL Hockey 95"))))
        self.assertEqual((stats["no_match"], stats["by_name"]), (1, 0))
        self.assertIsNone(self.label("MD", f"{BRETT} (JUE) [b1]"))
        self.assertFalse(any(c.startswith("https://x.test/") for c in self.http.calls))
        self.assertEqual(self.report, [f"MD\t{BRETT} (JUE) [b1]\tno confident match\t"])

    def test_two_games_with_the_title_or_another_system_are_not_guessed(self):
        self.assertEqual(self.search(jeux(game("1", ("us", BRETT)), game("2", ("eu", BRETT))))["no_match"], 1)
        self.setUp()
        self.assertEqual(self.search(jeux(game("1", ("us", BRETT), system="2")))["no_match"], 1)

    def test_an_empty_reply_is_no_confident_match(self):
        for answer in (jeux(), jeux({})):
            self.setUp()
            self.assertEqual(self.search(answer)["no_match"], 1)

    def test_a_result_without_medias_is_completed_by_game_id(self):
        jeu = (200, json.dumps({"response": {"jeu": game("7", ("us", BRETT))}}).encode(), None)
        stats = self.search(jeux(game("7", ("us", BRETT), medias=False)), infos=jeu)
        infos = [c for c in self.http.calls if c.startswith(fl.SS_API + "jeuInfos.php")]
        self.assertEqual((len(infos), stats["by_name"]), (1, 1))
        self.assertIn("gameid=7", infos[0])
        self.assertEqual(self.label("MD", f"{BRETT} (JUE) [b1]"), PNG)

    def test_a_dry_run_never_searches(self):
        stats = self.search(jeux(game("1", ("us", BRETT))), args=("--dry-run",))
        self.assertEqual((stats["name_skipped"], len(self.asked())), (1, 0))
        self.assertIn("not searched by name", self.out)


class Ps1Sibling(Base):
    def test_a_disc_with_no_art_copies_the_siblings_cover_and_disc_label(self):
        self.rom("PS1", "Crash Bandicoot (USA) (Hack).chd", b"chd" * 10)
        for sub, body in (("", PNG), ("disc", OTHER)):
            d = os.path.join(self.card, "Labels", "PS1", sub)
            os.makedirs(d, exist_ok=True)
            fl.spit(os.path.join(d, "Crash Bandicoot (USA).png"), body)
        stats = self.run_tool({}, ["--card", self.card, "--only", "PS1", "--by-name"])
        self.assertEqual(stats["sibling"], 1)
        self.assertEqual(self.label("PS1", "Crash Bandicoot (USA) (Hack)"), PNG)
        self.assertEqual(self.label("PS1", "disc/Crash Bandicoot (USA) (Hack)"), OTHER)


class SearchErrors(Base):
    search, asked = Search.search, Search.asked

    def test_a_garbled_reply_is_one_error_and_the_run_goes_on(self):
        self.rom("MD", "Jungle Strike (UEJ) [p1][!].bin", b"js" * 100)
        stats = self.search((200, b"Erreur de login : Verifier vos identifiants developpeur !", None))
        self.assertEqual((stats["errors"], len(self.asked())), (2, 2), "both ROMs asked, each failed alone")
        self.assertIn("error  MD/Jungle Strike (UEJ) [p1][!]", self.out)
        self.assertIn("Summary", self.out)

    def test_a_media_that_is_not_a_png_is_an_error_and_writes_nothing(self):
        self.rom("MD", "Jungle Strike (UEJ) [p1][!].bin", b"js" * 100)
        stats = self.search(jeux(game("9", ("us", BRETT))), media=(200, b"NOMEDIA", None))
        self.assertEqual((stats["errors"], stats["no_match"]), (1, 1))
        self.assertIsNone(self.label("MD", f"{BRETT} (JUE) [b1]"))
