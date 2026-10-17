"""tools/fetch-labels.py PlayStation route (ADR 0069), offline: generated ISO9660 tracks, a PBP and a fake CHD,
a fake HTTP layer and a fake adb. ScreenScraper is never contacted.

    python3 -m unittest tools/tests/test_fetch_labels_ps1.py
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

COVER = fl.PNG + b"cover" * 30
DISC = fl.PNG + b"disc" * 30
SS_ENV = {"SS_DEVID": "d", "SS_DEVPASSWORD": "p"}
JEU = {"response": {"jeu": {"medias": [
    {"type": "ss", "region": "us", "url": "https://x.test/shot.png"},
    {"type": "box-2D-back", "region": "us", "url": "https://x.test/back.png"},
    {"type": "support-texture", "region": "us", "url": "https://x.test/texture.png"},
    {"type": "box-2D", "region": "jp", "url": "https://x.test/cover-jp.png"},
    {"type": "box-2D", "region": "us", "url": "https://x.test/cover-us.png"},
    {"type": "support-2D", "region": "eu", "url": "https://x.test/disc-eu.png"},
    {"type": "support-2D", "region": "us", "url": "https://x.test/disc-us.png"}]}}}


def iso(serial_line, raw=False):
    """A data track: PVD at 16, root directory at 20 holding SYSTEM.CNF at 21 (the layout ps1.rs reads)."""
    sectors = [bytes(2048)] * 22
    pvd = bytearray(2048)
    pvd[0], pvd[1:6] = 1, b"CD001"
    root = bytearray(34)
    root[0], root[2:6], root[10:14] = 34, (20).to_bytes(4, "little"), (2048).to_bytes(4, "little")
    pvd[156:190] = root
    name = b"SYSTEM.CNF;1"
    rec = bytearray(34 + len(name))
    rec[0], rec[2:6], rec[32] = len(rec), (21).to_bytes(4, "little"), len(name)
    rec[33:33 + len(name)] = name
    sectors[16], sectors[20] = bytes(pvd), bytes(rec).ljust(2048, b"\0")
    sectors[21] = f"BOOT = cdrom:\\{serial_line};1\r\nTCB = 4\r\n".encode().ljust(2048, b"\0")
    if not raw:
        return b"".join(sectors)
    return b"".join(fl.SYNC + bytes(3) + b"\x02" + bytes(8) + s + bytes(2352 - 24 - 2048) for s in sectors)


def pbp(disc_id):
    key, value = b"DISC_ID\0", disc_id.encode() + b"\0"
    sfo = bytearray(b"\0PSF" + (0x101).to_bytes(4, "little"))
    keys, data = 20 + 16, 20 + 16 + len(key)
    sfo += keys.to_bytes(4, "little") + data.to_bytes(4, "little") + (1).to_bytes(4, "little")
    sfo += (0).to_bytes(2, "little") + (0x204).to_bytes(2, "little") + len(value).to_bytes(4, "little")
    sfo += len(value).to_bytes(4, "little") + (0).to_bytes(4, "little")
    sfo += key + value
    head = b"\0PBP" + (0x10000).to_bytes(4, "little") + (40).to_bytes(4, "little")
    head += (40 + len(sfo)).to_bytes(4, "little") + bytes(24)
    return head + bytes(sfo) + b"PSISOIMG0000" + bytes(64)


class Http:
    def __init__(self, jeu=(200, json.dumps(JEU).encode(), None)):
        self.calls, self.jeu = [], jeu

    def get(self, url):
        self.calls.append(url)
        if url.startswith(fl.SS_API + "jeuInfos.php"):
            return self.jeu
        if url.startswith("https://x.test/cover"):
            return 200, COVER, None
        if url.startswith("https://x.test/disc"):
            return 200, DISC, None
        if url.startswith("https://x.test/"):
            return 200, fl.PNG + b"wrong media", None
        return 404, b"", None

    def jeu_params(self):
        return [dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(u).query)) for u in self.calls
                if u.startswith(fl.SS_API + "jeuInfos.php")]


class Ps1(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.card = os.path.join(self.tmp, "card")
        self.games = os.path.join(self.card, "Games", "PS1")
        os.makedirs(self.games)

    def put(self, name, data):
        fl.spit(os.path.join(self.games, name), data if isinstance(data, bytes) else data.encode())

    def cue(self, stem, track_data, raw=True):
        self.put(stem + ".bin", track_data)
        self.put(stem + ".cue", f'FILE "{stem}.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')

    def run_tool(self, args, http=None, env=SS_ENV):
        self.http = http or Http()
        ctx = fl.Ctx(http=self.http, env=dict(env, SLOT_LABELS_CACHE=os.path.join(self.tmp, "cache")),
                     sleep=lambda s: None)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            stats = fl.main(["--card", self.card, "--only", "PS1"] + args, ctx)
        self.out = out.getvalue()
        return stats

    def cover(self, stem):
        p = os.path.join(self.card, "Labels", "PS1", stem + ".png")
        return fl.slurp(p) if os.path.exists(p) else None

    def disc(self, stem):
        p = os.path.join(self.card, "Labels", "PS1", "disc", stem + ".png")
        return fl.slurp(p) if os.path.exists(p) else None

    def test_playstation_is_screenscraper_system_57_with_its_disc_extensions(self):
        folder, exts, dats, ssid = fl.SYSTEMS["PS1"]
        self.assertEqual((folder, exts, dats, ssid), ("psx", {".cue", ".chd", ".pbp", ".m3u"}, [], 57))
        self.assertEqual(fl.PS1_MEDIA, (("box-2D", ""), ("support-2D", "disc")))

    def test_serials_from_system_cnf_and_param_sfo_read_as_one_form(self):
        self.assertEqual(fl.norm_serial("SLUS_005.94"), "SLUS-00594")
        self.assertEqual(fl.norm_serial("SLES00972"), "SLES-00972")
        self.assertEqual(fl.norm_serial("SCPS-10031"), "SCPS-10031")
        self.assertIsNone(fl.norm_serial("PSX.EXE"))
        self.assertIsNone(fl.norm_serial("ABCD_123.45"))

    def test_a_cue_game_is_matched_by_its_system_cnf_serial_and_gets_cover_and_disc(self):
        track = iso("SLUS_005.94", raw=True)
        self.cue("Final Fantasy VII (USA)", track)
        stats = self.run_tool([])
        self.assertEqual(stats["written"], 2)
        self.assertEqual(self.cover("Final Fantasy VII (USA)"), COVER)
        self.assertEqual(self.disc("Final Fantasy VII (USA)"), DISC)
        (p,) = self.http.jeu_params()
        self.assertEqual(p["serialnum"], "SLUS-00594")
        self.assertEqual(p["systemeid"], "57")
        self.assertEqual(p["romtype"], "iso")
        self.assertEqual(p["romnom"], "Final Fantasy VII (USA).bin")
        self.assertEqual(p["crc"], f"{zlib.crc32(track) & 0xffffffff:08X}")
        self.assertEqual(p["romtaille"], str(len(track)))
        self.assertNotIn("https://x.test/shot.png", self.http.calls)
        self.assertNotIn("https://x.test/texture.png", self.http.calls)

    def test_a_plain_2048_byte_track_reads_the_same_serial(self):
        p = os.path.join(self.tmp, "plain.iso")
        fl.spit(p, iso("SCES_009.69"))
        self.assertEqual(fl.iso_serial(p), "SCES-00969")
        fl.spit(p, iso("SCES_009.69", raw=True))
        self.assertEqual(fl.iso_serial(p), "SCES-00969")

    def test_a_pbp_is_matched_by_the_disc_id_in_its_param_sfo(self):
        self.put("Breath of Fire III.PBP", pbp("SLUS00422"))
        stats = self.run_tool([])
        self.assertEqual(stats["written"], 2)
        (p,) = self.http.jeu_params()
        self.assertEqual(p["serialnum"], "SLUS-00422")
        self.assertEqual(p["romnom"], "Breath of Fire III.PBP")
        self.assertEqual(self.cover("Breath of Fire III"), COVER)

    def test_a_chd_has_no_serial_and_is_matched_by_crc_size_and_name(self):
        chd = b"MComprHD" + bytes(200)
        self.put("Ape Escape (USA).chd", chd)
        stats = self.run_tool([])
        self.assertEqual(stats["written"], 2)
        (p,) = self.http.jeu_params()
        self.assertNotIn("serialnum", p)
        self.assertEqual((p["crc"], p["romnom"], p["romtaille"]),
                         (f"{zlib.crc32(chd) & 0xffffffff:08X}", "Ape Escape (USA).chd", str(len(chd))))
        self.assertIn("no serial", self.out)
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "cache", "ss", "PS1", "box-2D", p["crc"] + ".png")))

    def test_an_m3u_is_one_game_from_its_first_disc_and_the_discs_it_names_are_skipped(self):
        self.cue("Chrono Cross (USA) (Disc 1)", iso("SLUS_010.41", raw=True))
        self.cue("Chrono Cross (USA) (Disc 2)", iso("SLUS_010.80", raw=True))
        self.put("Chrono Cross (USA).m3u", "Chrono Cross (USA) (Disc 1).cue\r\n# comment\nChrono Cross (USA) (Disc 2).cue\n")
        stats = self.run_tool([])
        self.assertEqual(stats["matched"], 1)
        (p,) = self.http.jeu_params()
        self.assertEqual(p["serialnum"], "SLUS-01041")
        self.assertEqual(self.cover("Chrono Cross (USA)"), COVER)
        self.assertEqual(self.disc("Chrono Cross (USA)"), DISC)
        self.assertEqual(sorted(os.listdir(os.path.join(self.card, "Labels", "PS1"))), ["Chrono Cross (USA).png", "disc"])

    def test_disc_tagged_chds_without_a_playlist_are_one_game_under_slots_title(self):
        self.put("Alone in the Dark - The New Nightmare (USA) (Disc 2).chd", b"MComprHD2" + bytes(64))
        self.put("Alone in the Dark - The New Nightmare (USA) (Disc 1).chd", b"MComprHD1" + bytes(64))
        self.put("Brigandine (Disc 1 of 2) [ENG].chd", b"MComprHDb" + bytes(64))
        stats = self.run_tool([])
        self.assertEqual(stats["matched"], 2)
        romnoms = sorted(p["romnom"] for p in self.http.jeu_params())
        self.assertEqual(romnoms, ["Alone in the Dark - The New Nightmare (USA) (Disc 1).chd",
                                   "Brigandine (Disc 1 of 2) [ENG].chd"])
        self.assertEqual(self.cover("Alone in the Dark - The New Nightmare (USA)"), COVER)
        self.assertEqual(self.cover("Brigandine (Disc 1 of 2) [ENG]"), COVER)

    def test_the_disc_region_is_preferred_when_the_name_has_no_tag(self):
        ss = fl.ScreenScraper(fl.Ctx(env={}))
        medias = JEU["response"]["jeu"]["medias"]
        self.assertEqual(ss.pick(medias, "Biohazard", "box-2D", "jp")["url"], "https://x.test/cover-jp.png")
        self.assertEqual(ss.pick(medias, "Biohazard (USA)", "box-2D", "jp")["url"], "https://x.test/cover-us.png")
        self.assertEqual(ss.pick(medias, "Medievil", "support-2D", "eu")["url"], "https://x.test/disc-eu.png")

    def test_a_game_with_both_images_is_skipped_and_one_with_only_a_cover_gets_its_disc(self):
        self.put("A (USA).chd", b"MComprHDa")
        self.put("B (USA).chd", b"MComprHDb")
        labels = os.path.join(self.card, "Labels", "PS1")
        os.makedirs(os.path.join(labels, "disc"))
        old = fl.PNG + b"own cover"
        for p in ("A (USA).png", "disc/A (USA).png", "B (USA).png"):
            fl.spit(os.path.join(labels, p), old)
        stats = self.run_tool([])
        self.assertEqual((stats["skipped"], stats["matched"], stats["written"]), (1, 1, 1))
        self.assertEqual(self.cover("B (USA)"), old)
        self.assertEqual(self.disc("B (USA)"), DISC)
        self.assertEqual(len(self.http.jeu_params()), 1)

    def test_one_call_serves_both_images_and_a_rerun_uses_the_cache(self):
        self.put("Ape Escape (USA).chd", b"MComprHD")
        self.run_tool([])
        shutil.rmtree(os.path.join(self.card, "Labels"))
        stats = self.run_tool([])
        self.assertEqual(stats["written"], 2)
        self.assertEqual(self.http.jeu_params(), [])

    def test_a_disc_is_read_once_and_not_at_all_in_a_dry_run_or_without_credentials(self):
        self.put("Ape Escape (USA).chd", b"MComprHD")
        reads = []
        real = fl.file_crc
        fl.file_crc = lambda p: reads.append(p) or real(p)
        self.addCleanup(setattr, fl, "file_crc", real)
        self.run_tool(["--dry-run"])
        self.run_tool([], env={})
        self.assertEqual(reads, [])
        self.run_tool([], Http((200, json.dumps({"response": {"jeu": {"medias": []}}}).encode(), None)))
        self.run_tool([])
        self.assertEqual(len(reads), 1)
        self.assertEqual(len(self.http.jeu_params()), 0)

    def test_no_disc_scan_is_missing_never_a_screenshot(self):
        jeu = {"response": {"jeu": {"medias": [m for m in JEU["response"]["jeu"]["medias"]
                                               if m["type"] != "support-2D"]}}}
        self.put("Ape Escape (USA).chd", b"MComprHD")
        stats = self.run_tool([], Http((200, json.dumps(jeu).encode(), None)))
        self.assertEqual((stats["written"], stats["missing"]), (1, 1))
        self.assertIsNone(self.disc("Ape Escape (USA)"))
        self.assertEqual(self.cover("Ape Escape (USA)"), COVER)

    def test_a_bin_is_never_a_game_and_a_cue_with_no_track_is_reported(self):
        self.put("Loose.bin", iso("SLUS_000.01"))
        self.put("Broken (USA).cue", 'FILE "Missing.bin" BINARY\n')
        stats = self.run_tool([])
        self.assertEqual((stats["matched"], stats["unknown"]), (0, 1))
        self.assertIn("unreadable disc  PS1/Broken (USA)", self.out)
        self.assertEqual(self.http.jeu_params(), [])

    def test_dry_run_never_calls_screenscraper_and_writes_nothing(self):
        self.put("Ape Escape (USA).chd", b"MComprHD")
        stats = self.run_tool(["--dry-run"])
        self.assertEqual(stats["written"], 2)
        self.assertEqual(self.http.calls, [])
        self.assertFalse(os.path.exists(os.path.join(self.card, "Labels")))

    def test_device_mode_reads_the_library_lists_both_label_folders_and_pushes_the_disc_folder(self):
        lib = os.path.join(self.tmp, "lib", "psx")
        os.makedirs(lib)
        fl.spit(os.path.join(lib, "Ape Escape (USA).chd"), b"MComprHD")
        fl.spit(os.path.join(lib, "Bushido Blade (USA).chd"), b"MComprHDbb")
        sd = "/mnt/sdcard"
        files = {f"{sd}/Games/PS1/Ape Escape (USA).chd": b"", f"{sd}/Games/PS1/Bushido Blade (USA).chd": b"",
                 f"{sd}/Labels/PS1/Bushido Blade (USA).png": b"x", f"{sd}/Labels/PS1/disc/Bushido Blade (USA).png": b"x"}
        listed, pushed = [], {}

        def adb(*a):
            if a[0] == "devices":
                return 0, "abc\tdevice\n"
            if a[0] == "shell" and a[1].startswith("for f in"):
                d = a[1].split("'")[1].rstrip("/") + "/"
                listed.append(d)
                return 0, "".join(k[len(d):] + "\n" for k in files if k.startswith(d) and "/" not in k[len(d):])
            if a[0] == "push":
                base = a[1].rstrip("/.")
                for top, _, names in os.walk(base):
                    for n in names:
                        rel = os.path.relpath(os.path.join(top, n), base)
                        pushed[a[2].rstrip("/") + "/" + rel] = fl.slurp(os.path.join(top, n))
            return 0, ""
        self.http = Http()
        ctx = fl.Ctx(http=self.http, adb=adb, env=dict(SS_ENV, SLOT_LABELS_CACHE=os.path.join(self.tmp, "cache")),
                     sleep=lambda s: None)
        with contextlib.redirect_stdout(io.StringIO()):
            stats = fl.main(["--device", "--library", os.path.dirname(lib), "--only", "PS1"], ctx)
        self.assertEqual((stats["skipped"], stats["written"]), (1, 2))
        self.assertIn(f"{sd}/Labels/PS1/disc/", listed)
        self.assertEqual(pushed, {f"{sd}/Labels/PS1/Ape Escape (USA).png": COVER,
                                  f"{sd}/Labels/PS1/disc/Ape Escape (USA).png": DISC})


if __name__ == "__main__":
    unittest.main()
