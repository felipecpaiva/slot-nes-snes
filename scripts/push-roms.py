#!/usr/bin/env python3
"""Push a ROM library (loose or zipped) and optionally saves and save states to the device over adb.

    python3 scripts/push-roms.py --src ~/ROMS                  # every system
    python3 scripts/push-roms.py --src ~/ROMS --only gba       # one system
    python3 scripts/push-roms.py --src ~/ROMS --dry-run        # count only, touch nothing

--src holds one folder per system: nes, snes, gba, gb, gbc (missing ones are skipped).
ROMs:   zips are read in place and only new games are unzipped; duplicates are found by CRC32 and
        size (zip headers), so nothing is unzipped twice. Loose ROMs are pushed as they are.
Saves:  Name.srm or Name.sav -> Saves/<SYSTEM>/<rom file stem>.sav. Never overwrites a save already
        on the device. The name follows the ROM inside the zip, as slot expects.
States: --states converts RetroArch states (Name.state1, Name.state.auto) to
        States/<SYSTEM>/<core>/<rom stem>/<stamp>.state. A state loads only on the core that made it,
        and many will not load at all, so this is off by default.
adb:    $ADB, else adb on PATH, else `mise exec -- adb` from the repo root.
"""
import argparse
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import zipfile
import zlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEMS = {  # folder -> (device folder, rom extensions, core that loads its states)
    "nes": ("NES", {".nes", ".unf"}, "fceumm"),
    "snes": ("SNES", {".sfc", ".smc", ".swc", ".fig"}, "snes9x"),
    "gba": ("GBA", {".gba"}, "mgba"),
    "gb": ("GB", {".gb", ".gbc"}, "mgba"),
    "gbc": ("GBC", {".gb", ".gbc"}, "mgba"),
}

ap = argparse.ArgumentParser(description="Push ROMs, saves and states to the device over adb.")
ap.add_argument("--src", default=".", help="library folder holding nes/ snes/ gba/ gb/ gbc/ (default: .)")
ap.add_argument("--only", choices=SYSTEMS, help="push one system only")
ap.add_argument("--dry-run", action="store_true", help="count what would be pushed; touch nothing")
ap.add_argument("--sd", default="/mnt/sdcard", help="device content root (default: /mnt/sdcard)")
ap.add_argument("--states", action="store_true", help="also convert and push RetroArch save states")
ap.add_argument("--gba-core", choices=["mgba", "gpsp"], default="mgba",
                help="core the GBA states were made with (default: mgba)")
args = ap.parse_args()
SRC, SD, dry = os.path.abspath(os.path.expanduser(args.src)), args.sd, args.dry_run
SYSTEMS["gba"] = (*SYSTEMS["gba"][:2], args.gba_core)

if os.environ.get("ADB"):
    ADB, ADB_CWD = [os.environ["ADB"]], None
elif shutil.which("adb"):
    ADB, ADB_CWD = ["adb"], None
else:
    ADB, ADB_CWD = ["mise", "exec", "--", "adb"], REPO  # the repo pins adb in mise.toml


def adb(*a, **kw):
    return subprocess.run([*ADB, *a], cwd=ADB_CWD, **kw)


def crc_file(p):
    c = 0
    with open(p, "rb") as f:
        while b := f.read(1 << 20):
            c = zlib.crc32(b, c)
    return c


def put(stage, name, src_fn):
    """Write one file into stage under a free name. Returns the stem it got."""
    dst, n = os.path.join(stage, name), 2
    stem, ext = os.path.splitext(name)
    while os.path.exists(dst):  # same name, different content
        dst = os.path.join(stage, f"{stem} ({n}){ext}")
        n += 1
    src_fn(dst)
    return os.path.splitext(os.path.basename(dst))[0]


def rastate_to_core(p):
    """RetroArch state (maybe RZIP, maybe RASTATE wrapper) -> raw core state."""
    d = open(p, "rb").read()
    if d[:8] == b"#RZIPv\x01#":
        _, total = struct.unpack("<IQ", d[8:20])
        i, out = 20, b""
        while i < len(d):
            (n,) = struct.unpack("<I", d[i:i + 4])
            out += zlib.decompress(d[i + 4:i + 4 + n])
            i += 4 + n
        assert len(out) == total, "bad RZIP size"
        d = out
    if d[:7] == b"RASTATE":
        i = 8
        while i + 8 <= len(d):
            tag, size = d[i:i + 4], struct.unpack("<I", d[i + 4:i + 8])[0]
            if tag == b"MEM ":
                return d[i + 8:i + 8 + size]
            i += 8 + ((size + 7) & ~7)
        raise ValueError("no MEM block")
    return d


def device_names(path):
    if dry:
        return set()
    # a shell glob, not ls: the device's ls colours names even through adb, so they never match
    q = "'" + path.replace("'", "'\\''") + "'"
    r = adb("shell", f'for f in {q}/*; do [ -e "$f" ] && echo "${{f##*/}}"; done; true',
            capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"could not list {path} on the device, refusing to push saves blind")
    return {l.rstrip("\r") for l in r.stdout.splitlines() if l.strip()}


def stage_roms(folder, exts, stage):
    """Stage new ROMs. Returns (alias: file stem -> staged stem, count staged)."""
    d = os.path.join(SRC, folder)
    seen, alias, new, dupes, norom = {}, {}, 0, 0, []
    names = sorted(os.listdir(d))
    # loose ROMs first, so zips holding the same game count as dupes
    for n in names:
        p = os.path.join(d, n)
        stem, ext = os.path.splitext(n)
        if n.startswith("._") or not os.path.isfile(p) or ext.lower() not in exts:
            continue
        key = (crc_file(p), os.path.getsize(p))
        if key in seen:
            dupes += 1
        else:
            seen[key] = put(stage, n, lambda dst: shutil.copyfile(p, dst))
            new += 1
        alias[stem] = seen[key]
    for n in names:
        if n.startswith("._") or not n.lower().endswith(".zip"):
            continue
        try:
            with zipfile.ZipFile(os.path.join(d, n)) as z:
                roms = [i for i in z.infolist() if not i.is_dir()
                        and os.path.splitext(i.filename)[1].lower() in exts
                        and not os.path.basename(i.filename).startswith("._")]
                if not roms:
                    norom.append(n)
                for i in roms:
                    key = (i.CRC, i.file_size)
                    if key in seen:
                        dupes += 1
                    else:
                        def ex(dst, i=i):
                            with z.open(i) as s, open(dst, "wb") as o:
                                shutil.copyfileobj(s, o)
                        seen[key] = put(stage, os.path.basename(i.filename), ex)
                        new += 1
                    alias.setdefault(n[:-4], seen[key])  # first ROM in the zip
        except zipfile.BadZipFile:
            print(f"  BAD ZIP  {folder}/{n}")
    print(f"{folder}: {new} ROMs to push, {dupes} duplicates skipped, {len(norom)} zips with no ROM")
    for n in norom:
        print(f"  no ROM   {folder}/{n}")
    return alias, new


def stage_saves(folder, devdir, alias, stage):
    d = os.path.join(SRC, folder)
    have = device_names(f"{SD}/Saves/{devdir}")
    out, new, skipped, orphans = os.path.join(stage, "Saves"), 0, 0, []
    for n in sorted(os.listdir(d)):
        stem, ext = os.path.splitext(n)
        if n.startswith("._") or ext.lower() not in (".srm", ".sav"):
            continue
        if stem not in alias:
            orphans.append(n)
        target = alias.get(stem, stem) + ".sav"
        if target in have or os.path.exists(os.path.join(out, target)):
            skipped += 1  # already on device (or two files for one game)
            continue
        os.makedirs(out, exist_ok=True)
        shutil.copyfile(os.path.join(d, n), os.path.join(out, target))
        new += 1
    print(f"{folder}: {new} saves to push, {skipped} skipped (already there)")
    for n in orphans:
        print(f"  save has no ROM here: {folder}/{n} (pushed under its own name)")
    return new


STATE_RE = re.compile(r"^(?P<base>.+)\.state(?P<n>\d*|\.auto)$")


def stage_states(folder, devdir, core, alias, stage):
    d = os.path.join(SRC, folder)
    found = [(os.path.getmtime(os.path.join(d, n)), n, m) for n in os.listdir(d)
             if not n.startswith("._") and (m := STATE_RE.match(n))]
    new, used = 0, set()
    for mtime, n, m in sorted(found):
        stem = alias.get(m["base"], m["base"])
        t = int(mtime)
        while (stem, t) in used:  # stamps must be unique per game
            t += 1
        used.add((stem, t))
        stamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(t))
        out = os.path.join(stage, "States", devdir, core, stem)
        try:
            raw = rastate_to_core(os.path.join(d, n))
        except Exception as e:
            print(f"  BAD STATE {folder}/{n}: {e}")
            continue
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, stamp + ".state"), "wb") as f:
            f.write(raw)
        png = os.path.join(d, n + ".png")
        if os.path.exists(png):
            shutil.copyfile(png, os.path.join(out, stamp + ".png"))
        new += 1
    print(f"{folder}: {new} save states to push (as core '{core}')")
    return new


if not os.path.isdir(SRC):
    sys.exit(f"--src not found: {SRC}")
if not dry:
    r = adb("devices", capture_output=True, text=True)
    if not any(l.endswith("\tdevice") for l in r.stdout.splitlines()):
        sys.exit("No device found. Check the USB cable.")

for folder, (devdir, exts, core) in SYSTEMS.items():
    if (args.only and folder != args.only) or not os.path.isdir(os.path.join(SRC, folder)):
        continue
    with tempfile.TemporaryDirectory() as tmp:
        roms = os.path.join(tmp, "roms")
        os.mkdir(roms)
        alias, n_roms = stage_roms(folder, exts, roms)
        n_sav = stage_saves(folder, devdir, alias, tmp)
        n_st = stage_states(folder, devdir, core, alias, tmp) if args.states else 0
        if dry:
            continue
        if n_roms:
            adb("push", roms + "/.", f"{SD}/Games/{devdir}/")
        if n_sav:
            adb("shell", "mkdir", "-p", f"{SD}/Saves/{devdir}")
            adb("push", os.path.join(tmp, "Saves") + "/.", f"{SD}/Saves/{devdir}/")
        if n_st:
            adb("push", os.path.join(tmp, "States", devdir) + "/.", f"{SD}/States/{devdir}/")
