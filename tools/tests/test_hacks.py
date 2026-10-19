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


def vint(n):
    out = [n & 0x7f]
    n >>= 7
    while n:
        out.append(0x80 | n & 0x7f)
        n >>= 7
    return bytes(reversed(out))


def vcdiff(src, tgt, insts):
    """One VCD_SOURCE window over all of src with an Adler-32, from (code, ...) instructions using the
    default table's explicit-size codes: (19, size, address) COPY mode 0, (1, bytes) ADD, (0, size, byte) RUN."""
    data, inst, addr = b"", b"", b""
    for code, *a in insts:
        if code == 19:
            inst += bytes([19]) + vint(a[0])
            addr += vint(a[1])
        elif code == 1:
            inst += bytes([1]) + vint(len(a[0]))
            data += a[0]
        else:
            inst += bytes([0]) + vint(a[0])
            data += a[1]
    body = vint(len(tgt)) + b"\0" + vint(len(data)) + vint(len(inst)) + vint(len(addr)) + \
        zlib.adler32(tgt).to_bytes(4, "big") + data + inst + addr
    return b"\xd6\xc3\xc4\x00\x00" + bytes([1 | 4]) + vint(len(src)) + vint(0) + vint(len(body)) + body


def ppf(ver, records, image=None, undo=False, check=False, diz=False):
    """A PPF 1.0/2.0/3.0 of (offset, bytes) records; PPF2 (and PPF3 with check) carry image's block at 0x9320,
    PPF3 with undo the original bytes from image."""
    head = b"PPF" + ver + bytes([int(ver) // 10 - 1]) + b"test patch".ljust(50)
    if ver == b"20":
        head += u32(len(image)) + image[0x9320:0x9320 + 1024]
    elif ver == b"30":
        head += bytes([0, int(check), int(undo), 0]) + (image[0x9320:0x9320 + 1024] if check else b"")
    wide = 8 if ver == b"30" else 4
    body = b"".join(o.to_bytes(wide, "little") + bytes([len(d)]) + d + (image[o:o + len(d)] if undo else b"")
                    for o, d in records)
    tail = b"@BEGIN_FILE_ID.DIZ hello @END_FILE_ID.DIZ" + (24).to_bytes(2, "little") if diz else b""
    return head + body + tail


IMAGE = bytes(range(256)) * 200  # past 0x9320 + 1024, so PPF2's block exists


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

    def test_xdelta_copy_add_run_and_an_overlapping_copy(self):
        tgt = BASE[:100] + b"new!" + b"z" * 5 + b"ababab"
        p = vcdiff(BASE, tgt, [(19, 100, 0), (1, b"new!"), (0, 5, b"z"), (1, b"ab"), (19, 4, len(BASE) + 109)])
        self.assertEqual(hk.apply_patch(BASE, p, warn=lambda *_: None), tgt)
        self.assertEqual(hk.apply_patch(BASE, p, hk.crc_hex(tgt)), tgt)

    def test_xdelta_refuses_another_base_and_secondary_compression(self):
        p = vcdiff(BASE, BASE[:50], [(19, 50, 0)])
        with self.assertRaisesRegex(hk.PatchError, "checksum mismatch"):
            hk.apply_patch(b"x" + BASE[1:], p, warn=lambda *_: None)
        with self.assertRaisesRegex(hk.PatchError, "secondary compression"):
            hk.apply_patch(BASE, p[:4] + b"\x01" + p[5:])

    def test_ppf_1_2_3_apply_and_ignore_the_file_id_block(self):
        recs = [(5, b"abc"), (0x9400, b"XY")]
        want = bytearray(IMAGE)
        want[5:8], want[0x9400:0x9402] = b"abc", b"XY"
        for ver, kw in ((b"10", {}), (b"20", {"image": IMAGE}), (b"30", {"image": IMAGE, "undo": True, "check": True}),
                        (b"30", {"diz": True})):
            self.assertEqual(hk.apply_patch(IMAGE, ppf(ver, recs, **kw), warn=lambda *_: None), bytes(want), (ver, kw))

    def test_ppf_refuses_another_image_and_writes_nothing(self):
        other = bytearray(IMAGE)
        other[0x9330] ^= 1
        for p, why in ((ppf(b"20", [(5, b"abc")], IMAGE), "block check"),
                       (ppf(b"20", [(5, b"abc")], IMAGE + b"x"), "size mismatch"),
                       (ppf(b"30", [(5, b"abc")], IMAGE, check=True), "block check")):
            buf = bytearray(other)
            with self.assertRaisesRegex(hk.PatchError, why):
                hk.apply_ppf(buf, p)
            self.assertEqual(buf, other)
        buf = bytearray(IMAGE)
        buf[6] ^= 1
        before = bytes(buf)
        with self.assertRaisesRegex(hk.PatchError, "undo data mismatch"):  # the second record is checked first, nothing written
            hk.apply_ppf(buf, ppf(b"30", [(0x9400, b"XY"), (5, b"abc")], IMAGE, undo=True))
        self.assertEqual(bytes(buf), before)
        with self.assertRaisesRegex(hk.PatchError, "past the end"):
            hk.apply_ppf(bytearray(IMAGE), ppf(b"30", [(len(IMAGE) - 1, b"ab")]))
        with self.assertRaisesRegex(hk.PatchError, "truncated"):
            hk.apply_ppf(bytearray(IMAGE), ppf(b"30", [(5, b"abc")])[:-1])
        said = []
        hk.apply_patch(IMAGE, ppf(b"30", [(5, b"abc")]), warn=said.append)
        self.assertIn("no block check", said[0])


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
RELEASES = "https://api.github.com/repos/o/r/releases?per_page=10"


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
        # the library: the zip comes back loose under its member's name; RetroArch's state and .srm left alone
        self.assertEqual(rd(os.path.join(self.lib, "gba", self.STEM + ".gba")), NEW)
        self.assertFalse(os.path.exists(os.path.join(self.lib, "gba", self.STEM + ".zip")))
        self.assertEqual(rd(os.path.join(self.lib, "gba", self.STEM + ".state.auto")), b"ra")
        self.assertEqual(rd(os.path.join(self.lib, "gba", self.STEM + ".srm")), b"ra-save")
        self.assertIn("may not work with the new version", out)
        lb = os.path.join(self.env["SLOT_HACKS_HOME"], "backups", "GBA", self.STEM, label)
        self.assertEqual(sorted(os.listdir(lb)), ["Hack (v1).zip", "backup.json"])
        state = json.loads(rd(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks-state.json")))
        self.assertEqual((state["hack"]["version"], state["hack"]["crc32"]), ("2", hk.crc_hex(NEW)))
        self.assertEqual(state["hack"]["library"], self.STEM + ".gba")
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

    def test_a_neogeo_pocket_flash_save_is_copied_like_a_sav(self):
        class Card:
            def exists(self, p):
                return p == "Saves/NGP/Pocket.flash"

            def names(self, p):
                return []

            def isdir(self, p):
                return False
        self.assertEqual(hk.card_items(Card(), "NGP", "Pocket", "Pocket.ngc"),
                         [("Games/NGP/Pocket.ngc", "move"), ("Saves/NGP/Pocket.flash", "copy")])

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
        self.assertFalse(os.path.exists(os.path.join(self.lib, "gba", self.STEM + ".gba")))
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
        self.write(self.at("Games", "GBA", "it's a & b.gba"), b"12345")
        self.assertEqual(hk.AdbCard(adb, self.card).sizes("Games/GBA"),
                         {self.STEM + ".gba": len(NEW), "it's a & b.gba": 5})

    def test_a_move_across_filesystems_still_lands(self):
        real = os.rename

        def rename(a, b):
            if a.startswith(self.lib):  # the library is another volume than ~/ROMHacks
                raise OSError(errno.EXDEV, "Cross-device link")
            return real(a, b)
        with mock.patch("os.rename", rename):
            r, out = self.update("--yes")
        self.assertEqual(r, 0, out)
        self.assertEqual(rd(os.path.join(self.lib, "gba", self.STEM + ".gba")), NEW)

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

    def gh_by_crc(self, installed):
        """A GitHub hack whose file name carries no version, installed (card and library) as installed."""
        user = os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks.json")
        self.write(user, json.dumps({"gh": {"card": "Gh.gba"}}))
        self.write(self.at("Games", "GBA", "Gh.gba"), installed)
        with zipfile.ZipFile(os.path.join(self.lib, "gba", "Gh.zip"), "w") as z:
            z.writestr("Gh.gba", installed)
        v1 = BASE[:5] + b"one" + BASE[8:]
        rels = [{"tag_name": "v2.0", "assets": [{"name": "gh.bps", "browser_download_url": ASSET}]},
                {"tag_name": "v1.0", "assets": [{"name": "gh.bps", "browser_download_url": ASSET + "1"}]}]
        return FakeHttp({RELEASE: release(), RELEASES: (200, json.dumps(rels).encode(), None),
                         ASSET: (200, bps(BASE, NEW, [(1, NEW)]), None),
                         ASSET + "1": (200, bps(BASE, v1, [(1, v1)]), None)}), v1

    def test_check_identifies_the_installed_release_by_crc_and_records_it(self):
        http, v1 = self.gh_by_crc(BASE[:5] + b"one" + BASE[8:])
        rows = self.run_main("--card", self.card, "--library", self.lib, http=http)[0]
        row = [r for r in rows if r[1] == "gh"][0]
        self.assertEqual((row[2], row[4]), ("v1.0", "UPDATE AVAILABLE"))
        state = json.loads(rd(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks-state.json")))
        self.assertEqual((state["gh"]["version"], state["gh"]["crc32"]), ("v1.0", hk.crc_hex(v1)))

    def test_check_says_up_to_date_when_the_crc_is_the_latest_release(self):
        http, _ = self.gh_by_crc(NEW)
        row = [r for r in self.run_main("--card", self.card, "--library", self.lib, http=http)[0] if r[1] == "gh"][0]
        self.assertEqual((row[2], row[4]), ("v2.0", "up to date"))

    def test_an_unknown_build_is_an_update_and_all_takes_it(self):
        http, _ = self.gh_by_crc(b"some other build")
        r, out = self.run_main("--card", self.card, "--library", self.lib, "--all", "--dry-run", http=http)
        self.assertIn("UPDATE AVAILABLE (installed version unknown)", out)
        self.assertIn("updates available: gh", out.replace("hack, ", ""))
        self.assertIn("DRY RUN", out)

    def test_incoming_version_txt_names_the_version_and_a_bps_names_its_base(self):
        user = os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks.json")
        self.write(user, json.dumps({"hack": {"base_crc32": None}}))
        self.write(os.path.join(self.env["SLOT_HACKS_HOME"], "incoming", "hack", "version.txt"), "2.0.1\n")
        r, out = self.update("--yes")
        self.assertEqual(r, 0, out)
        state = json.loads(rd(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks-state.json")))
        self.assertEqual(state["hack"]["version"], "2.0.1")

    def test_check_reports_an_incoming_patch_as_ready(self):
        rows = self.run_main("--card", self.card, "--library", self.lib)[0]
        row = [r for r in rows if r[1] == "hack"][0]
        self.assertEqual(row[4], "UPDATE AVAILABLE (from incoming 2)")
        out = self.run_main("--library", self.lib)[1]
        self.assertIn("in neither the library nor the state file (install with --add <id>): gh", out)
        self.assertNotIn("not in library", out)

    def settings(self, **fields):
        self.write(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks.json"), json.dumps({"hack": fields}))

    def test_an_update_replaces_in_place_and_adds_no_file(self):
        games, lib = sorted(os.listdir(self.at("Games", "GBA"))), sorted(os.listdir(os.path.join(self.lib, "gba")))
        r, out = self.update("--yes")
        self.assertEqual(r, 0, out)
        self.assertEqual(sorted(os.listdir(self.at("Games", "GBA"))), games)
        lib[lib.index(self.STEM + ".zip")] = self.STEM + ".gba"  # the zip is swapped for its loose ROM
        self.assertEqual(sorted(os.listdir(os.path.join(self.lib, "gba"))), sorted(lib))

    def test_two_library_copies_are_ambiguous_until_the_settings_name_one(self):
        loose = os.path.join(self.lib, "gba", self.STEM + ".gba")
        self.write(loose, self.old)
        before = self.tree(self.tmp)
        r, out = self.update("--yes")
        self.assertIn("ambiguous", out)
        self.assertIn("Hack (v1).gba", out)
        self.assertEqual(self.tree(self.tmp), before)
        self.settings(library=self.STEM + ".zip")  # unzipping it would put a second loose copy beside the first
        before = self.tree(self.tmp)
        r, out = self.update("--yes")
        self.assertIn("already sits next to", out)
        self.assertEqual(self.tree(self.tmp), before)
        self.settings(library=self.STEM + ".gba")
        r, out = self.update("--yes")
        self.assertEqual(r, 0, out)
        self.assertEqual(rd(loose), NEW)
        with zipfile.ZipFile(os.path.join(self.lib, "gba", self.STEM + ".zip")) as z:  # never touched
            self.assertEqual(z.read(self.STEM + ".gba"), self.old)

    def test_a_clean_base_game_is_never_a_target(self):
        self.write(self.at("Games", "GBA", "Base (USA).gba"), BASE)
        self.settings(card="Base (USA).gba")
        before = self.tree(self.tmp)
        r, out = self.update("--yes")
        self.assertIn("clean base game", out)
        self.assertEqual(self.tree(self.tmp), before)

    def test_check_warns_about_two_versions_side_by_side_and_touches_neither(self):
        self.write(self.at("Games", "GBA", "Hack v2.gba"), b"other")
        before = self.tree(self.card)
        r, out = self.run_main("--card", self.card, "--library", self.lib)
        self.assertIn("possible duplicate on the card: GBA/Hack v2.gba looks like another version of Hack (v1).gba", out)
        self.assertEqual(self.tree(self.card), before)

    def test_a_file_renamed_since_install_is_refused_until_accepted(self):
        hk.write_state(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks-state.json"),
                       {"hack": {"version": "1", "card": "Hack (v0).gba"}})
        r, out = self.update("--yes")
        self.assertIn("--accept-rename", out)
        self.assertEqual(rd(self.at("Games", "GBA", self.STEM + ".gba")), self.old)
        r, out = self.update("--yes", "--accept-rename")
        self.assertEqual(r, 0, out)
        state = json.loads(rd(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks-state.json")))
        self.assertEqual((state["hack"]["card"], state["hack"]["library"]), (self.STEM + ".gba", self.STEM + ".gba"))

    def test_fix_library_zips_unzips_an_updated_hack_and_rollback_still_finds_the_old_rom(self):
        # an update made before the tool unzipped: the library zip (another name, a __MACOSX member) holds NEW
        zpath = os.path.join(self.lib, "gba", "Pokemon - Hack (v1).zip")
        os.remove(os.path.join(self.lib, "gba", self.STEM + ".zip"))
        with zipfile.ZipFile(zpath, "w") as z:
            z.writestr(self.STEM + ".gba", self.old)
            z.writestr("__MACOSX/._" + self.STEM + ".gba", b"apple")
        self.settings(library="Pokemon - Hack (v1).zip")
        r, out = self.update("--yes")
        self.assertEqual(r, 0, out)
        old_backup = os.path.join(self.env["SLOT_HACKS_HOME"], "backups", "GBA", self.STEM)
        (label,) = os.listdir(old_backup)
        os.remove(os.path.join(self.lib, "gba", self.STEM + ".gba"))  # the old tool rezipped instead
        with zipfile.ZipFile(zpath, "w") as z:
            z.writestr(self.STEM + ".gba", NEW)
        state_path = os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks-state.json")
        state = json.loads(rd(state_path))
        state["hack"]["library"] = "Pokemon - Hack (v1).zip"
        hk.write_state(state_path, state)
        self.write(os.path.join(self.lib, "gba", "Pokemon - Hack (v1).srm"), b"ra")

        fix = lambda *a: self.run_main("--library", self.lib, "--fix-library-zips", *a)
        before = self.tree(self.tmp)
        r, out = fix("--dry-run")
        self.assertIn("Pokemon - Hack (v1).zip -> Hack (v1).gba", out)
        self.assertIn("stop attaching", out)
        self.assertEqual(self.tree(self.tmp), before)
        r, out = fix("--yes")
        self.assertEqual(r, 0, out)
        self.assertEqual(rd(os.path.join(self.lib, "gba", self.STEM + ".gba")), NEW)
        self.assertFalse(os.path.exists(zpath))
        self.assertEqual(json.loads(rd(state_path))["hack"]["library"], self.STEM + ".gba")
        self.assertIn("already loose", fix("--yes")[1])
        # rollback skips the unzip backup (it holds NEW) and brings back the update's old zip
        self.settings()
        r, out = self.run_main("--card", self.card, "--library", self.lib, "--rollback", "hack", "--yes")
        self.assertIn("rolled back", out)
        with zipfile.ZipFile(zpath) as z:
            self.assertEqual(z.read(self.STEM + ".gba"), self.old)
        self.assertFalse(os.path.exists(os.path.join(self.lib, "gba", self.STEM + ".gba")))

    def test_fix_library_zips_refuses_a_zip_that_is_not_the_installed_version(self):
        hk.write_state(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks-state.json"),
                       {"hack": {"version": "2", "crc32": hk.crc_hex(NEW), "card": self.STEM + ".gba", "backup": "x"},
                        "gh": {"version": "v1.0", "crc32": "0"}})
        before = self.tree(self.tmp)
        r, out = self.run_main("--library", self.lib, "--fix-library-zips", "--yes")
        self.assertIn("the state file says", out)
        self.assertIn("gh: skipped, never updated", out)
        self.assertEqual(self.tree(self.tmp), before)

    def test_zip_with_two_roms_is_refused(self):
        inc = os.path.join(self.env["SLOT_HACKS_HOME"], "incoming", "hack")
        os.remove(os.path.join(inc, "hack-v2.bps"))
        with zipfile.ZipFile(os.path.join(inc, "two.zip"), "w") as z:
            z.writestr("a.gba", NEW)
            z.writestr("b.gba", NEW)
        r, out = self.update("--yes")
        self.assertIn("want exactly one", out)


class Add(Base):
    NAME = "Base Remix (v1.0).gba"

    def setUp(self):
        super().setUp()
        self.write(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks.json"), json.dumps({"remix": {
            "name": "Base Remix", "system": "GBA", "card": self.NAME, "source": "manual", "format": "bps",
            "base_crc32": hk.crc_hex(BASE), "cite": ["https://example.test"]}}))
        self.write(self.at("Games", "GBA", "Other.gba"), b"other")
        self.write(os.path.join(self.lib, "gba", "Base (USA).gba"), BASE)
        inc = os.path.join(self.env["SLOT_HACKS_HOME"], "incoming", "remix")
        self.write(os.path.join(inc, "remix.bps"), bps(BASE, NEW, [(1, NEW)]))
        self.write(os.path.join(inc, "version.txt"), "1.0\n")

    def add(self, *extra):
        return self.run_main("--card", self.card, "--library", self.lib, "--add", "remix", *extra)

    def test_add_writes_a_new_loose_file_on_both_and_check_and_update_track_it(self):
        before = self.tree(self.tmp)
        r, out = self.add("--dry-run")
        self.assertIn("DRY RUN", out)
        self.assertEqual(self.tree(self.tmp), before)
        r, out = self.add("--yes")
        self.assertEqual(r, 0, out)
        self.assertEqual(rd(self.at("Games", "GBA", self.NAME)), NEW)
        self.assertEqual(rd(os.path.join(self.lib, "gba", self.NAME)), NEW)
        self.assertEqual(rd(os.path.join(self.lib, "gba", "Base (USA).gba")), BASE)  # the base is never touched
        state = json.loads(rd(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks-state.json")))["remix"]
        self.assertEqual((state["version"], state["crc32"], state["library"]), ("1.0", hk.crc_hex(NEW), self.NAME))
        row = [r for r in self.run_main("--card", self.card, "--library", self.lib)[0] if r[1] == "remix"][0]
        self.assertEqual(row[2], "1.0")
        self.assertIn("already installed", self.add("--yes")[1])
        r, out = self.run_main("--card", self.card, "--library", self.lib, "--update", "remix", "--yes")
        self.assertIn("already installed", out)  # --update finds the added file

    def test_add_refuses_another_version_or_the_same_rom_under_another_name(self):
        tree = lambda: self.tree(self.tmp)
        self.write(self.at("Games", "GBA", "Base Remix (v0.9).gba"), b"older")
        before = tree()
        self.assertIn("the card already has Base Remix (v0.9).gba", self.add("--yes")[1])
        self.assertEqual(tree(), before)
        os.remove(self.at("Games", "GBA", "Base Remix (v0.9).gba"))
        self.write(self.at("Games", "GBA", "renamed.gba"), NEW)
        before = tree()
        self.assertIn("the card already has this ROM", self.add("--yes")[1])
        self.assertEqual(tree(), before)
        os.remove(self.at("Games", "GBA", "renamed.gba"))
        with zipfile.ZipFile(os.path.join(self.lib, "gba", "x.zip"), "w") as z:
            z.writestr("x.gba", NEW)
        self.assertIn("the library already has this ROM", self.add("--yes")[1])
        self.assertFalse(os.path.exists(self.at("Games", "GBA", self.NAME)))

    def test_add_reads_a_same_size_card_file_from_its_library_copy_and_pulls_only_without_one(self):
        self.write(self.at("Games", "GBA", "same.gba"), b"x" * len(NEW))
        self.write(os.path.join(self.lib, "gba", "same.gba"), b"x" * len(NEW))
        self.write(self.at("Games", "GBA", "card only.gba"), b"y" * len(NEW))
        pulled = []
        real = hk.LocalCard.read
        with mock.patch.object(hk.LocalCard, "read", lambda c, rel: pulled.append(rel) or real(c, rel)):
            r, out = self.add("--dry-run")
        self.assertIn("DRY RUN", out)
        self.assertEqual([p for p in pulled if p.startswith("Games/")], ["Games/GBA/card only.gba"])

    def test_add_refuses_leftover_saves_or_states_for_the_new_name(self):
        self.write(self.at("States", "GBA", "mgba", "Base Remix (v1.0)", "slot1.state"), b"s")
        self.assertIn("already has saves or states", self.add("--yes")[1])
        self.assertFalse(os.path.exists(self.at("Games", "GBA", self.NAME)))

    tree = Update.tree


def track(n, seed):
    return bytes((i * seed + i // 7) & 0xff for i in range(n * 2352))


@unittest.skipUnless(shutil.which("chdman"), "chdman not installed (brew install rom-tools): disc pipeline not tested")
class Disc(Base):
    """A two-track disc (data + audio with a pregap) as a .chd built here with chdman, patched by --add."""
    NAME = "Disc Hack (v1.0).chd"

    def setUp(self):
        super().setUp()
        self.t1, self.t2 = track(300, 3), track(200, 5)
        d = os.path.join(self.tmp, "src")
        self.write(os.path.join(d, "t1.bin"), self.t1)
        self.write(os.path.join(d, "t2.bin"), self.t2)
        self.write(os.path.join(d, "disc.cue"), 'FILE "t1.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n'
                   'FILE "t2.bin" BINARY\n  TRACK 02 AUDIO\n    INDEX 00 00:00:00\n    INDEX 01 00:02:00\n')
        self.base = os.path.join(self.lib, "psx", "Disc (USA).chd")
        os.makedirs(os.path.dirname(self.base))
        subprocess.run(["chdman", "createcd", "-i", os.path.join(d, "disc.cue"), "-o", self.base], check=True,
                       capture_output=True)
        self.entry(hk.crc_hex(self.t1))
        self.inc = os.path.join(self.env["SLOT_HACKS_HOME"], "incoming", "disc")
        self.patch([(1000, b"HACKED"), (len(self.t1) - 4, b"END!")])
        os.makedirs(self.at("Games", "PS1"))

    def entry(self, base_crc):
        self.write(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks.json"), json.dumps({"disc": {
            "name": "Disc Hack", "system": "PS1", "card": self.NAME, "source": "manual", "format": "ppf",
            "base_name": "Disc (USA)", "base_crc32": base_crc}}))

    def patch(self, recs):
        self.write(os.path.join(self.inc, "disc.ppf"), ppf(b"30", recs))

    def add(self, *extra):
        return self.run_main("--card", self.card, "--library", self.lib, "--add", "disc", *extra)

    def test_add_patches_track_1_keeps_track_2_and_the_base_disc(self):
        base = rd(self.base)
        r, out = self.add("--yes")
        self.assertEqual(r, 0, out)
        self.assertIn("round trip checked", out)
        new = self.at("Games", "PS1", self.NAME)
        self.assertEqual(rd(os.path.join(self.lib, "psx", self.NAME)), rd(new))
        self.assertEqual(rd(self.base), base)
        bins = hk.extract_disc(new, os.path.join(self.tmp, "x"))
        want = bytearray(self.t1)
        want[1000:1006], want[-4:] = b"HACKED", b"END!"
        self.assertEqual([rd(b) for b in bins], [bytes(want), self.t2])
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "x", "disc.cue")))
        state = json.loads(rd(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks-state.json")))["disc"]
        self.assertEqual(state["crc32"], hk.crc_hex(rd(new)))
        self.assertIn("already installed", self.add("--yes")[1])

    def test_update_replaces_the_disc_keeps_the_memory_card_and_moves_the_states(self):
        self.assertEqual(self.add("--yes")[0], 0)
        stem = os.path.splitext(self.NAME)[0]
        self.write(self.at("States", "PS1", "pcsx_rearmed", stem, "x.state"), b"state")
        self.write(self.at("Saves", "PS1", stem + ".sav"), b"memcard")
        self.write(self.at("Saves", "PS1", stem + ".disc"), b"disc")
        old = rd(self.at("Games", "PS1", self.NAME))
        self.patch([(2000, b"VERSION 2")])
        self.write(os.path.join(self.inc, "version.txt"), "2.0\n")
        r, out = self.run_main("--card", self.card, "--library", self.lib, "--update", "disc", "--yes")
        self.assertEqual(r, 0, out)
        new = self.at("Games", "PS1", self.NAME)
        self.assertNotEqual(rd(new), old)
        self.assertEqual(rd(os.path.join(self.lib, "psx", self.NAME)), rd(new))
        self.assertEqual(sorted(os.listdir(os.path.join(self.lib, "psx"))), ["Disc (USA).chd", self.NAME])
        self.assertEqual(rd(self.at("Saves", "PS1", stem + ".sav")), b"memcard")  # the memory card stays
        self.assertEqual(rd(self.at("Saves", "PS1", stem + ".disc")), b"disc")
        self.assertFalse(os.path.exists(self.at("States", "PS1", "pcsx_rearmed", stem)))
        (b,) = os.listdir(self.at("Backups", "hacks", "PS1", stem))
        bdir = self.at("Backups", "hacks", "PS1", stem, b)
        self.assertEqual(rd(os.path.join(bdir, "States", "PS1", "pcsx_rearmed", stem, "x.state")), b"state")
        self.assertEqual(rd(os.path.join(bdir, "Saves", "PS1", stem + ".sav")), b"memcard")
        self.assertEqual(rd(os.path.join(bdir, "Games", "PS1", self.NAME)), old)
        (lb,) = os.listdir(os.path.join(self.env["SLOT_HACKS_HOME"], "backups", "PS1", stem))
        self.assertEqual(rd(os.path.join(self.env["SLOT_HACKS_HOME"], "backups", "PS1", stem, lb, self.NAME)), old)

    def test_a_wrong_base_track_or_a_write_past_track_1_is_refused(self):
        self.entry("DEADBEEF")
        self.assertIn("track 1 of Disc (USA).chd is", self.add("--yes")[1])
        self.entry(hk.crc_hex(self.t1))
        self.patch([(len(self.t1), b"into track 2")])
        self.assertIn("past the end", self.add("--yes")[1])
        self.assertEqual(os.listdir(self.at("Games", "PS1")), [])
        self.assertEqual(sorted(os.listdir(os.path.join(self.lib, "psx"))), ["Disc (USA).chd"])

    def test_the_base_disc_is_never_an_update_target(self):
        self.write(os.path.join(self.env["SLOT_HACKS_CONFIG"], "hacks.json"), json.dumps({"disc": {
            "name": "Disc Hack", "system": "PS1", "card": "Disc (USA).chd", "source": "manual", "format": "ppf",
            "base_name": "Disc (USA)", "base_crc32": hk.crc_hex(self.t1)}}))
        shutil.copy(self.base, self.at("Games", "PS1", "Disc (USA).chd"))
        r, out = self.run_main("--card", self.card, "--library", self.lib, "--update", "disc", "--yes")
        self.assertIn("clean base game", out)


if __name__ == "__main__":
    unittest.main()
