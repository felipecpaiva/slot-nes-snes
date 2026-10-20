#!/usr/bin/env python3
"""Prepare an Expansion Card: the second TF card (TF2) of a BaseOS device, holding whole systems' game folders
that slot binds under Games/ on the main card at launch (System/expansion.sh, ADR 0098).

    python3 tools/expansion-card.py --disk disk4 --size 255869321216 --label MuOs             # dry run
    sudo python3 tools/expansion-card.py --disk disk4 --size 255869321216 --label MuOs --yes  # erases disk4

Layout (GPT):
  p1  16 MiB at 1 MiB, type Linux reserved, every byte zero (written as zeros after the table, then read back).
      BaseOS rcS mounts TF2 p1 as the main card when it mounts as vfat, exfat or `-t auto` (after one
      fsck.fat -a), so p1 must hold no filesystem at all. Zero bytes carry no superblock for any filesystem
      the kernel knows, and fsck.fat refuses a zero boot sector without writing.
  p2  the rest, from 17 MiB, exFAT labelled EXPANSION, with Games/<SYS>/ for each --systems entry.

macOS: one `diskutil partitionDisk -noEFI` writes the table and formats p2. -noEFI matters: without it a GPT
gets a 200 MiB FAT32 EFI partition first, which would become TF2 p1 and the main card. gpt(8) cannot be used:
since macOS 27 it only runs `show`, every write verb fails "operation not permitted", root or not.

Refuses unless --disk is a whole removable disk (never the system disk), --size is its exact size in bytes and
--label is the name of a volume on it now. Without --yes it only prints the commands.
"""
import argparse
import os
import platform
import plistlib
import re
import subprocess
import sys

MIB = 1 << 20
P1_START, P1_SIZE = 1 * MIB, 16 * MIB
P2_START = P1_START + P1_SIZE
ZEROED = P1_SIZE + 2 * MIB  # Linux: p1 and the head of p2, before the table
P1_TYPE = "8DA63339-0007-60C0-C436-083AC8230908"
P2_TYPE = "EBD0A0A2-B9E5-4433-87C0-68B6B72699C7"
LABEL = "EXPANSION"
BEFORE = "nothing was erased yet: the card is as it was."
AFTER = ("the card is erased but not finished: do not put it in the device. "
         f"Run the tool again with --label {LABEL} (or the label it now shows) to redo it.")


class Refuse(Exception):
    pass


def run(argv, stdin=None):
    r = subprocess.run(argv, input=stdin.encode() if stdin else None, capture_output=True)
    return r.returncode, r.stdout + r.stderr


def systems_of(text):
    names = [s.strip() for s in text.split(",") if s.strip()]
    bad = [s for s in names if not re.fullmatch(r"[A-Za-z0-9]+", s)]
    if bad or not names:
        raise Refuse(f"system folder names are letters and digits only, got {text!r}")
    return names


def mac_disk(disk, sh=run):
    if not re.fullmatch(r"disk\d+", disk):
        raise Refuse(f"--disk must be a whole disk identifier like disk4, got {disk!r}")
    rc, out = sh(["diskutil", "info", "-plist", disk])
    if rc != 0:
        raise Refuse(f"diskutil does not know {disk}")
    info = plistlib.loads(out)
    rc, out = sh(["diskutil", "list", "-plist", disk])
    listing = plistlib.loads(out) if rc == 0 else {}
    parts = [p for d in listing.get("AllDisksAndPartitions", []) for p in d.get("Partitions", [])]
    return {
        "size": info.get("TotalSize") or info.get("Size"),
        "block": info.get("DeviceBlockSize", 512),
        "whole": info.get("WholeDisk", False),
        "removable": info.get("RemovableMedia", False) or info.get("VirtualOrPhysical") == "Virtual",
        "system": info.get("OSInternalMedia", True) or info.get("SystemImage", False),
        "labels": [p.get("VolumeName") for p in parts if p.get("VolumeName")],
        "mounted": [p.get("MountPoint") for p in parts if p.get("MountPoint")],
    }


def linux_disk(dev, sh=run):
    if not re.fullmatch(r"/dev/(sd[a-z]+|mmcblk\d+|loop\d+)", dev):
        raise Refuse(f"--disk must be a whole disk like /dev/sdb or /dev/mmcblk1, got {dev!r}")
    rc, out = sh(["lsblk", "-bnrpo", "NAME,TYPE,SIZE,RM,LABEL,MOUNTPOINT", dev])
    if rc != 0:
        raise Refuse(f"lsblk does not know {dev}")
    rows = [l.split(" ") + [""] * 6 for l in out.decode().splitlines()]
    disk = next((r for r in rows if r[0] == dev), None)
    if not disk:
        raise Refuse(f"lsblk does not list {dev}")
    rc, root = sh(["findmnt", "-nvo", "SOURCE", "/"])
    root = root.decode().strip()

    def unescape(s):
        return re.sub(r"\\x([0-9a-f]{2})", lambda m: chr(int(m.group(1), 16)), s)

    return {
        "size": int(disk[2]),
        "block": 512,
        "whole": disk[1] in ("disk", "loop"),
        "removable": disk[3] == "1" or disk[1] == "loop",
        "system": any(r[0] == root for r in rows),
        "labels": [unescape(r[4]) for r in rows if r[4]],
        "mounted": [unescape(r[5]) for r in rows if r[5]],
    }


def refusal(d, size, label):
    if not d["whole"]:
        return "that is a partition, give the whole disk"
    if d["system"]:
        return "that disk holds the running system"
    if not d["removable"]:
        return "that disk is not removable media"
    if d["size"] != size:
        return f"that disk is {d['size']} bytes, not the {size} you confirmed"
    if label not in d["labels"]:
        return f"no volume named {label!r} on that disk (it has {', '.join(d['labels']) or 'none'})"
    return None


def part(disk, n, raw=False):
    if disk.startswith("/dev/"):
        return f"{disk}{'p' if disk[-1].isdigit() else ''}{n}"
    return f"/dev/{'r' if raw else ''}{disk}s{n}"


def mac_plan(disk, systems, mnt):
    # Sizes in S (512-byte sectors, whatever the device block). The leading gap is counted from sector 0,
    # so p1 lands at 1 MiB; layout_ok checks that diskutil kept it there.
    return [
        ["diskutil", "unmountDisk", "force", disk],
        ["diskutil", "partitionDisk", "-noEFI", disk, "3", "GPT",
         "Free Space", "gap", f"{P1_START // 512}S",
         f"%{P1_TYPE}%", "%noformat%", f"{P1_SIZE // 512}S",
         "ExFAT", LABEL, "R"],
        ["diskutil", "unmountDisk", "force", disk],
        ["dd", "if=/dev/zero", f"of={part(disk, 1, raw=True)}", "bs=1m", f"count={P1_SIZE // MIB}"],
        ["diskutil", "mount", "-mountPoint", mnt, part(disk, 2)],
        ["mkdir", "-p"] + [f"{mnt}/Games/{x}" for x in systems],
        ["diskutil", "unmount", part(disk, 2)],
    ]


def linux_plan(disk, systems, mnt, mounted):
    script = (f"label: gpt\nstart={P1_START // 512}, size={P1_SIZE // 512}, type={P1_TYPE}\n"
              f"start={P2_START // 512}, type={P2_TYPE}\n")
    return [["umount", m] for m in mounted] + [
        ["wipefs", "-a", disk],
        ["dd", "if=/dev/zero", f"of={disk}", "bs=1M", f"seek={P1_START // MIB}", f"count={ZEROED // MIB}", "conv=fsync"],
        ["sfdisk", disk, script],
        ["udevadm", "settle"],
        ["mkfs.exfat", "-L", LABEL, part(disk, 2)],
        ["mount", "-t", "exfat", part(disk, 2), mnt],
        ["mkdir", "-p"] + [f"{mnt}/Games/{x}" for x in systems],
        ["umount", mnt],
    ]


def p1_is_zero(path):
    with open(path, "rb") as f:
        left = P1_SIZE
        while left:
            chunk = f.read(min(left, MIB))
            if not chunk or chunk.count(0) != len(chunk):
                return False
            left -= len(chunk)
    return True


def layout_ok(disk, block, sh=run):
    if disk.startswith("/dev/"):
        rc, out = sh(["sfdisk", "-d", disk])
        starts = re.findall(r"start=\s*(\d+)", out.decode())
        return rc == 0 and [int(x) * 512 for x in starts] == [P1_START, P2_START]
    rc, out = sh(["gpt", "-r", "show", disk])
    rows = [l.split() for l in out.decode().splitlines()]
    starts = [int(r[0]) * block for r in rows if len(r) >= 6 and r[3] == "GPT" and r[4] == "part"]
    return rc == 0 and starts == [P1_START, P2_START]


def show(argv):
    return " ".join(a if re.fullmatch(r"[\w@%+=:,./-]+", a) else repr(a) for a in argv)


def main(argv=None, sh=run, system=platform.system):
    ap = argparse.ArgumentParser(description="Erase a TF card into an Expansion Card (dry run unless --yes).")
    ap.add_argument("--disk", required=True, help="whole disk: disk4 on macOS, /dev/sdb or /dev/mmcblk1 on Linux")
    ap.add_argument("--size", required=True, type=int, help="the disk's exact size in bytes, as you confirmed it")
    ap.add_argument("--label", required=True, help="the name of a volume on the disk now, as you confirmed it")
    ap.add_argument("--systems", default="PS1", help="comma separated Games/ folders to create (default PS1)")
    ap.add_argument("--yes", action="store_true", help="erase the disk and run the plan")
    args = ap.parse_args(argv)
    mac = system() == "Darwin"
    try:
        systems = systems_of(args.systems)
        d = mac_disk(args.disk, sh) if mac else linux_disk(args.disk, sh)
        why = refusal(d, args.size, args.label)
        if why:
            raise Refuse(f"refusing {args.disk}: {why}")
    except Refuse as e:
        print(f"expansion-card: {e}", file=sys.stderr)
        return 2
    mnt = "/tmp/slot-expansion"
    plan = mac_plan(args.disk, systems, mnt) if mac else linux_plan(args.disk, systems, mnt, d["mounted"])
    print(f"{args.disk}: {args.size} bytes, volumes {', '.join(d['labels'])}. Everything on it will be erased.")
    for step in plan:
        print("  " + (show(step[:2]) + " <<<\n    " + step[2].replace("\n", "\n    ") if step[0] == "sfdisk" else show(step)))
    print("Config/expansion.txt on the main card:\n" + "".join(f"  {x}\n" for x in systems))
    if not args.yes:
        print("dry run: nothing written. Add --yes to erase the disk.")
        return 0
    os.makedirs(mnt, exist_ok=True)
    erased = False
    for step in plan:
        erased = erased or step[:2] in (["diskutil", "partitionDisk"], ["wipefs", "-a"])
        rc, out = sh(step[:2], step[2]) if step[0] == "sfdisk" else sh(step)
        if rc != 0 and step[:2] != ["diskutil", "unmount"]:
            print(f"expansion-card: {show(step)} failed ({rc}): {out!r:.300}", file=sys.stderr)
            print("expansion-card: " + (AFTER if erased else BEFORE), file=sys.stderr)
            return 1
        print(f"ok: {show(step[:2]) if step[0] == 'sfdisk' else show(step)}")
    if not layout_ok(args.disk, d["block"], sh):
        print("expansion-card: the partition table is not exactly p1 at 1 MiB and p2 at 17 MiB. " + AFTER, file=sys.stderr)
        return 1
    if not p1_is_zero(part(args.disk, 1, raw=True)):
        print("expansion-card: p1 is not all zero, BaseOS could mount it as the main card. " + AFTER, file=sys.stderr)
        return 1
    print(f"done: p1 checked all zero, p2 is exFAT {LABEL} with " + ", ".join(f"Games/{x}" for x in systems))
    return 0


if __name__ == "__main__":
    sys.exit(main())
