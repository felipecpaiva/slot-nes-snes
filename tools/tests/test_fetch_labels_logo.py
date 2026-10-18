"""tools/fetch-labels.py --by-name --logo-fallback, offline: matching a ROM to a libretro Named_Logos name, and the
"logo fallback" outcome on a card with a fake HTTP layer and a fake renderer.

    python3 -m unittest tools/tests/test_fetch_labels_logo.py
"""
import contextlib
import io
import os
import urllib.parse

from tools.tests.test_fetch_labels import PNG, SS_ENV, Base, fl
from tools.tests.test_fetch_labels_by_name import game, jeu_answer, jeux
from tools.tests import test_fetch_labels as t

NES = "Nintendo - Nintendo Entertainment System"
INDEX_URL = fl.LOGOS + urllib.parse.quote(NES) + "/Named_Logos/"
LOGO = fl.PNG + b"logo" * 20
NAMES = ["Advanced Dungeons _ Dragons - Hillsfar (USA)", "Advanced Dungeons _ Dragons - Hillsfar (Japan)",
         "8 Eyes (Japan)", "8 Eyes (USA)", "Zen - Intergalactic Ninja (USA)",
         "Teenage Mutant Ninja Turtles II - The Arcade Game (USA)",
         "Teenage Mutant Ninja Turtles III - The Manhattan Project (USA)"]


def listing(names):
    rows = "".join(f'<a href="{urllib.parse.quote(n)}.png">{n}.png</a>\n' for n in names)
    return f'<a href="?C=N;O=D">Name</a><a href="/{urllib.parse.quote(NES)}/">Parent</a>\n{rows}'.encode()


def logo_url(name):
    return fl.LOGOS + urllib.parse.quote(f"{NES}/Named_Logos/{name}.png")


class Match(Base):
    def index(self):
        ctx = fl.Ctx(http=t.FakeHttp({INDEX_URL: (200, listing(NAMES), None)}),
                     env={"SLOT_LABELS_CACHE": os.path.join(self.tmp, "cache")}, sleep=lambda s: None)
        return fl.logo_index(ctx, "NES")

    def test_a_title_meets_its_logo_and_the_region_picks_the_file(self):
        idx = self.index()
        self.assertEqual(fl.pick_logo(idx, "Advanced Dungeons & Dragons - Hillsfar (U) [b1]", "NES"),
                         "Advanced Dungeons _ Dragons - Hillsfar (USA)", "libretro writes & as _")
        self.assertEqual(fl.pick_logo(idx, "8 Eyes (J)", "NES"), "8 Eyes (Japan)")
        self.assertEqual(fl.pick_logo(idx, "8 Eyes (U) [!]", "NES"), "8 Eyes (USA)")
        self.assertIsNone(fl.pick_logo(idx, "8 Eyes 2 (U)", "NES"))

    def test_a_cut_name_takes_the_one_title_starting_with_it_and_never_guesses_between_two(self):
        idx = self.index()
        self.assertEqual(fl.pick_logo(idx, "Teenage Mutant Ninja Turtles III - The M", "NES"),
                         "Teenage Mutant Ninja Turtles III - The Manhattan Project (USA)")
        self.assertIsNone(fl.pick_logo(idx, "Teenage Mutant Ninja Turtles I", "NES"), "II and III both start so")

    def test_hacks_are_told_apart(self):
        self.assertTrue(fl.is_hack("8 Eyes (U) [h1]"))
        self.assertTrue(fl.is_hack("Zen (U) (Hack)"))
        self.assertFalse(fl.is_hack("8 Eyes (J) [T+Eng]"))
        self.assertFalse(fl.is_hack("8 Eyes (U) [b1]"))

    def test_a_system_with_no_named_logos_has_an_empty_index(self):
        ctx = fl.Ctx(http=t.FakeHttp({}), env={"SLOT_LABELS_CACHE": os.path.join(self.tmp, "cache")},
                     sleep=lambda s: None)
        self.assertEqual(fl.logo_index(ctx, "GG"), {})


class Fallback(Base):
    def go(self, args=(), routes=None, env=None, http=None):
        self.rendered = []
        http = http or t.FakeHttp(dict(self.dat("NES", ("Other (USA)", "DEADBEEF")), **(routes or {
            INDEX_URL: (200, listing(NAMES), None), logo_url("8 Eyes (USA)"): (200, LOGO, None)})))
        ctx = fl.Ctx(http=http, env=dict(env or {}, SLOT_LABELS_CACHE=os.path.join(self.tmp, "cache")),
                     sleep=lambda s: None)
        ctx.render = lambda system, stem, logo: self.rendered.append((system, stem, logo)) or PNG
        report = os.path.join(self.tmp, "r.tsv")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            stats = fl.main(["--card", self.card, "--only", "NES", "--by-name", "--report", report, *args], ctx)
        self.out, self.http, self.report = out.getvalue(), http, fl.slurp(report, "r").splitlines()[1:]
        return stats

    def test_a_bare_rom_gets_a_logo_label_and_one_report_row(self):
        self.rom("NES", "8 Eyes (U) [b2].nes", b"bad" * 50)
        self.rom("NES", "Nothing Like It (U).nes", b"zzz" * 50)
        stats = self.go(["--logo-fallback"])
        self.assertEqual(self.label("NES", "8 Eyes (U) [b2]"), PNG)
        self.assertEqual(self.rendered, [("NES", "8 Eyes (U) [b2]", LOGO)])
        self.assertEqual((stats["logo"], stats["name_skipped"]), (1, 1))
        self.assertEqual(self.report, ["NES\t8 Eyes (U) [b2]\tlogo fallback\tlibretro:8 Eyes (USA)\tlogo",
                                       "NES\tNothing Like It (U)\tnot searched\tno SS_DEVID/SS_DEVPASSWORD\t"])
        self.assertIn("logo fallback  NES/8 Eyes (U) [b2] (libretro:8 Eyes (USA), logo)", self.out)
        self.assertIn("logo fallback", self.out.split("Summary")[1])
        self.setUp()
        self.rom("NES", "8 Eyes (U) [b2].nes", b"bad" * 50)
        self.assertEqual(self.go()["logo"], 0, "off by default")
        self.assertIsNone(self.label("NES", "8 Eyes (U) [b2]"))
        self.assertFalse(any(c.startswith(fl.LOGOS) for c in self.http.calls))

    def test_a_dry_run_matches_from_the_index_and_writes_renders_and_downloads_nothing(self):
        self.rom("NES", "8 Eyes (U).nes", b"x" * 50)
        stats = self.go(["--logo-fallback", "--dry-run"])
        self.assertEqual(stats["logo"], 1)
        self.assertEqual(self.rendered, [])
        self.assertFalse(os.path.exists(os.path.join(self.card, "Labels")))
        self.assertNotIn(logo_url("8 Eyes (USA)"), self.http.calls)

    def test_a_hack_gets_its_parents_logo_only_through_an_alias(self):
        self.rom("NES", "8 Eyes (U) [h1].nes", b"h" * 50)
        self.assertEqual(self.go(["--logo-fallback"])["logo"], 0)
        self.assertIsNone(self.label("NES", "8 Eyes (U) [h1]"))
        al = os.path.join(self.tmp, "a.tsv")
        fl.spit(al, "NES\t8 Eyes (U) [h1]\tsibling:8 Eyes (U)\n", "w")
        self.assertEqual(self.go(["--logo-fallback", "--aliases", al])["logo"], 1)
        self.assertEqual(self.label("NES", "8 Eyes (U) [h1]"), PNG)
        self.assertEqual(self.report, ["NES\t8 Eyes (U) [h1]\tlogo fallback\tlibretro:8 Eyes (USA)\tlogo"])

    def test_a_game_matched_by_name_with_no_art_takes_its_screenscraper_wheel(self):
        self.rom("NES", "Mystery Quest (U) [b1].nes", b"m" * 50)
        g = game("77", ("us", "Mystery Quest"), system="3", medias=False)
        g["medias"] = [{"type": "wheel", "region": "wor", "url": "https://x.test/wheel.png", "format": "png"}]
        h = t.NesSnes.ss_http(self, dict(self.dat("NES", ("Other (USA)", "DEADBEEF")),
                                         **{INDEX_URL: (200, listing(NAMES), None)}))
        h.prefix = {fl.SS_API + "ssuserInfos.php": (200, b"{}", None), fl.SS_API + "jeuRecherche.php": jeux(g),
                    fl.SS_API + "jeuInfos.php": jeu_answer(g), "https://x.test/wheel.png": (200, LOGO, None)}
        stats = self.go(["--logo-fallback"], env=SS_ENV, http=h)
        self.assertEqual((stats["logo"], stats["name_no_art"]), (1, 0))
        self.assertEqual(self.rendered, [("NES", "Mystery Quest (U) [b1]", LOGO)])
        self.assertEqual(self.report, ["NES\tMystery Quest (U) [b1]\tlogo fallback\tss:77 wheel\tlogo"])

    def test_a_rom_skipped_by_limit_gets_no_logo_so_a_later_run_still_searches_it(self):
        self.rom("NES", "8 Eyes (U) [b1].nes", b"a" * 50)
        self.rom("NES", "Zen - Intergalactic Ninja (U).nes", b"b" * 50)
        h = t.NesSnes.ss_http(self, dict(self.dat("NES", ("Other (USA)", "DEADBEEF")),
                                         **{INDEX_URL: (200, listing(NAMES), None),
                                            logo_url("8 Eyes (USA)"): (200, LOGO, None),
                                            logo_url("Zen - Intergalactic Ninja (USA)"): (200, LOGO, None)}))
        h.prefix = {fl.SS_API + "ssuserInfos.php": (200, b"{}", None), fl.SS_API + "jeuRecherche.php": jeux()}
        self.go(["--logo-fallback", "--limit", "1"], env=SS_ENV, http=h)
        self.assertEqual(self.report, ["NES\t8 Eyes (U) [b1]\tlogo fallback\tlibretro:8 Eyes (USA)\tlogo",
                                       "NES\tZen - Intergalactic Ninja (U)\tnot searched\t--limit 1\t"])
        self.assertIsNone(self.label("NES", "Zen - Intergalactic Ninja (U)"), "it has a logo, but was not searched")

    def test_a_logo_host_that_is_down_leaves_the_rom_bare_not_an_error(self):
        self.rom("NES", "8 Eyes (U).nes", b"x" * 50)

        class Down(t.FakeHttp):
            def get(s, url):
                if url.startswith(fl.LOGOS):
                    raise fl.Fail("network error")
                return super().get(url)
        stats = self.go(["--logo-fallback"], http=Down(self.dat("NES", ("Other (USA)", "DEADBEEF"))))
        self.assertEqual((stats["logo"], stats["errors"], stats["name_skipped"]), (0, 0, 1))
        self.assertIn("no logo for NES/8 Eyes (U): network error", self.out)

    def test_the_flag_needs_by_name(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            fl.main(["--card", self.tmp, "--logo-fallback"])
