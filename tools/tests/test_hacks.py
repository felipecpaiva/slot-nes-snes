"""tools/hacks.py, offline: BPS/UPS/IPS built here, the registry merge, --check against a fake GitHub, the
update plan on a temp card and library (same name kept, saves copied, states moved, seated cart refused) and
the rollback round trip.

    python3 -m unittest tools/tests/test_hacks.py
"""
import contextlib
import errno
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
import unicodedata
import unittest
from unittest import mock
import zipfile
import zlib

from tools.tests.test_fetch_labels import FakeHttp

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("hacks", os.path.join(HERE, "..", "hacks.py"))
hk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hk)


def rd(path):
    with open(path, "rb") as f:
        return f.read()


def enc(n):
    out = bytearray()
    while True:
        x, n = n & 0x7f, n >> 7
        if not n:
            out.append(0x80 | x)
            return bytes(out)
        out.append(x)
        n -= 1


def u32(n):
    return (n & 0xffffffff).to_bytes(4, "little")


def seal(body, src, tgt):
    body += u32(zlib.crc32(src)) + u32(zlib.crc32(tgt))
    return body + u32(zlib.crc32(body))


def bps(src, tgt, actions):
    """actions: (0, n) SourceRead, (1, bytes) TargetRead, (2|3, n, relative offset) Source/TargetCopy."""
    body = b"BPS1" + enc(len(src)) + enc(len(tgt)) + enc(0)
    for a in actions:
        n = a[1] if isinstance(a[1], int) else len(a[1])
        body += enc((n - 1) << 2 | a[0])
        if a[0] == 1:
            body += a[1]
        elif a[0] > 1:
            body += enc(abs(a[2]) << 1 | (a[2] < 0))
    return seal(body, src, tgt)


def ups(src, tgt):
    body, prev, i = b"UPS1" + enc(len(src)) + enc(len(tgt)), 0, 0
    a, b = src.ljust(len(tgt), b"\0"), tgt.ljust(len(src), b"\0")
    while i < len(b):
        if a[i] == b[i]:
            i += 1
            continue
        body += enc(i - prev)
        while i < len(b) and a[i] != b[i]:
            body += bytes([a[i] ^ b[i]])
            i += 1
        body += b"\0"
        i += 1
        prev = i
    return seal(body, src, tgt)


def ips(records, truncate=None):
    out = b"PATCH"
    for off, data in records:
        if isinstance(data, tuple):  # RLE
            out += off.to_bytes(3, "big") + b"\0\0" + data[0].to_bytes(2, "big") + data[1]
        else:
            out += off.to_bytes(3, "big") + len(data).to_bytes(2, "big") + data
    return out + b"EOF" + (truncate.to_bytes(3, "big") if truncate is not None else b"")


BASE = bytes(range(256)) * 64
NEW = BASE[:100] + b"HACKED v2" + BASE[109:] + b"tail"


class Patches(unittest.TestCase):
    def test_bps_every_action_and_an_overlapping_target_copy(self):
        tgt = BASE[:10] + b"ab" + b"abababab" + BASE[20:30]
        p = bps(BASE, tgt, [(0, 10), (1, b"ab"), (3, 8, 10), (2, 10, 20)])
        self.assertEqual(hk.apply_patch(BASE, p), tgt)

    def test_bps_refuses_another_base(self):
        p = bps(BASE, NEW, [(1, NEW)])
        with self.assertRaisesRegex(hk.PatchError, "source CRC mismatch"):
            hk.apply_patch(BASE[:-1] + b"x", p)

    def test_bps_refuses_a_corrupt_patch(self):
        p = bytearray(bps(BASE, NEW, [(1, NEW)]))
        p[20] ^= 1
        with self.assertRaisesRegex(hk.PatchError, "corrupt"):
            hk.apply_patch(BASE, bytes(p))

    def test_ups_round_trip_and_refusals(self):
        p = ups(BASE, NEW)
        self.assertEqual(hk.apply_patch(BASE, p), NEW)
        with self.assertRaisesRegex(hk.PatchError, "source CRC mismatch"):
            hk.apply_patch(NEW[:len(BASE)], p)
        with self.assertRaisesRegex(hk.PatchError, "target CRC"):
            # a well sealed patch whose target CRC does not match what it produces
            body = p[:-12]
            hk.apply_patch(BASE, seal(body, BASE, b"other"))

    def test_ips_records_rle_growth_and_truncate(self):
        p = ips([(100, b"HACKED v2"), (len(BASE), (4, b"z"))])
        self.assertEqual(hk.apply_patch(BASE, p, warn=lambda *_: None), BASE[:100] + b"HACKED v2" + BASE[109:] + b"zzzz")
        self.assertEqual(hk.apply_patch(BASE, ips([], truncate=16), warn=lambda *_: None), BASE[:16])

    def test_ips_checks_the_registry_target_crc_and_warns_without_one(self):
        p = ips([(100, b"HACKED v2")])
        good = BASE[:100] + b"HACKED v2" + BASE[109:]
        self.assertEqual(hk.apply_patch(BASE, p, hk.crc_hex(good)), good)
        with self.assertRaisesRegex(hk.PatchError, "registry wants"):
            hk.apply_patch(BASE, p, "DEADBEEF")
        said = []
        hk.apply_patch(BASE, p, None, warn=said.append)
        self.assertIn("unverified", said[0])

    def test_xdelta_is_refused_with_advice(self):
        with self.assertRaisesRegex(hk.PatchError, "xdelta"):
            hk.apply_patch(BASE, b"\xd6\xc3\xc4\x00rest")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.card, self.lib = os.path.join(self.tmp, "card"), os.path.join(self.tmp, "lib")
        self.env = {"SLOT_HACKS_CACHE": os.path.join(self.tmp, "cache"),
                    "SLOT_HACKS_CONFIG": os.path.join(self.tmp, "config"),
                    "SLOT_HACKS_HOME": os.path.join(self.tmp, "home")}
        self.seed = os.path.join(self.tmp, "seed.json")
        self.write(self.seed, "// test seed\n" + json.dumps({
            "hack": {"name": "Test Hack", "system": "GBA", "card": "Hack (v1).gba", "source": "manual",
                     "format": "bps", "base_name": "Base (USA)", "base_crc32": hk.crc_hex(BASE),
                     "saves_carry_over": "yes"},
            "gh": {"name": "GitHub Hack", "system": "GBA", "card": "Gh v1.0.gba", "source": "github:o/r",
                   "asset": "*.bps", "format": "bps", "base_crc32": hk.crc_hex(BASE), "saves_carry_over": "unknown"}}))
        old_seed, hk.SEED = hk.SEED, self.seed
        self.addCleanup(setattr, hk, "SEED", old_seed)

    def write(self, path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb" if isinstance(data, bytes) else "w") as f:
            f.write(data)

    def at(self, *parts):
        return os.path.join(self.card, *parts)

    def run_main(self, *argv, http=None):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            r = hk.main(list(argv), hk.Ctx(http=http or FakeHttp({}), env=self.env, sleep=lambda s: None))
        return r, out.getvalue()


class Registry(Base):
    def test_user_file_overrides_adds_and_ignores_unknown_ids(self):
        user = os.path.join(self.tmp, "user.json")
        self.write(user, "// mine\n{\n"
                         '  "hack": {"source": "page:https://example.test/hack", "version_regex": "v([0-9.]+)"},\n'
                         '  // a comment between entries\n'
                         '  "new": {"system": "MD", "card": "New v2.bin", "source": "manual", "colour": "red"},\n'
                         '  "ghost": {"source": "github:a/b"}\n}\n')
        said = []
        reg = hk.load_registry(self.seed, user, warn=said.append)
        self.assertEqual(reg["hack"]["source"], "page:https://example.test/hack")
        self.assertEqual(reg["hack"]["base_crc32"], hk.crc_hex(BASE))  # the seed's other fields stay
        self.assertEqual(reg["new"]["card"], "New v2.bin")
        self.assertNotIn("ghost", reg)
        self.assertTrue(any("ghost" in s and "ignored" in s for s in said))
        self.assertTrue(any("colour" in s for s in said))

    def test_a_bad_entry_is_skipped_not_fatal(self):
        user = os.path.join(self.tmp, "user.json")
        self.write(user, json.dumps({"hack": {"system": "N64"}}))
        said = []
        self.assertNotIn("hack", hk.load_registry(self.seed, user, warn=said.append))
        self.assertIn("system", said[0])

    def test_the_shipped_seed_loads_cleanly(self):
        said = []
        reg = hk.load_registry(os.path.join(HERE, "..", "hacks.json"), None, warn=said.append)
        self.assertEqual(said, [])
        self.assertTrue(reg)
        for hid, h in reg.items():
            self.assertTrue(h.get("cite"), f"{hid} cites no source")

    def test_init_writes_a_commented_file_once(self):
        self.write(self.at("Games", "GBA", "Hack (v1).gba"), BASE)
        self.write(self.at("Games", "MD", "Sonic Fan Remix v3.1.bin"), b"x")
        self.write(self.at("Games", "MD", "Sonic 2 (W) [h1].bin"), b"x")
        r, out = self.run_main("--card", self.card, "--init")
        path = os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks.json")
        reg = hk.load_registry(self.seed, path, warn=self.fail)
        self.assertEqual(reg["sonic-fan-remix-v3-1"]["source"], "")
        self.assertNotIn("sonic-2-w-h1", reg)
        self.assertIn('//  "hack"', rd(path).decode())
        before = rd(path).decode()
        self.run_main("--card", self.card, "--init")
        self.assertEqual(rd(path).decode(), before)


RELEASE = "https://api.github.com/repos/o/r/releases/latest"
ASSET = "https://github.com/o/r/releases/download/v2.0/gh.bps"


def release(tag="v2.0"):
    return (200, json.dumps({"tag_name": tag, "html_url": "https://github.com/o/r/releases/tag/" + tag,
                             "assets": [{"name": "gh.bps", "browser_download_url": ASSET},
                                        {"name": "readme.txt", "browser_download_url": "x"}]}).encode(), None)


class Check(Base):
    def test_github_newer_tag_is_an_update_and_equal_is_up_to_date(self):
        self.write(self.at("Games", "GBA", "Gh v1.0.gba"), b"x")
        rows = self.run_main("--card", self.card, http=FakeHttp({RELEASE: release()}))[0]
        self.assertEqual([(r[1], r[2], r[3], r[4]) for r in rows], [("gh", "1.0", "v2.0", "UPDATE AVAILABLE")])
        hk.write_state(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks-state.json"), {"gh": {"version": "v2.0"}})
        shutil.rmtree(self.env["SLOT_HACKS_CACHE"])
        rows = self.run_main("--card", self.card, http=FakeHttp({RELEASE: release()}))[0]
        self.assertEqual(rows[0][4], "up to date")

    def test_check_writes_nothing_to_the_card(self):
        self.write(self.at("Games", "GBA", "Gh v1.0.gba"), b"x")
        before = sorted(os.walk(self.card))
        self.run_main("--card", self.card, "--check", http=FakeHttp({RELEASE: release()}))
        self.assertEqual(sorted(os.walk(self.card)), before)
        self.assertFalse(os.path.exists(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks-state.json")))

    def test_page_source_hash_baseline_then_changed(self):
        user = os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks.json")
        self.write(user, json.dumps({"hack": {"source": "page:https://x.test/p"}}))
        self.write(self.at("Games", "GBA", "Hack (v1).gba"), b"x")
        status = lambda body: [r[4] for r in self.run_main("--card", self.card, http=FakeHttp(
            {"https://x.test/p": (200, body, None)}))[0] if r[1] == "hack"][0]
        self.assertEqual(status(b"one"), "page baseline recorded")
        self.assertTrue(status(b"one").startswith("page unchanged"))
        self.assertTrue(status(b"two").startswith("page changed"))

    def test_page_version_regex_takes_the_highest_listed(self):
        user = os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks.json")
        self.write(user, json.dumps({"hack": {"source": "page:https://x.test/p", "version_regex": r"p/(\d+(?:\.\d+)+)\.zip"}}))
        self.write(self.at("Games", "GBA", "Hack (v1).gba"), b"x")
        page = b"p/2.0.zip p/10.1.zip p/4.1.zip"
        rows = self.run_main("--card", self.card, http=FakeHttp({"https://x.test/p": (200, page, None)}))[0]
        self.assertEqual(rows[0][3:5], ("10.1", "UPDATE AVAILABLE"))


class Update(Base):
    STEM = "Hack (v1)"

    def setUp(self):
        super().setUp()
        old = BASE[:100] + b"HACKED v1" + BASE[109:]
        self.write(self.at("Games", "GBA", self.STEM + ".gba"), old)
        self.write(self.at("Saves", "GBA", self.STEM + ".sav"), b"battery")
        self.write(self.at("States", "GBA", "mgba", self.STEM, "2026-10-01_10-00-00.state"), b"s1")
        self.write(self.at("States", "GBA", "mgba", self.STEM, "2026-10-01_10-00-00.png"), b"t1")
        self.write(self.at("States", "GBA", "mgba", self.STEM, "resume.state"), b"auto")
        self.write(self.at("States", "GBA", "gpsp", self.STEM, "resume.state"), b"auto2")
        self.write(self.at("States", "GBA", "mgba", "Other", "resume.state"), b"keep")
        self.write(self.at("Config", "slot.state"), "cart=Other\ncart_platform=gba\nshelf_cart=gba/Hack (v1)\n")
        self.write(os.path.join(self.lib, "gba", "Base (USA).gba"), BASE)
        with zipfile.ZipFile(os.path.join(self.lib, "gba", self.STEM + ".zip"), "w") as z:
            z.writestr(self.STEM + ".gba", old)
        self.write(os.path.join(self.lib, "gba", self.STEM + ".state.auto"), b"ra")
        self.write(os.path.join(self.lib, "gba", self.STEM + ".srm"), b"ra-save")
        self.write(os.path.join(self.env["SLOT_HACKS_HOME"], "incoming", "hack", "hack-v2.bps"),
                   bps(BASE, NEW, [(0, 100), (1, b"HACKED v2"), (2, len(BASE) - 109, 109), (1, b"tail")]))
        self.old = old

    def tree(self, root):
        return sorted(os.path.relpath(os.path.join(d, f), root) for d, _, fs in os.walk(root) for f in fs)

    def update(self, *extra):
        return self.run_main("--card", self.card, "--library", self.lib, "--update", "hack", *extra)

    def test_dry_run_writes_nothing(self):
        before = self.tree(self.tmp)
        r, out = self.update("--dry-run")
        self.assertIn("DRY RUN", out)
        self.assertEqual(self.tree(self.tmp), before)

    def test_update_keeps_the_name_copies_the_save_and_moves_every_state(self):
        r, out = self.update("--yes")
        self.assertEqual(r, 0, out)
        rom = self.at("Games", "GBA", self.STEM + ".gba")
        self.assertEqual(rd(rom), NEW)
        self.assertEqual(rd(self.at("Saves", "GBA", self.STEM + ".sav")), b"battery")
        self.assertFalse(os.path.exists(self.at("States", "GBA", "mgba", self.STEM)))
        self.assertFalse(os.path.exists(self.at("States", "GBA", "gpsp", self.STEM)))
        self.assertTrue(os.path.exists(self.at("States", "GBA", "mgba", "Other", "resume.state")))
        (label,) = os.listdir(self.at("Backups", "hacks", "GBA", self.STEM))
        self.assertTrue(label.endswith("_1"), label)
        b = self.at("Backups", "hacks", "GBA", self.STEM, label)
        self.assertEqual(self.tree(b), sorted([
            "Games/GBA/Hack (v1).gba", "Saves/GBA/Hack (v1).sav", "backup.json",
            "States/GBA/mgba/Hack (v1)/2026-10-01_10-00-00.state", "States/GBA/mgba/Hack (v1)/2026-10-01_10-00-00.png",
            "States/GBA/mgba/Hack (v1)/resume.state", "States/GBA/gpsp/Hack (v1)/resume.state"]))
        self.assertEqual(rd(os.path.join(b, "Games", "GBA", self.STEM + ".gba")), self.old)
        # the library: same zip and member name; RetroArch's state and .srm left alone
        with zipfile.ZipFile(os.path.join(self.lib, "gba", self.STEM + ".zip")) as z:
            self.assertEqual(z.read(self.STEM + ".gba"), NEW)
        self.assertEqual(rd(os.path.join(self.lib, "gba", self.STEM + ".state.auto")), b"ra")
        self.assertEqual(rd(os.path.join(self.lib, "gba", self.STEM + ".srm")), b"ra-save")
        self.assertIn("may not work with the new version", out)
        lb = os.path.join(self.env["SLOT_HACKS_HOME"], "backups", "GBA", self.STEM, label)
        self.assertEqual(sorted(os.listdir(lb)), ["Hack (v1).zip", "backup.json"])
        state = json.loads(rd(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks-state.json")))
        self.assertEqual((state["hack"]["version"], state["hack"]["crc32"]), ("2", hk.crc_hex(NEW)))
        # a second run finds nothing to do
        r, out = self.update("--yes")
        self.assertIn("already installed", out)

    def test_a_seated_cart_is_refused_before_any_write(self):
        self.write(self.at("Config", "slot.state"), "cart=Hack (v1)\ncart_platform=gba\n")
        before = self.tree(self.tmp)
        r, out = self.update("--yes")
        self.assertIn("seated", out)
        self.assertEqual(r, 1)
        self.assertEqual(self.tree(self.tmp), before)

    def test_missing_base_is_refused(self):
        os.remove(os.path.join(self.lib, "gba", "Base (USA).gba"))
        before = self.tree(self.tmp)
        r, out = self.update("--yes")
        self.assertIn("no clean base ROM", out)
        self.assertEqual(self.tree(self.tmp), before)

    def test_rollback_round_trip(self):
        self.update("--yes")
        # play the new version a little
        self.write(self.at("Saves", "GBA", self.STEM + ".sav"), b"battery-v2")
        self.write(self.at("States", "GBA", "mgba", self.STEM, "resume.state"), b"auto-v2")
        r, out = self.run_main("--card", self.card, "--library", self.lib, "--rollback", "hack", "--yes")
        self.assertIn("rolled back", out)
        self.assertEqual(rd(self.at("Games", "GBA", self.STEM + ".gba")), self.old)
        self.assertEqual(rd(self.at("Saves", "GBA", self.STEM + ".sav")), b"battery")
        self.assertEqual(rd(self.at("States", "GBA", "mgba", self.STEM, "resume.state")), b"auto")
        self.assertEqual(rd(self.at("States", "GBA", "gpsp", self.STEM, "resume.state")), b"auto2")
        with zipfile.ZipFile(os.path.join(self.lib, "gba", self.STEM + ".zip")) as z:
            self.assertEqual(z.read(self.STEM + ".gba"), self.old)
        # nothing lost: the new version's ROM, save and state sit in the rollback backup
        safety = [n for n in os.listdir(self.at("Backups", "hacks", "GBA", self.STEM)) if n.endswith("_rollback")]
        s = self.at("Backups", "hacks", "GBA", self.STEM, safety[0])
        self.assertEqual(rd(os.path.join(s, "Saves", "GBA", self.STEM + ".sav")), b"battery-v2")
        self.assertEqual(rd(os.path.join(s, "Games", "GBA", self.STEM + ".gba")), NEW)
        self.assertEqual(rd(os.path.join(s, "States", "GBA", "mgba", self.STEM, "resume.state")), b"auto-v2")

    def test_github_asset_update(self):
        self.write(self.at("Games", "GBA", "Gh v1.0.gba"), b"old")
        http = FakeHttp({RELEASE: release(), ASSET: (200, bps(BASE, NEW, [(1, NEW)]), None)})
        r, out = self.run_main("--card", self.card, "--library", self.lib, "--update", "gh", "--yes", http=http)
        self.assertEqual(r, 0, out)
        self.assertEqual(rd(self.at("Games", "GBA", "Gh v1.0.gba")), NEW)

    def test_over_adb_the_same_plan_runs_through_the_device_shell(self):
        def adb(*a):
            if a[0] == "devices":
                return 0, "List of devices attached\nabc\tdevice\n"
            if a[0] in ("push", "pull"):
                if not os.path.exists(a[1]):
                    return 1, "no such file"
                shutil.copy(a[1], a[2])
                return 0, ""
            r = subprocess.run(["sh", "-c", a[1]], capture_output=True, text=True)
            return r.returncode, r.stdout
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            r = hk.main(["--device", "--sd", self.card, "--library", self.lib, "--update", "hack", "--yes"],
                        hk.Ctx(http=FakeHttp({}), env=self.env, sleep=lambda s: None, adb=adb))
        self.assertEqual(r, 0, out.getvalue())
        self.assertEqual(rd(self.at("Games", "GBA", self.STEM + ".gba")), NEW)
        self.assertFalse(os.path.exists(self.at("States", "GBA", "mgba", self.STEM)))
        self.assertEqual(rd(self.at("Saves", "GBA", self.STEM + ".sav")), b"battery")
        (label,) = os.listdir(self.at("Backups", "hacks", "GBA", self.STEM))
        b = self.at("Backups", "hacks", "GBA", self.STEM, label)
        self.assertEqual(rd(os.path.join(b, "States", "GBA", "gpsp", self.STEM, "resume.state")), b"auto2")

    def test_a_move_across_filesystems_still_lands(self):
        real = os.rename

        def rename(a, b):
            if a.startswith(self.lib):  # the library is another volume than ~/ROMHacks
                raise OSError(errno.EXDEV, "Cross-device link")
            return real(a, b)
        with mock.patch("os.rename", rename):
            r, out = self.update("--yes")
        self.assertEqual(r, 0, out)
        with zipfile.ZipFile(os.path.join(self.lib, "gba", self.STEM + ".zip")) as z:
            self.assertEqual(z.read(self.STEM + ".gba"), NEW)

    def test_a_failure_mid_update_can_be_rolled_back(self):
        real = hk.LocalCard.apply

        def apply(card, op, src, dst):
            if op == "write" and dst == f"Games/GBA/{self.STEM}.gba":
                raise OSError(28, "No space left on device")
            return real(card, op, src, dst)
        with mock.patch.object(hk.LocalCard, "apply", apply):
            r, out = self.update("--yes")
        self.assertIn("--rollback hack", out)
        self.assertFalse(os.path.exists(self.at("Games", "GBA", self.STEM + ".gba")))
        r, out = self.run_main("--card", self.card, "--library", self.lib, "--rollback", "hack", "--yes")
        self.assertIn("rolled back", out)
        self.assertEqual(rd(self.at("Games", "GBA", self.STEM + ".gba")), self.old)
        self.assertEqual(rd(self.at("States", "GBA", "mgba", self.STEM, "resume.state")), b"auto")
        self.assertEqual(rd(self.at("Saves", "GBA", self.STEM + ".sav")), b"battery")

    def test_an_nfd_name_on_the_card_is_the_seed_entry(self):
        nfd = "Hack\u0301 (v1)"
        user = os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks.json")
        os.rename(self.at("Games", "GBA", self.STEM + ".gba"), self.at("Games", "GBA", nfd + ".gba"))
        os.rename(self.at("States", "GBA", "mgba", self.STEM), self.at("States", "GBA", "mgba", nfd))
        self.write(user, json.dumps({"hack": {"card": unicodedata.normalize("NFC", nfd) + ".gba"}}))
        r, out = self.update("--yes")
        self.assertEqual(r, 0, out)
        self.assertEqual(rd(self.at("Games", "GBA", nfd + ".gba")), NEW)
        self.assertFalse(os.path.exists(self.at("States", "GBA", "mgba", nfd)))

    def test_an_unreadable_slot_state_refuses(self):
        card = hk.LocalCard(self.card)
        card.read = lambda rel: None
        with self.assertRaisesRegex(hk.Refuse, "could not be read"):
            hk.seated(card, "GBA", self.STEM)

    def test_zip_with_two_roms_is_refused(self):
        inc = os.path.join(self.env["SLOT_HACKS_HOME"], "incoming", "hack")
        os.remove(os.path.join(inc, "hack-v2.bps"))
        with zipfile.ZipFile(os.path.join(inc, "two.zip"), "w") as z:
            z.writestr("a.gba", NEW)
            z.writestr("b.gba", NEW)
        r, out = self.update("--yes")
        self.assertIn("want exactly one", out)


if __name__ == "__main__":
    unittest.main()
