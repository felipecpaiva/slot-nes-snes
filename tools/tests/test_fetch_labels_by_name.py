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
        self.assertIn(f"matched by sibling  MD/{BRETT} (J) [b1] ({BRETT} (J))", self.out)
        self.assertEqual([c for c in self.http.calls if not c.startswith(fl.DAT)], [])
        shell = fl.slurp(os.path.join(self.card, "Labels", "cart_shell.txt"), "r")
        self.assertIn(f"{BRETT} (J) [b1] = megadrive 26242a solid", shell)
        self.assertEqual(fl.slurp(report, "r").splitlines(), [
            "system\tstem\toutcome\tsource\tmedia", f"MD\t{BRETT} (J) [b1]\tsibling\t{BRETT} (J)\t",
            "MD\tNothing Like It (U)\tnot searched\tno SS_DEVID/SS_DEVPASSWORD\t"])

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
        self.assertIn("matched by sibling  NES/Tetris (U) [h1] (Tetris (U) [!])", self.out)
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
    def search(self, answer, stem=f"{BRETT} (JUE) [b1]", args=(), infos=(404, b"", None), media=(200, PNG, None),
               dat=(("Other (USA)", "DEADBEEF"),), body=b"bad" * 100):
        self.rom("MD", stem + ".bin", body)
        h = t.NesSnes.ss_http(self, self.dat("MD", *dat))
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
        self.assertEqual(self.report, [f"MD\t{BRETT} (JUE) [b1]\tname\tss:31337\tsupport-texture"])
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
        self.assertEqual(self.report, [f"MD\t{BRETT} (JUE) [b1]\tno confident match\t\t"])

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


def jeu_answer(g):
    return (200, json.dumps({"response": {"jeu": g}}).encode(), None)


BOX_ONLY = [{"type": "wheel", "region": "wor", "url": "https://x.test/wheel.png", "format": "png"},
            {"type": "box-2D", "region": "jp", "url": "https://x.test/box-jp.png", "format": "png"},
            {"type": "box-2D", "region": "wor", "url": "https://x.test/box-wor.png", "format": "png"}]


class Round2Names(Base):
    def test_underscores_and_n_and_the_dot_the_forms_meet(self):
        for a, b in [("sonic3_and_knuckles", "Sonic 3 & Knuckles"), ("street_fighter2_turbo", "Street Fighter2 Turbo"),
                     ("Snake Rattle'n Roll (U)", "Snake Rattle 'n' Roll"), ("Rock n' Roll Racing", "Rock & Roll Racing"),
                     ("Ed. Edd n Eddy - Jawbreakers! (U) [hI]", "Ed, Edd 'n Eddy: Jawbreakers!"),
                     ("Fairly Odd Parents!. The - Breakin' da Rules", "The Fairly OddParents! Breakin' da Rules")]:
            self.assertEqual(fl.title_key(a), fl.title_key(b), (a, b))
        self.assertNotEqual(fl.title_key("Sonic 2 in Paynt by Monkeyman (Hack)"), fl.title_key("Sonic 2 in Paynt"))

    def test_search_queries_drop_an_author_a_cut_word_and_32x(self):
        self.assertEqual(fl.attempts("Sonic 2 in Paynt by Monkeyman (Hack) [f1]", "MD"),
                         [(1, "Sonic 2 in Paynt", fl.title_key("Sonic 2 in Paynt by Monkeyman"), False)])
        self.assertEqual(fl.attempts("Dora the Explorer - The Search for Pi", "GBA"),
                         [(12, "Dora the Explorer - The Search for", "doratheexplorerthesearchforpi", True)])
        self.assertEqual(fl.attempts("Cosmic Carnage 32X (A) [!]", "MD"),
                         [(19, "Cosmic Carnage", "cosmiccarnage", False), (1, "Cosmic Carnage 32X", "cosmiccarnage32x", False)])
        self.assertFalse(fl.is_cut("Crouching Tiger. Hidden Dragon (U) (M"), "tagged: never a prefix match")
        self.assertFalse(fl.is_cut("Short Title"))

    def test_a_cut_name_takes_one_prefix_game_and_never_two(self):
        key = fl.title_key("Dora the Explorer - The Search for Pi")
        one = [game("5", ("us", "Dora the Explorer: The Search for Pirate Pig's Treasure"), system="12")]
        self.assertEqual(fl.judge(one, key, "12", True, "GBA").get("game", {}).get("id"), "5")
        self.assertNotIn("game", fl.judge(one, key, "12", False, "GBA"), "only a cut name matches a prefix")
        two = one + [game("6", ("us", "Dora the Explorer: The Search for Pirate Treasure"), system="12")]
        self.assertEqual(fl.judge(two, key, "12", True, "GBA")["why"], "several ids (5, 6)")


class Round2(Base):
    search, asked = Search.search, Search.asked
    ss_http = t.NesSnes.ss_http

    def test_no_label_scan_falls_back_to_the_world_box_never_a_wheel(self):
        g = game("8", ("us", BRETT))
        g["medias"] = BOX_ONLY
        stats = self.search(jeux(g))
        self.assertEqual(stats["by_name"], 1)
        self.assertEqual(self.report, [f"MD\t{BRETT} (JUE) [b1]\tname\tss:8\tbox-2D"])
        self.assertTrue(any(c.startswith("https://x.test/box-wor.png") for c in self.http.calls))
        self.assertFalse(any("wheel" in c for c in self.http.calls))
        self.setUp()
        g["medias"] = BOX_ONLY[:1]
        self.assertEqual(self.search(jeux(g))["name_no_art"], 1)

    def test_a_crc_with_no_label_scan_takes_the_box_only_with_by_name(self):
        body = b"known" * 50
        jeu = game("44", ("us", BRETT))
        jeu["medias"] = BOX_ONLY
        stats = self.search(jeux(), infos=jeu_answer(jeu), dat=((f"{BRETT} (USA)", crc(body)),), body=body)
        self.assertEqual((stats["missing"], stats["crc_box"]), (1, 1))
        self.assertEqual(self.report, [f"MD\t{BRETT} (JUE) [b1]\tcrc box\tcrc:{crc(body)}\tbox-2D"])
        self.assertEqual(self.label("MD", f"{BRETT} (JUE) [b1]"), OTHER)
        self.assertEqual(self.asked(), [], "the CRC game is enough, no name search")
        self.assertFalse(any("secret" in fl.slurp(os.path.join(dp, f), "r") for dp, _, fs in
                             os.walk(os.path.join(self.tmp, "cache")) for f in fs if f.endswith(".json")))

    def test_the_default_run_keeps_missing_as_missing(self):
        body = b"known" * 50
        self.rom("MD", f"{BRETT} (U).bin", body)
        stats = t.NesSnes.run_ss(self, "MD", self.dat("MD", (f"{BRETT} (USA)", crc(body))), {},
                                 jeu_answer({"medias": BOX_ONLY}), ["--card", self.card, "--only", "MD"])
        self.assertEqual((stats["missing"], stats["written"]), (1, 0))

    def test_round_1_none_is_asked_again_and_a_round_1_match_is_kept(self):
        d = os.path.join(self.tmp, "cache", "ss", "MD", "name")
        os.makedirs(d)
        fl.spit(os.path.join(d, fl.title_key(BRETT) + ".id"), "", "w")
        self.assertEqual(self.search(jeux(game("3", ("us", BRETT))))["by_name"], 1)
        self.assertEqual(len(self.asked()), 1)
        self.setUp()
        d = os.path.join(self.tmp, "cache", "ss", "MD", "name")
        os.makedirs(os.path.join(d, "support-texture"))
        fl.spit(os.path.join(d, fl.title_key(BRETT) + ".id"), "77", "w")
        fl.spit(os.path.join(d, "support-texture", "77.png"), PNG)
        self.assertEqual(self.search(jeux())["by_name"], 1)
        self.assertEqual(self.report, [f"MD\t{BRETT} (JUE) [b1]\tname\tss:77\tsupport-texture"])
        self.assertEqual([c for c in self.http.calls if c.startswith(fl.SS_API)], [])

    def test_a_32x_name_is_asked_under_system_19_first(self):
        g = game("90", ("wor", "Cosmic Carnage"), system="19")
        stats = self.search(jeux(g), stem="Cosmic Carnage 32X (A) [!]")
        self.assertEqual(stats["by_name"], 1)
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(self.asked()[0]).query)
        self.assertEqual((q["systemeid"], q["recherche"]), (["19"], ["Cosmic Carnage"]))

    def test_suggest_names_the_near_game_and_writes_no_art(self):
        sug = os.path.join(self.tmp, "s.tsv")
        stats = self.search(jeux(game("12", ("us", "Brett Hull Hockey 95 Special"))), args=("--suggest", sug))
        self.assertEqual(stats["no_match"], 1)
        self.assertIsNone(self.label("MD", f"{BRETT} (JUE) [b1]"))
        self.assertEqual(fl.slurp(sug, "r").splitlines()[1:], [
            f"MD\t{BRETT} (JUE) [b1]\tss:12\tBrett Hull Hockey 95 Special\thack or bad dump; subtitle differs"])

    def test_a_suggest_file_applies_unchanged_as_aliases(self):
        sug = os.path.join(self.tmp, "s.tsv")
        stem = 'Brett Hull "95" Hockey (JUE) [b1] '
        self.search(jeux(game("12", ("us", "Brett Hull 95 Hockey Special"))), stem=stem, args=("--suggest", sug))
        with open(sug, "a", encoding="utf-8") as f:
            f.write("MD\tNothing Here\t\t\tno results\n")
        self.assertIn('"', fl.slurp(sug, "r"), "the stem is quoted")
        self.setUp()
        g = game("12", ("us", "Brett Hull 95 Hockey Special"))
        self.assertEqual(self.search(jeux(), stem=stem, args=("--aliases", sug), infos=jeu_answer(g))["alias"], 1)
        self.assertIsNotNone(self.label("MD", stem))

    def test_aliases_force_a_game_or_a_sibling(self):
        al = os.path.join(self.tmp, "a.tsv")
        fl.spit(al, f"# approved\nMD\t{BRETT} (JUE) [b1]\tss:555\n", "w")
        g = game("555", ("us", "NHL Hockey"))
        stats = self.search(jeux(), args=("--aliases", al), infos=jeu_answer(g))
        self.assertEqual(stats["alias"], 1)
        self.assertEqual(self.report, [f"MD\t{BRETT} (JUE) [b1]\talias\tss:555\tsupport-texture"])
        self.assertEqual(self.asked(), [])
        self.setUp()
        os.makedirs(os.path.join(self.card, "Labels", "MD"))
        fl.spit(os.path.join(self.card, "Labels", "MD", "NHL 95 (U).png"), OTHER)
        fl.spit(al, f"MD\t{BRETT} (JUE) [b1]\tsibling:NHL 95 (U)\n", "w")
        self.assertEqual(self.search(jeux(), args=("--aliases", al))["alias"], 1)
        self.assertEqual(self.label("MD", f"{BRETT} (JUE) [b1]"), OTHER)


class Round2Sibling(Base):
    def test_a_cut_name_copies_the_one_sibling_its_title_starts(self):
        self.rom("GBA", "Dora the Explorer - The Search for Pi.gba", b"cut" * 30)
        self.rom("GBA", "Mucha Lucha! - Mascaritas of the Lost.gba", b"cut2" * 30)
        d = os.path.join(self.card, "Labels", "GBA")
        os.makedirs(d)
        fl.spit(os.path.join(d, "Dora the Explorer - The Search for Pirate Pig's Treasure (U).png"), PNG)
        fl.spit(os.path.join(d, "Mucha Lucha! - Mascaritas of the Lost Code (U).png"), PNG)
        fl.spit(os.path.join(d, "Mucha Lucha! - Mascaritas of the Lost Code (E).png"), PNG)
        fl.spit(os.path.join(d, "Mucha Lucha! - Mascaritas of the Lost Temple (U).png"), PNG)
        stats = self.run_tool(self.dat("GBA", ("Other (USA)", "DEADBEEF")), ["--card", self.card, "--only", "GBA", "--by-name"])
        self.assertEqual(stats["sibling"], 1)
        self.assertEqual(self.label("GBA", "Dora the Explorer - The Search for Pi"), PNG)
        self.assertIsNone(self.label("GBA", "Mucha Lucha! - Mascaritas of the Lost"), "two titles start with it")
