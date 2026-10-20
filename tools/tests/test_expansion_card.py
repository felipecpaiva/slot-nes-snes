"""tools/expansion-card.py, offline: the refusals, the macOS and Linux plans, dry run writes nothing, and the
checks that run after the plan.

    python3 -m unittest tools/tests/test_expansion_card.py
"""
import contextlib
import importlib.util
import io
import os
import plistlib
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("expansion_card", os.path.join(HERE, "..", "expansion-card.py"))
ec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ec)

SIZE = 255869321216


def fake_mac(info=None, labels=("BOOT", "MuOs"), gpt_show=None):
    calls = []
    disk = {"TotalSize": SIZE, "DeviceBlockSize": 512, "WholeDisk": True, "RemovableMedia": True,
            "OSInternalMedia": False, "SystemImage": False, "Internal": True}
    disk.update(info or {})
    listing = {"AllDisksAndPartitions": [{"Partitions": [{"VolumeName": n} for n in labels]}]}

    def sh(argv, stdin=None):
        calls.append(argv)
        if argv[:3] == ["diskutil", "info", "-plist"]:
            return 0, plistlib.dumps(disk)
        if argv[:3] == ["diskutil", "list", "-plist"]:
            return 0, plistlib.dumps(listing)
        if argv[:3] == ["gpt", "-r", "show"] and gpt_show is not None:
            return 0, gpt_show.encode()
        return 0, b""
    return sh, calls


def main(argv, sh, system="Darwin"):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = ec.main(argv, sh=sh, system=lambda: system)
    return rc, out.getvalue(), err.getvalue()


ARGS = ["--disk", "disk4", "--size", str(SIZE), "--label", "MuOs"]
WRITES = ("gpt", "dd", "newfs_exfat", "mkdir", "sfdisk", "wipefs", "mkfs.exfat")


class Refusals(unittest.TestCase):
    def refused(self, argv=ARGS, **fake):
        sh, calls = fake_mac(**fake)
        rc, _, err = main(argv + ["--yes"], sh)
        self.assertEqual(rc, 2, err)
        self.assertFalse([c for c in calls if c[0] in WRITES or c[:2] == ["diskutil", "unmountDisk"]])
        return err

    def test_a_size_one_byte_off_is_refused(self):
        self.assertIn("not the 255869321215 you confirmed",
                      self.refused(["--disk", "disk4", "--size", str(SIZE - 1), "--label", "MuOs"]))

    def test_a_label_not_on_the_disk_is_refused(self):
        self.assertIn("no volume named 'MuOs'", self.refused(labels=("NO NAME",)))

    def test_the_system_disk_is_refused(self):
        self.assertIn("running system", self.refused(info={"OSInternalMedia": True}))

    def test_a_fixed_disk_is_refused(self):
        self.assertIn("not removable", self.refused(info={"RemovableMedia": False}))

    def test_a_partition_is_refused(self):
        self.assertIn("must be a whole disk", self.refused(["--disk", "disk4s6", "--size", str(SIZE), "--label", "MuOs"]))

    def test_a_system_name_that_is_a_path_is_refused(self):
        self.assertIn("letters and digits", self.refused(ARGS + ["--systems", "PS1,../Saves"]))


class MacPlan(unittest.TestCase):
    def test_a_dry_run_runs_nothing_that_writes(self):
        sh, calls = fake_mac()
        rc, out, _ = main(ARGS, sh)
        self.assertEqual(rc, 0)
        self.assertEqual([c[:2] for c in calls], [["diskutil", "info"], ["diskutil", "list"]])
        self.assertIn("dry run: nothing written", out)

    def test_one_diskutil_call_writes_both_partitions_without_an_efi_partition(self):
        plan = ec.mac_plan("disk4", ["PS1", "SEGACD"], "/tmp/m")
        layout = ["diskutil", "partitionDisk", "-noEFI", "disk4", "3", "GPT", "Free Space", "gap", "2048S",
                  f"%{ec.P1_TYPE}%", "%noformat%", "32768S", "ExFAT", "EXPANSION", "R"]
        zero = ["dd", "if=/dev/zero", "of=/dev/rdisk4s1", "bs=1m", "count=16"]
        self.assertIn(layout, plan)
        self.assertLess(plan.index(layout), plan.index(zero))
        self.assertIn(["mkdir", "-p", "/tmp/m/Games/PS1", "/tmp/m/Games/SEGACD"], plan)

    def test_gpt_only_reads(self):
        # macOS 27 gpt(8) refuses every write verb: "operation not permitted", even as root
        self.assertFalse([s for s in ec.mac_plan("disk4", ["PS1"], "/tmp/m") if s[0] in ("gpt", "newfs_exfat")])

    def test_a_failure_after_the_table_says_the_card_is_not_finished(self):
        sh, _ = fake_mac()

        def failing(argv, stdin=None):
            return (1, b"Resource busy") if argv[0] == "dd" else sh(argv, stdin)
        rc, out, err = main(ARGS + ["--yes"], failing)
        self.assertEqual(rc, 1)
        self.assertIn("ok: diskutil partitionDisk", out)
        self.assertIn("do not put it in the device", err)

    def test_a_failure_before_the_table_says_nothing_was_erased(self):
        sh, calls = fake_mac()

        def failing(argv, stdin=None):
            return (1, b"busy") if argv[:2] == ["diskutil", "unmountDisk"] else sh(argv, stdin)
        rc, _, err = main(ARGS + ["--yes"], failing)
        self.assertEqual(rc, 1)
        self.assertIn("nothing was erased yet", err)
        self.assertFalse([c for c in calls if c[:2] == ["diskutil", "partitionDisk"]])

    def test_a_table_with_an_efi_partition_first_fails_the_check(self):
        efi = ("      start       size  index  contents\n"
               "         40     409600      1  GPT part - C12A7328-F81F-11D2-BA4B-00A0C93EC93B\n"
               "     409640      31256      2  GPT part - 8DA63339-0007-60C0-C436-083AC8230908\n")
        ours = ("       2048      32768      1  GPT part - 8DA63339-0007-60C0-C436-083AC8230908\n"
                "      34816  499709919      2  GPT part - EBD0A0A2-B9E5-4433-87C0-68B6B72699C7\n")
        self.assertFalse(ec.layout_ok("disk4", 512, fake_mac(gpt_show=efi)[0]))
        self.assertTrue(ec.layout_ok("disk4", 512, fake_mac(gpt_show=ours)[0]))


class LinuxPlan(unittest.TestCase):
    def test_partition_names_follow_the_kernel(self):
        self.assertEqual(ec.part("/dev/mmcblk1", 1), "/dev/mmcblk1p1")
        self.assertEqual(ec.part("/dev/sdb", 2), "/dev/sdb2")

    def test_the_sfdisk_script_places_both_partitions(self):
        plan = ec.linux_plan("/dev/sdb", ["PS1"], "/tmp/m", ["/media/f/MuOs"])
        self.assertEqual(plan[0], ["umount", "/media/f/MuOs"])
        script = next(s for s in plan if s[0] == "sfdisk")[2]
        self.assertIn(f"start=2048, size=32768, type={ec.P1_TYPE}", script)
        self.assertIn(f"start=34816, type={ec.P2_TYPE}", script)
        zero = ["dd", "if=/dev/zero", "of=/dev/sdb", "bs=1M", "seek=1", "count=18", "conv=fsync"]
        self.assertLess(plan.index(zero), plan.index(next(s for s in plan if s[0] == "sfdisk")))

    def test_lsblk_rows_are_read(self):
        rows = ("/dev/sdb disk 255869321216 1  \n"
                "/dev/sdb1 part 8388608 0 BOOT \n"
                "/dev/sdb6 part 247100000000 0 MuOs /media/f/MuOs\n")

        def sh(argv, stdin=None):
            return (0, rows.encode()) if argv[0] == "lsblk" else (0, b"/dev/nvme0n1p2\n")
        d = ec.linux_disk("/dev/sdb", sh)
        self.assertEqual((d["size"], d["removable"], d["system"]), (SIZE, True, False))
        self.assertEqual((d["labels"], d["mounted"]), (["BOOT", "MuOs"], ["/media/f/MuOs"]))


class ZeroCheck(unittest.TestCase):
    def test_one_stray_byte_in_p1_fails(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(bytes(ec.P1_SIZE))
            f.flush()
            self.assertTrue(ec.p1_is_zero(f.name))
            f.seek(ec.P1_SIZE - 1)
            f.write(b"\x01")
            f.flush()
            self.assertFalse(ec.p1_is_zero(f.name))


if __name__ == "__main__":
    unittest.main()
