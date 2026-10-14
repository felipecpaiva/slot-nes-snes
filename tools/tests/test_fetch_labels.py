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
    return (len(w) == 3 and w[0] in {"auto", "notched", "rounded", "nes", "famicom", "snes", "sfc"}
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
        self.assertEqual(fl.shell_word("SNES", "G", "G (Europe)"), "sfc")
        self.assertIsNone(fl.shell_word("SNES", "G", "G (USA)"))
        self.assertIsNone(fl.shell_word("GBA", "G", "G (Japan)"), "no shell lines for GB, GBC or GBA")


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
