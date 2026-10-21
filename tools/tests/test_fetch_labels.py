"""T49: tools/fetch-labels.py, offline. Fixture mini-dats, a fake HTTP layer and a fake adb.

    python3 -m unittest tools/tests/test_fetch_labels.py
"""
import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import tempfile
import unittest
import urllib.parse
import zipfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("fetch_labels", os.path.join(HERE, "..", "fetch-labels.py"))
fl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fl)

PNG = fl.PNG + b"label" * 40
INES = b"NES\x1a" + bytes(12)


def crc(b):
    return f"{zlib.crc32(b) & 0xffffffff:08X}"


def dat_text(*games):
    return "".join(f'game (\n\tname "{n}"\n\trom ( name "{n}.x" size 1 crc {c} )\n)\n' for n, c in games)


class FakeHttp:
    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def get(self, url):
        self.calls.append(url)
        r = self.routes.get(url, (404, b"", None))
        if isinstance(r, list):
            r = r.pop(0) if len(r) > 1 else r[0]
        return r


class FakeAdb:
    """Just enough of adb. ls is a trap: the device's ls colours names, so only the glob may be used."""

    def __init__(self, files):
        self.files, self.pushed, self.cmds = dict(files), [], []

    def __call__(self, *a):
        self.cmds.append(a)
        if a[0] == "devices":
            return 0, "List of devices attached\nabc\tdevice\n"
        if a[0] == "shell":
            cmd = a[1]
            assert not cmd.startswith("ls"), "ls adds colour codes on the device"
            m = re.match(r"for f in '(.*)'/\*;", cmd)
            if m:
                d = m.group(1).rstrip("/") + "/"
                return 0, "".join(p[len(d):] + "\r\n" for p in sorted(self.files)
                                  if p.startswith(d) and "/" not in p[len(d):])
            return 0, ""
        if a[0] == "pull":
            fl.spit(a[2], self.files[a[1]])
            return 0, ""
        if a[0] == "push":
            src, dest = a[1], a[2].rstrip("/")
            if os.path.isdir(src.rstrip("/.")):
                base = src.rstrip("/.")
                for n in os.listdir(base):
                    self.files[f"{dest}/{n}"] = fl.slurp(os.path.join(base, n))
                    self.pushed.append(f"{dest}/{n}")
            else:
                self.files[dest] = fl.slurp(src)
                self.pushed.append(dest)
            return 0, ""
        return 1, "bad"


def slot_parses(line):
    """slot's grammar (cart_shell.rs ShellChoice::parse): outline word, 6 hex digits, finish, nothing else."""
    w = line.split()
    return (len(w) == 3 and w[0] in {"auto", "notched", "rounded", "nes", "famicom", "snes", "sfc", "gg", "sms",
                                     "segacard", "megadrive", "genesis"}
            and re.fullmatch(r"[0-9a-fA-F]{6}", w[1]) is not None and w[2] in {"solid", "clear", "glitter"})


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.card = os.path.join(self.tmp, "card")

    def rom(self, system, name, data):
        d = os.path.join(self.card, "Games", system)
        os.makedirs(d, exist_ok=True)
        fl.spit(os.path.join(d, name), data)

    def run_tool(self, routes, args, env=None, adb=None):
        http = FakeHttp(routes)
        ctx = fl.Ctx(http=http, adb=adb, env=dict(env or {}, SLOT_LABELS_CACHE=os.path.join(self.tmp, "cache")),
                     sleep=lambda s: None)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            stats = fl.main(args, ctx)
        self.out, self.http = out.getvalue(), http
        return stats

    def dat(self, system, *games):
        return {fl.DAT + urllib.parse.quote(n) + ".dat": (200, dat_text(*games).encode(), None)
                for n in fl.SYSTEMS[system][2][:1]}

    def label(self, system, stem):
        p = os.path.join(self.card, "Labels", system, stem + ".png")
        return fl.slurp(p) if os.path.exists(p) else None


SS_ENV = {"SS_DEVID": "d", "SS_DEVPASSWORD": "p", "SS_SSID": "u", "SS_SSPASSWORD": "secret"}
JEU = {"response": {"jeu": {"medias": [{"type": "support-texture", "region": "us", "url": "https://x.test/m.png"}]}}}

SMS_JEU = {"response": {"jeu": {"medias": [
    {"type": "support-texture", "region": "us", "url": "https://x.test/scan.png"},
    {"type": "ss", "region": "wor", "url": "https://x.test/shot.png"},
    {"type": "box-2D-side", "region": "us", "url": "https://x.test/side.png"},
    {"type": "box-2D-back", "region": "us", "url": "https://x.test/back.png"},
    {"type": "box-2D", "region": "jp", "url": "https://x.test/box-jp.png", "format": "png"},
    {"type": "box-2D", "region": "eu", "url": "https://x.test/box-eu.png", "format": "png"},
    {"type": "box-2D", "region": "us", "url": "https://x.test/box-us.png", "format": "png"}]}}}


class NesSnes(Base):
    def ss_http(self, routes):
        """FakeHttp matches exact URLs, but SS urls carry credentials: route by endpoint prefix instead."""
        class H(FakeHttp):
            def get(s, url):
                s.calls.append(url)
                for prefix, r in s.prefix.items():
                    if url.startswith(prefix):
                        return r
                return s.routes.get(url, (404, b"", None))
        h = H(routes)
        h.prefix = {}
        return h

    def run_ss(self, system, dat_routes, ss_user, jeu, args, media=(200, PNG, None), env=SS_ENV):
        h = self.ss_http(dat_routes)
        h.prefix = {fl.SS_API + "ssuserInfos.php": (200, json.dumps(ss_user).encode(), None),
                    fl.SS_API + "jeuInfos.php": jeu,
                    "https://x.test/": media}
        ctx = fl.Ctx(http=h, env=dict(env, SLOT_LABELS_CACHE=os.path.join(self.tmp, "cache")), sleep=lambda s: None)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            stats = fl.main(args, ctx)
        self.out, self.http = out.getvalue(), h
        return stats

    def test_headered_nes_rom_matches_by_crc_without_the_header(self):
        body = b"prg-data" * 100
        self.rom("NES", "My Game.nes", INES + body)
        r = self.dat("NES", ("Super Game (USA)", crc(body)))
        stats = self.run_ss("NES", r, {}, (200, json.dumps(JEU).encode(), None), ["--card", self.card, "--only", "NES"])
        self.assertEqual((stats["matched"], stats["written"], stats["unknown"]), (1, 1, 0))
        self.assertEqual(self.label("NES", "My Game"), PNG)
        self.assertIn("renamed?", self.out)

    def test_a_developer_only_login_never_asks_for_member_limits(self):
        body = b"d" * 64
        self.rom("NES", "D.nes", body)
        r = self.dat("NES", ("D (USA)", crc(body)))
        dev_only = {"SS_DEVID": "d", "SS_DEVPASSWORD": "p"}
        stats = self.run_ss("NES", r, {}, (200, json.dumps(JEU).encode(), None),
                            ["--card", self.card, "--only", "NES"], env=dev_only)
        self.assertEqual((stats["written"], stats["errors"]), (1, 0))
        self.assertFalse(any("ssuserInfos" in c for c in self.http.calls))

    def test_nes_whole_file_crc_wins_when_the_dat_has_the_header(self):
        data = INES + b"x" * 64
        self.rom("NES", "A.nes", data)
        r = self.dat("NES", ("A (USA)", crc(data)))
        stats = self.run_ss("NES", r, {}, (200, json.dumps(JEU).encode(), None), ["--card", self.card, "--only", "NES"])
        self.assertEqual(stats["written"], 1)

    def test_snes_copier_header_is_stripped(self):
        body = b"s" * 1024
        self.rom("SNES", "Zelda.smc", bytes(512) + body)
        r = self.dat("SNES", ("Zelda (Japan)", crc(body)))
        stats = self.run_ss("SNES", r, {}, (200, json.dumps(JEU).encode(), None), ["--card", self.card, "--only", "SNES"])
        self.assertEqual((stats["matched"], stats["written"]), (1, 1))
        text = fl.slurp(os.path.join(self.card, "Labels", "cart_shell.txt"), "r")
        self.assertEqual(text, "Zelda = sfc 949696 solid\n")

    def test_unknown_crc_is_reported_and_nothing_is_written(self):
        self.rom("SNES", "Mystery.sfc", b"zz" * 512)
        r = self.dat("SNES", ("Other (USA)", "DEADBEEF"))
        stats = self.run_ss("SNES", r, {}, (200, json.dumps(JEU).encode(), None), ["--card", self.card, "--only", "SNES"])
        self.assertEqual((stats["unknown"], stats["written"]), (1, 0))
        self.assertIsNone(self.label("SNES", "Mystery"))
        self.assertFalse(any(c.startswith(fl.SS_API + "jeuInfos") for c in self.http.calls))

    def test_screenscraper_404_is_missing_and_not_asked_again(self):
        body = b"b" * 64
        self.rom("NES", "G.nes", body)
        r = self.dat("NES", ("G (USA)", crc(body)))
        args = ["--card", self.card, "--only", "NES"]
        stats = self.run_ss("NES", r, {}, (404, b"", None), args)
        self.assertEqual((stats["missing"], stats["errors"]), (1, 0))
        self.run_ss("NES", r, {}, (404, b"", None), args)
        asked = [c for c in self.http.calls if c.startswith(fl.SS_API + "jeuInfos")]
        self.assertEqual(asked, [], "the .none marker keeps the quota")

    def test_quota_exhausted_stops_cleanly_and_keeps_what_was_written(self):
        a, b = b"a" * 64, b"b" * 64
        self.rom("NES", "A.nes", a)
        self.rom("NES", "B.nes", b)
        r = self.dat("NES", ("A (USA)", crc(a)), ("B (USA)", crc(b)))
        h = self.ss_http(r)
        answers = [(200, json.dumps(JEU).encode(), None), (430, b"", None)]
        h.prefix = {fl.SS_API + "ssuserInfos.php": (200, b"{}", None), "https://x.test/": (200, PNG, None)}
        orig = h.get

        def get(url):
            if url.startswith(fl.SS_API + "jeuInfos"):
                h.calls.append(url)
                return answers.pop(0)
            return orig(url)
        h.get = get
        ctx = fl.Ctx(http=h, env=dict(SS_ENV, SLOT_LABELS_CACHE=os.path.join(self.tmp, "cache")), sleep=lambda s: None)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            stats = fl.main(["--card", self.card, "--only", "NES"], ctx)
        self.assertEqual((stats["written"], stats["missing"]), (1, 1))
        self.assertIn("Rerun to resume", out.getvalue())
        self.assertNotIn("secret", out.getvalue())
        self.assertEqual(len([c for c in h.calls if "jeuInfos" in c]), 2)

    def test_existing_label_is_skipped_case_insensitively_without_any_request(self):
        body = b"c" * 64
        self.rom("NES", "Game.nes", body)
        os.makedirs(os.path.join(self.card, "Labels", "NES"))
        fl.spit(os.path.join(self.card, "Labels", "NES", "GAME.PNG"), b"mine")
        r = self.dat("NES", ("Game (USA)", crc(body)))
        stats = self.run_ss("NES", r, {}, (200, json.dumps(JEU).encode(), None), ["--card", self.card, "--only", "NES"])
        self.assertEqual((stats["skipped"], stats["written"]), (1, 0))
        self.assertEqual(fl.slurp(os.path.join(self.card, "Labels", "NES", "GAME.PNG")), b"mine")
        stats = self.run_ss("NES", r, {}, (200, json.dumps(JEU).encode(), None),
                            ["--card", self.card, "--only", "NES", "--force"])
        self.assertEqual(stats["written"], 1)

    def test_dry_run_writes_nothing(self):
        body = b"d" * 64
        self.rom("NES", "Game.nes", body)
        r = self.dat("NES", ("Game (Japan)", crc(body)))
        stats = self.run_ss("NES", r, {}, (200, b"{}", None), ["--card", self.card, "--only", "NES", "--dry-run"])
        self.assertEqual(stats["matched"], 1)
        self.assertFalse(os.path.exists(os.path.join(self.card, "Labels")))

    def test_two_extensions_for_one_stem_write_nothing(self):
        self.rom("SNES", "Dup.sfc", b"1" * 1024)
        self.rom("SNES", "Dup.smc", b"1" * 1024)
        r = self.dat("SNES", ("Dup (USA)", crc(b"1" * 1024)))
        stats = self.run_ss("SNES", r, {}, (200, b"{}", None), ["--card", self.card, "--only", "SNES"])
        self.assertEqual((stats["collisions"], stats["written"]), (1, 0))

    def test_cart_shell_lines_parse_under_slots_grammar_and_never_replace_a_line(self):
        a, b = b"a" * 64, b"b" * 64
        self.rom("NES", "Jp Game.nes", a)
        self.rom("NES", "Us Game.nes", b)
        os.makedirs(os.path.join(self.card, "Labels"))
        fl.spit(os.path.join(self.card, "Labels", "cart_shell.txt"), "# mine\nJp Game = nes 112233 glitter\n", "w")
        r = self.dat("NES", ("Jp Game (Japan)", crc(a)), ("Us Game (USA)", crc(b)))
        self.run_ss("NES", r, {}, (200, json.dumps(JEU).encode(), None), ["--card", self.card, "--only", "NES"])
        text = fl.slurp(os.path.join(self.card, "Labels", "cart_shell.txt"), "r")
        self.assertEqual(text, "# mine\nJp Game = nes 112233 glitter\n")
        self.run_ss("NES", r, {}, (200, json.dumps(JEU).encode(), None),
                    ["--card", self.card, "--only", "NES", "--force"])
        text = fl.slurp(os.path.join(self.card, "Labels", "cart_shell.txt"), "r")
        lines = [l for l in text.splitlines() if fl.shell_entry(l)]
        self.assertEqual(lines, ["Jp Game = famicom 7a7a7a solid"])
        for l in lines:
            self.assertTrue(slot_parses(l.split("=", 1)[1]))

    def test_region_rules(self):
        self.assertEqual(fl.shell_word("NES", "Game", "Game (Japan)"), "famicom")
        self.assertIsNone(fl.shell_word("NES", "Game (Japan)", "Game (Japan)"), "slot reads that tag itself")
        self.assertIsNone(fl.shell_word("NES", "Game", "Game (USA)"))
        self.assertIsNone(fl.shell_word("NES", "Game", "Game (Japan, USA)"))
        self.assertIsNone(fl.shell_word("NES", "Game (J)", "Game (Japan)"), "slot reads a GoodTools (J) too")
        self.assertIsNone(fl.shell_word("NES", "Game (J) [!]", "Game (Japan)"))
        self.assertEqual(fl.shell_word("NES", "Game (JU)", "Game (Japan)"), "famicom", "(JU) is a western release to slot")
        self.assertEqual(fl.shell_word("NES", "Game (Unl)", "Game (Japan)"), "famicom")
        self.assertEqual(fl.shell_word("SNES", "G", "G (Europe)"), "sfc")
        self.assertIsNone(fl.shell_word("SNES", "G", "G (USA)"))
        self.assertIsNone(fl.shell_word("GBA", "G", "G (Japan)"), "no shell lines for GB, GBC or GBA")


def md_raw(size=0x8000):
    raw = bytearray((i * 7 + 3) & 0xff for i in range(size))
    raw[0x100:0x110] = b"SEGA MEGA DRIVE "
    return bytes(raw)


def smd_of(raw):
    """The inverse of Genesis Plus GX's deinterleave_block: odd bytes first, then even, per 16 KB."""
    out = bytearray()
    for at in range(0, len(raw), 0x4000):
        block = raw[at:at + 0x4000]
        out += block[1::2] + block[0::2]
    return bytes(512) + bytes(out)


class Sega(Base):
    ss_http = NesSnes.ss_http
    run_ss = NesSnes.run_ss

    def test_the_sega_systems_name_their_library_folders_dats_and_screenscraper_ids(self):
        self.assertEqual(fl.SYSTEMS["GG"][:2], ("gamegear", {".gg"}))
        self.assertEqual(fl.SYSTEMS["SMS"][:2], ("mastersystem", {".sms"}))
        self.assertEqual(fl.SYSTEMS["MD"][:2], ("megadrive", {".md", ".gen", ".bin"}))
        self.assertEqual([fl.SYSTEMS[s][2] for s in ("GG", "SMS", "MD")],
                         [["Sega - Game Gear"], ["Sega - Master System - Mark III"], ["Sega - Mega Drive - Genesis"]])
        self.assertEqual([fl.SYSTEMS[s][3] for s in ("GG", "SMS", "MD")], [21, 2, 1])
        self.assertNotIn("MD", fl.ART_SYSTEMS)

    def test_an_interleaved_smd_dump_matches_the_raw_rom_crc_in_the_dat(self):
        raw = md_raw()
        smd = smd_of(raw)
        self.assertEqual(fl.deinterleave(smd[512:]), raw)
        self.rom("MD", "Sonic.bin", smd)
        r = self.dat("MD", ("Sonic the Hedgehog (USA, Europe)", crc(raw)))
        stats = self.run_ss("MD", r, {}, (200, json.dumps(JEU).encode(), None), ["--card", self.card, "--only", "MD"])
        self.assertEqual((stats["matched"], stats["written"], stats["unknown"]), (1, 1, 0))
        self.assertEqual(self.label("MD", "Sonic"), PNG)

    def test_a_raw_mega_drive_rom_of_an_odd_512_multiple_is_hashed_whole(self):
        raw = md_raw(0x200 * 3)
        self.rom("MD", "Tiny.md", raw)
        r = self.dat("MD", ("Tiny (Japan)", crc(raw)))
        stats = self.run_ss("MD", r, {}, (200, json.dumps(JEU).encode(), None), ["--card", self.card, "--only", "MD"])
        self.assertEqual(stats["written"], 1)
        text = fl.slurp(os.path.join(self.card, "Labels", "cart_shell.txt"), "r")
        self.assertEqual(text, "Tiny = megadrive 26242a solid\n")
        self.assertTrue(slot_parses(text.split("=", 1)[1]))

    def test_game_gear_and_master_system_carts_match_their_own_dats_and_write_no_shell_line(self):
        gg, sms = b"g" * 0x8000, b"m" * 0x8000
        self.rom("GG", "Shinobi.gg", gg)
        self.rom("SMS", "Alex Kidd.sms", sms)
        self.rom("SMS", "Not Mine.gg", gg)
        r = self.dat("GG", ("Shinobi (USA, Europe)", crc(gg)))
        r.update(self.dat("SMS", ("Alex Kidd in Miracle World (Japan)", crc(sms))))
        stats = self.run_ss("GG", r, {}, (200, json.dumps(SMS_JEU).encode(), None), ["--card", self.card])
        self.assertEqual((stats["matched"], stats["written"]), (2, 2))
        self.assertEqual(self.label("GG", "Shinobi"), PNG)
        self.assertEqual(self.label("SMS", "Alex Kidd"), PNG)
        self.assertFalse(os.path.exists(os.path.join(self.card, "Labels", "cart_shell.txt")))

    def test_master_system_takes_the_front_box_never_a_side_scan_or_screenshot(self):
        ss = fl.ScreenScraper(fl.Ctx(env={}))
        medias = SMS_JEU["response"]["jeu"]["medias"]
        self.assertEqual(ss.pick(medias, "Alex Kidd (USA)", "box-2D")["url"], "https://x.test/box-us.png")
        self.assertEqual(ss.pick(medias, "Alex Kidd (Europe)", "box-2D")["url"], "https://x.test/box-eu.png")
        self.assertEqual(ss.pick(medias, "Alex Kidd (Japan)", "box-2D")["url"], "https://x.test/box-jp.png")
        self.assertEqual(ss.pick(medias, "Alex Kidd (Brazil)", "box-2D")["url"], "https://x.test/box-us.png")
        self.assertEqual(ss.pick(medias, "Alex Kidd (USA)")["url"], "https://x.test/scan.png")
        jpg_first = [{"type": "box-2D", "region": "us", "format": "jpg", "url": "https://x.test/box.jpg"},
                     {"type": "box-2D", "region": "us", "format": "png", "url": "https://x.test/box.png"}]
        self.assertEqual(ss.pick(jpg_first, "A (USA)", "box-2D")["url"], "https://x.test/box.png")
        self.assertIsNone(ss.pick([m for m in medias if m["type"] != "box-2D"], "A (USA)", "box-2D"))
        self.assertEqual(fl.MEDIA, {"SMS": "box-2D"})

    def test_a_master_system_box_is_fetched_and_cached_apart_from_old_label_scans(self):
        sms = b"m" * 0x8000
        self.rom("SMS", "Alex Kidd.sms", sms)
        r = self.dat("SMS", ("Alex Kidd in Miracle World (USA, Europe)", crc(sms)))
        old = os.path.join(self.tmp, "cache", "ss", "SMS", crc(sms) + ".png")
        os.makedirs(os.path.dirname(old))
        fl.spit(old, fl.PNG + b"old cart scan")
        args = ["--card", self.card, "--only", "SMS"]
        stats = self.run_ss("SMS", r, {}, (200, json.dumps(SMS_JEU).encode(), None), args)
        self.assertEqual(stats["written"], 1)
        self.assertEqual(self.label("SMS", "Alex Kidd"), PNG)
        self.assertIn("https://x.test/box-us.png", self.http.calls)
        self.assertEqual(fl.slurp(os.path.join(self.tmp, "cache", "ss", "SMS", "box-2D", crc(sms) + ".png")), PNG)
        self.assertEqual(fl.slurp(old), fl.PNG + b"old cart scan")

    def test_an_existing_master_system_label_is_replaced_only_with_force(self):
        sms = b"m" * 0x8000
        self.rom("SMS", "Alex Kidd.sms", sms)
        r = self.dat("SMS", ("Alex Kidd in Miracle World (USA, Europe)", crc(sms)))
        scan = fl.PNG + b"cart scan from before"
        os.makedirs(os.path.join(self.card, "Labels", "SMS"))
        fl.spit(os.path.join(self.card, "Labels", "SMS", "Alex Kidd.png"), scan)
        args = ["--card", self.card, "--only", "SMS"]
        jeu = (200, json.dumps(SMS_JEU).encode(), None)
        stats = self.run_ss("SMS", r, {}, jeu, args)
        self.assertEqual((stats["skipped"], stats["written"]), (1, 0))
        self.assertEqual(self.label("SMS", "Alex Kidd"), scan)
        self.assertIn("--force --only SMS", self.out)
        stats = self.run_ss("SMS", r, {}, jeu, args + ["--force"])
        self.assertEqual(stats["written"], 1)
        self.assertEqual(self.label("SMS", "Alex Kidd"), PNG)

    def test_mega_drive_region_rules(self):
        self.assertEqual(fl.shell_word("MD", "G", "G (Japan)"), "megadrive")
        self.assertEqual(fl.shell_word("MD", "G", "G (Japan, Korea)"), "megadrive")
        self.assertIsNone(fl.shell_word("MD", "G", "G (Japan, USA)"))
        self.assertIsNone(fl.shell_word("MD", "G", "G (Europe)"))
        self.assertIsNone(fl.shell_word("MD", "G", "G (Brazil)"))
        self.assertIsNone(fl.shell_word("GG", "G", "G (Japan)"))
        self.assertIsNone(fl.shell_word("SMS", "G", "G (Japan)"))

    def test_a_zipped_mega_drive_library_rom_is_found_by_the_name_inside_the_zip(self):
        lib = os.path.join(self.tmp, "lib")
        os.makedirs(os.path.join(lib, "megadrive"))
        raw = md_raw()
        with zipfile.ZipFile(os.path.join(lib, "megadrive", "Sonic (USA, Europe).zip"), "w") as z:
            z.writestr("Sonic the Hedgehog (USA, Europe).md", raw)
        found, bad = fl.scan_library(lib, "MD")
        self.assertEqual(bad, [])
        rom = found[fl.nfc("Sonic the Hedgehog (USA, Europe)")]
        self.assertEqual(f"{rom.whole() & 0xffffffff:08X}", crc(raw))


class Atari(NesSnes):
    def test_the_atari_shelves_name_their_folders_extensions_dats_and_screenscraper_ids(self):
        self.assertEqual(fl.SYSTEMS["A2600"], ("atari2600", {".a26", ".bin"}, ["Atari - 2600"], 26))
        self.assertEqual(fl.SYSTEMS["A7800"], ("atari7800", {".a78"}, ["Atari - 7800"], 41))

    def test_a_headered_7800_dump_is_also_hashed_without_its_header(self):
        body = bytes(range(256)) * 64
        head = b"\x01ATARI7800" + bytes(118)
        rom = fl.Rom("Asteroids (USA)", len(head + body), lambda: head + body)
        self.assertEqual(list(rom.crcs("A7800")), [zlib.crc32(body), zlib.crc32(head + body)])
        bare = fl.Rom("Asteroids (USA)", len(body), lambda: body)
        self.assertEqual(list(bare.crcs("A7800")), [zlib.crc32(body)])

    def test_a_2600_cart_matched_by_crc_is_asked_under_26_and_lands_in_labels_a2600(self):
        rom = bytes(range(256)) * 16
        self.rom("A2600", "Pitfall! (USA).a26", rom)
        r = self.dat("A2600", ("Pitfall! - Pitfall Harry's Jungle Adventure (USA)", crc(rom)))
        stats = self.run_ss("A2600", r, {}, (200, json.dumps(JEU).encode(), None), ["--card", self.card, "--only", "A2600"])
        self.assertEqual((stats["matched"], stats["written"], stats["unknown"]), (1, 1, 0))
        self.assertEqual(self.label("A2600", "Pitfall! (USA)"), PNG)


class Sega32X(NesSnes):
    def systemeids(self):
        return [urllib.parse.parse_qs(urllib.parse.urlparse(u).query)["systemeid"][0]
                for u in self.http.calls if u.startswith(fl.SS_API + "jeuInfos.php")]

    def test_the_32x_shelf_names_its_folder_extensions_dat_and_screenscraper_id(self):
        self.assertEqual(fl.SYSTEMS["32X"][:2], ("sega32x", {".32x", ".bin"}))
        self.assertEqual(fl.SYSTEMS["32X"][2], ["Sega - 32X"])
        self.assertEqual(fl.SYSTEMS["32X"][3], 19)
        self.assertNotIn("32X", fl.ART_SYSTEMS)

    def test_a_32x_bin_matched_by_crc_is_asked_under_19_and_lands_in_labels_32x(self):
        rom = bytes(range(256)) * 16
        self.rom("32X", "Knuckles Chaotix 32X (JU) [!].bin", rom)
        r = self.dat("32X", ("Knuckles' Chaotix (Japan, USA)", crc(rom)))
        stats = self.run_ss("32X", r, {}, (200, json.dumps(JEU).encode(), None), ["--card", self.card, "--only", "32X"])
        self.assertEqual((stats["matched"], stats["written"], stats["unknown"]), (1, 1, 0))
        self.assertEqual(self.label("32X", "Knuckles Chaotix 32X (JU) [!]"), PNG)
        self.assertEqual(self.systemeids(), ["19"])

    def test_a_32x_name_search_drops_the_32x_word_and_asks_only_under_19(self):
        out = fl.attempts("Knuckles Chaotix 32X (JU) [!]", "32X")
        self.assertEqual([(a[0], a[1]) for a in out], [(19, "Knuckles Chaotix")])
        md = fl.attempts("Doom 32X (JU) [!]", "MD")
        self.assertEqual([a[0] for a in md], [19, 1])


class VirtualBoy(Base):
    ss_http = NesSnes.ss_http
    run_ss = NesSnes.run_ss

    def test_the_virtual_boy_names_its_library_folder_dat_and_screenscraper_id(self):
        self.assertEqual(fl.SYSTEMS["VB"], ("virtualboy", {".vb", ".vboy"}, ["Nintendo - Virtual Boy"], 11))
        self.assertNotIn("VB", fl.ART_SYSTEMS)

    def test_a_vb_cart_matched_by_crc_is_asked_under_11_and_lands_in_labels_vb(self):
        raw = b"v" * 0x10000
        self.rom("VB", "Virtual Boy Wario Land (Japan, USA).vb", raw)
        r = self.dat("VB", ("Virtual Boy Wario Land (Japan, USA)", crc(raw)))
        stats = self.run_ss("VB", r, {}, (200, json.dumps(JEU).encode(), None), ["--card", self.card, "--only", "VB"])
        self.assertEqual((stats["matched"], stats["written"], stats["unknown"]), (1, 1, 0))
        self.assertEqual(self.label("VB", "Virtual Boy Wario Land (Japan, USA)"), PNG)
        self.assertFalse(os.path.exists(os.path.join(self.card, "Labels", "cart_shell.txt")))
        self.assertTrue(any("systemeid=11" in c for c in self.http.calls))


def p8_text(label_digit="8"):
    label = "\n".join([label_digit * 128] * 128)
    return f"pico-8 cartridge // http://www.pico-8.com\nversion 41\n__lua__\n-- band\n__label__\n{label}\n".encode()


def p8_png():
    """A 160x205 PNG cart picture: grey, with a red 128x128 label at (16, 24)."""
    rows = []
    for y in range(205):
        row = b""
        for x in range(160):
            row += bytes([255, 0, 77, 255]) if 16 <= x < 144 and 24 <= y < 152 else bytes([100, 100, 100, 255])
        rows.append(row)
    return fl.png_bytes(160, 205, rows)


class Pico8(Base):
    def test_pico_8_has_no_dat_and_no_screenscraper_id(self):
        self.assertEqual(fl.SYSTEMS["PICO8"], ("pico8", {".p8", ".png"}, [], None))

    def test_a_text_cart_label_section_becomes_a_128_square_png_in_the_palette_without_the_network(self):
        self.rom("PICO8", "Band.p8", p8_text("8"))
        self.rom("PICO8", "Night.p8", p8_text("o"))
        stats = self.run_tool({}, ["--card", self.card, "--only", "PICO8"])
        self.assertEqual((stats["matched"], stats["written"], stats["errors"]), (2, 2, 0))
        self.assertEqual(self.http.calls, [])
        w, h, rows = fl.png_rows(self.label("PICO8", "Band"))
        self.assertEqual((w, h), (128, 128))
        self.assertEqual(rows[64][:4], bytes([0xff, 0x00, 0x4d, 0xff]))
        self.assertEqual(fl.png_rows(self.label("PICO8", "Night"))[2][0][:3], bytes.fromhex("be1250"))

    def test_a_png_cart_gives_its_own_picture_at_16_24_and_a_bare_png_is_not_a_cart(self):
        self.rom("PICO8", "Celeste.p8.png", p8_png())
        self.rom("PICO8", "Packed.p8", p8_png())
        self.rom("PICO8", "cover.png", p8_png())
        stats = self.run_tool({}, ["--card", self.card, "--only", "PICO8"])
        self.assertEqual((stats["matched"], stats["written"]), (2, 2))
        for stem in ("Celeste.p8", "Packed"):
            w, h, rows = fl.png_rows(self.label("PICO8", stem))
            self.assertEqual((w, h), (128, 128))
            self.assertEqual({rows[y][x * 4:x * 4 + 4] for y in (0, 127) for x in (0, 127)}, {bytes([255, 0, 77, 255])})
        self.assertIsNone(self.label("PICO8", "cover"))

    def test_a_cart_without_a_label_is_missing_and_an_existing_label_is_kept(self):
        self.rom("PICO8", "Bare.p8", b"pico-8 cartridge\n__lua__\nx=1\n")
        self.rom("PICO8", "Band.p8", p8_text())
        os.makedirs(os.path.join(self.card, "Labels", "PICO8"))
        fl.spit(os.path.join(self.card, "Labels", "PICO8", "Band.png"), PNG)
        stats = self.run_tool({}, ["--card", self.card, "--only", "PICO8"])
        self.assertEqual((stats["missing"], stats["skipped"], stats["written"]), (1, 1, 0))
        self.assertEqual(self.label("PICO8", "Band"), PNG)


class Lynx(Base):
    ss_http = NesSnes.ss_http
    run_ss = NesSnes.run_ss

    def test_lynx_names_its_library_folder_dat_and_screenscraper_id(self):
        self.assertEqual(fl.SYSTEMS["Lynx"], ("atarilynx", {".lnx", ".lyx"}, ["Atari - Lynx"], 28))
        self.assertNotIn("Lynx", fl.ART_SYSTEMS)

    def test_a_lnx_cart_is_hashed_without_its_header(self):
        body = b"lynx-body" * 1000
        self.rom("Lynx", "Klax.lnx", b"LYNX" + bytes(60) + body)
        r = self.dat("Lynx", ("Klax (USA, Europe)", crc(body)))
        stats = self.run_ss("Lynx", r, {}, (200, json.dumps(JEU).encode(), None), ["--card", self.card, "--only", "Lynx"])
        self.assertEqual((stats["matched"], stats["written"], stats["unknown"]), (1, 1, 0))
        self.assertEqual(self.label("Lynx", "Klax"), PNG)
        self.assertFalse(os.path.exists(os.path.join(self.card, "Labels", "cart_shell.txt")))
        self.assertTrue(any("systemeid=28" in c for c in self.http.calls))

    def test_a_headerless_lyx_is_hashed_whole(self):
        raw = b"l" * 0x20000
        self.rom("Lynx", "Lexis.lyx", raw)
        r = self.dat("Lynx", ("Lexis (USA)", crc(raw)))
        stats = self.run_ss("Lynx", r, {}, (200, json.dumps(JEU).encode(), None), ["--card", self.card, "--only", "Lynx"])
        self.assertEqual(stats["written"], 1)


def ngp_rom(colour):
    rom = bytearray(0x1000)
    rom[:28] = b"COPYRIGHT BY SNK CORPORATION"
    rom[0x23] = 0x10 if colour else 0x00
    rom[0x24:0x30] = b"POCKET GAME "
    return bytes(rom)


class NeoGeoPocket(NesSnes):
    def ngp_dats(self, mono, color):
        return {fl.DAT + urllib.parse.quote(n) + ".dat": (200, dat_text(g).encode(), None)
                for n, g in zip(fl.SYSTEMS["NGP"][2], (mono, color))}

    def systemeids(self):
        return [urllib.parse.parse_qs(urllib.parse.urlparse(u).query)["systemeid"][0]
                for u in self.http.calls if u.startswith(fl.SS_API + "jeuInfos.php")]

    def test_the_ngp_shelf_names_its_folder_extensions_both_dats_and_the_mono_id(self):
        self.assertEqual(fl.SYSTEMS["NGP"][:2], ("ngp", {".ngp", ".ngc", ".ngpc"}))
        self.assertEqual(fl.SYSTEMS["NGP"][2], ["SNK - Neo Geo Pocket", "SNK - Neo Geo Pocket Color"])
        self.assertEqual((fl.SYSTEMS["NGP"][3], fl.NGP_COLOR_ID), (25, 82))

    def test_a_color_header_asks_screenscraper_for_82_and_a_mono_one_for_25(self):
        color, mono = ngp_rom(True), ngp_rom(False)
        self.rom("NGP", "Sonic.ngp", color)
        self.rom("NGP", "Baseball.ngc", mono)
        r = self.ngp_dats(("Baseball Stars (Japan, Europe)", crc(mono)),
                          ("Sonic the Hedgehog - Pocket Adventure (World)", crc(color)))
        stats = self.run_ss("NGP", r, {}, (200, json.dumps(JEU).encode(), None), ["--card", self.card, "--only", "NGP"])
        self.assertEqual((stats["matched"], stats["written"], stats["unknown"]), (2, 2, 0))
        self.assertEqual(self.label("NGP", "Sonic"), PNG)
        self.assertEqual(self.label("NGP", "Baseball"), PNG)
        self.assertEqual(sorted(self.systemeids()), ["25", "82"])

    def test_a_short_or_unsigned_ngp_file_asks_under_the_mono_id(self):
        rom = fl.Rom("Tiny", 4, lambda: b"\x00\x01\x02\x03")
        self.assertEqual(fl.ss_id("NGP", rom), 25)
        self.assertEqual(fl.ss_id("GG", rom), 21)


class ArtHost(Base):
    def routes(self, **extra):
        index = {"AAAAAAAA": {"support-texture": "GBA/support-texture/AAAAAAAA.png"}}
        r = {fl.ART + "index.json": (200, json.dumps(index).encode(), None),
             fl.ART + "GBA/support-texture/AAAAAAAA.png": (200, PNG, None)}
        r.update(self.dat("GBA", ("Metroid (USA)", "AAAAAAAA")))
        r.update(extra)
        return r

    def gba(self, data):
        # a ROM whose CRC is not AAAAAAAA, so the name rule is what resolves it
        self.rom("GBA", "Metroid (USA).gba", data)

    def test_art_set_label_is_written_unchanged_with_the_user_agent(self):
        self.gba(b"m" * 64)
        stats = self.run_tool(self.routes(), ["--card", self.card, "--only", "GBA"])
        self.assertEqual((stats["written"], stats["unknown"]), (1, 0))
        self.assertEqual(self.label("GBA", "Metroid (USA)"), PNG)
        self.assertEqual(fl.slurp(os.path.join(self.tmp, "cache", "art", "GBA", "support-texture", "AAAAAAAA.png")), PNG)
        self.assertIn("slot-nes-snes", fl.UA)
        self.run_tool(self.routes(), ["--card", self.card, "--only", "GBA", "--force"])
        self.assertEqual([c for c in self.http.calls if c.endswith(".png")], [], "a rerun is served from the cache")

    def test_art_404_is_missing(self):
        self.gba(b"m" * 64)
        stats = self.run_tool(self.routes(**{fl.ART + "GBA/support-texture/AAAAAAAA.png": (404, b"", None)}),
                              ["--card", self.card, "--only", "GBA"])
        self.assertEqual((stats["missing"], stats["errors"], stats["written"]), (1, 0, 0))

    def test_art_rate_limit_retries_then_succeeds_and_otherwise_stops(self):
        self.gba(b"m" * 64)
        slow = {fl.ART + "GBA/support-texture/AAAAAAAA.png": [(429, b"", "1"), (200, PNG, None)]}
        stats = self.run_tool(self.routes(**slow), ["--card", self.card, "--only", "GBA"])
        self.assertEqual(stats["written"], 1)
        shutil.rmtree(os.path.join(self.card, "Labels"))
        shutil.rmtree(os.path.join(self.tmp, "cache", "art", "GBA"))
        stats = self.run_tool(self.routes(**{fl.ART + "GBA/support-texture/AAAAAAAA.png": (429, b"", None)}),
                              ["--card", self.card, "--only", "GBA"])
        self.assertEqual((stats["written"], stats["missing"]), (0, 1))
        self.assertIn("art host rate limit", self.out)

    def test_refusing_host_is_reported_and_creds_fall_back(self):
        self.gba(b"m" * 64)
        r = self.routes(**{fl.ART + "index.json": (403, b"", None)})
        stats = self.run_tool(r, ["--card", self.card, "--only", "GBA"])
        self.assertIn("refuses non-browser clients (HTTP 403)", self.out)
        self.assertEqual(stats["written"], 0)

    def test_index_paths_are_validated(self):
        index = {"AAAAAAAA": {"support-texture": "../../etc/passwd"}}
        self.gba(b"m" * 64)
        stats = self.run_tool(self.routes(**{fl.ART + "index.json": (200, json.dumps(index).encode(), None)}),
                              ["--card", self.card, "--only", "GBA"])
        self.assertEqual(stats["written"], 0)


class Device(Base):
    def setUp(self):
        super().setUp()
        self.lib = os.path.join(self.tmp, "lib")
        os.makedirs(os.path.join(self.lib, "gba"))
        self.crc_a = None

    def test_device_mode_pushes_only_new_labels_using_the_glob_and_zip_names(self):
        data_a, data_b = b"a" * 64, b"b" * 64
        with zipfile.ZipFile(os.path.join(self.lib, "gba", "Alpha (USA).zip"), "w") as z:
            z.writestr("Alpha.gba", data_a)         # the stem is the one inside the zip
        fl.spit(os.path.join(self.lib, "gba", "Beta.gba"), data_b)
        sd = "/mnt/sdcard"
        adb = FakeAdb({f"{sd}/Games/GBA/Alpha.gba": b"", f"{sd}/Games/GBA/Beta.gba": b"",
                       f"{sd}/Games/GBA/._junk.gba": b"", f"{sd}/Labels/GBA/beta.png": b"theirs"})
        routes = {fl.ART + "index.json": (200, json.dumps({
            crc(data_a): {"support-texture": f"GBA/support-texture/{crc(data_a)}.png"},
            crc(data_b): {"support-texture": f"GBA/support-texture/{crc(data_b)}.png"}}).encode(), None),
            fl.ART + f"GBA/support-texture/{crc(data_a)}.png": (200, PNG, None),
            fl.ART + f"GBA/support-texture/{crc(data_b)}.png": (200, PNG, None)}
        routes.update(self.dat("GBA", ("Alpha (USA)", crc(data_a)), ("Beta (USA)", crc(data_b))))
        stats = self.run_tool(routes, ["--device", "--library", self.lib, "--only", "GBA"], adb=adb)
        self.assertEqual((stats["written"], stats["skipped"]), (1, 1))
        self.assertEqual(adb.pushed, [f"{sd}/Labels/GBA/Alpha.png"])
        self.assertEqual(adb.files[f"{sd}/Labels/GBA/beta.png"], b"theirs")
        self.assertFalse(any(c[0] == "shell" and c[1].startswith("ls") for c in adb.cmds))

    def test_device_cart_shell_is_pulled_merged_and_pushed_back(self):
        body = b"j" * 1024
        os.makedirs(os.path.join(self.lib, "snes"))
        fl.spit(os.path.join(self.lib, "snes", "Jp.sfc"), body)
        sd = "/mnt/sdcard"
        adb = FakeAdb({f"{sd}/Games/SNES/Jp.sfc": b"", f"{sd}/Labels/cart_shell.txt": b"Old = nes 010203 clear\n"})
        r = self.dat("SNES", ("Jp (Japan)", crc(body)))
        h = FakeHttp(r)
        h.get = lambda url, g=h.get: (200, json.dumps(JEU).encode(), None) if "jeuInfos" in url else \
            (200, b"{}", None) if "ssuserInfos" in url else (200, PNG, None) if url.startswith("https://x.test") else g(url)
        ctx = fl.Ctx(http=h, adb=adb, env=dict(SS_ENV, SLOT_LABELS_CACHE=os.path.join(self.tmp, "cache")),
                     sleep=lambda s: None)
        with contextlib.redirect_stdout(io.StringIO()):
            stats = fl.main(["--device", "--library", self.lib, "--only", "SNES"], ctx)
        self.assertEqual(stats["written"], 1)
        self.assertEqual(adb.files[f"{sd}/Labels/cart_shell.txt"],
                         b"Old = nes 010203 clear\nJp = sfc 949696 solid\n")
        self.assertIn(f"{sd}/Labels/SNES/Jp.png", adb.pushed)

    def test_dry_run_on_the_device_pushes_nothing(self):
        data = b"a" * 64
        fl.spit(os.path.join(self.lib, "gba", "Alpha.gba"), data)
        adb = FakeAdb({"/mnt/sdcard/Games/GBA/Alpha.gba": b""})
        routes = {fl.ART + "index.json": (200, json.dumps(
            {crc(data): {"support-texture": f"GBA/support-texture/{crc(data)}.png"}}).encode(), None)}
        routes.update(self.dat("GBA", ("Alpha (USA)", crc(data))))
        stats = self.run_tool(routes, ["--device", "--library", self.lib, "--only", "GBA", "--dry-run"], adb=adb)
        self.assertEqual((stats["matched"], stats["written"]), (1, 1))
        self.assertEqual(adb.pushed, [])


if __name__ == "__main__":
    unittest.main()
