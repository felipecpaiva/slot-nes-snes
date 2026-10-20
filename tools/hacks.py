#!/usr/bin/env python3
"""Check and update the ROM hacks on a slot SD card (and their library copies on the Mac).

    python3 tools/hacks.py --library /Volumes/MuOs/ROMS                      # --check, read only (default)
    python3 tools/hacks.py --device --library ~/ROMS --check                  # only the hacks on the card
    python3 tools/hacks.py --device --library ~/ROMS --update pokemon-unbound --dry-run
    python3 tools/hacks.py --device --library ~/ROMS --update pokemon-unbound
    python3 tools/hacks.py --device --library ~/ROMS --all --dry-run
    python3 tools/hacks.py --device --library ~/ROMS --rollback pokemon-unbound
    python3 tools/hacks.py --device --library ~/ROMS --add castlevania-2-retranslation --dry-run  # a new hack, new file
    python3 tools/hacks.py --device --init                                    # write the user settings file
    python3 tools/hacks.py --library ~/ROMS --fix-library-zips --dry-run      # unzip updated hacks' library copies
    python3 tools/hacks.py --device --migrate-backups --dry-run               # card backups -> the backups folder

Registry: tools/hacks.json (the researched seed) with the user's ~/.config/slot-nes-snes/hacks.json read on
top: an entry with a seed id overrides those fields, a new id adds a hack (it needs system, card, source).
Both are JSON with whole-line // comments (the repo's Python is 3.9, which has no tomllib). What is
installed (version, CRC32, backup) is recorded in ~/.config/slot-nes-snes/hacks-state.json, never in the
settings. Format and fields: docs/HACKS.md.

--check (default) writes nothing to the card, the library or the settings: per hack, the installed version
(state file, else the file name, else unknown) against the latest (GitHub releases API for github:, a
version_regex or a content hash of the page for page:, the link for manual). Page hashes are kept in the
cache dir so a later check can say "page changed".

--update <id>|--all (always try --dry-run first; a real run prints the plan and asks): the patch comes from
the GitHub release asset matching the entry's asset pattern, or from ~/ROMHacks/incoming/<id>/ (the newest
.bps .ips .ups .xdelta .ppf, ROM, or a .zip holding exactly one of them). Nothing downloaded is ever executed. A
patch is applied in pure Python to the clean base ROM found in --library by CRC32 (BPS and UPS check the source,
target and patch CRCs; xdelta checks each window's Adler-32; PPF2/3 their block check and undo data; IPS has none,
so the entry's target_crc32 is checked when known, else a warning). A PS1 disc (.chd) is extracted with chdman,
track 1 checked against base_crc32 (redump) and patched, packed back and checked again (ADR 0089).
Any mismatch refuses. Then, on the card (ADR 0082):
  - refuses while Config/slot.state has the game seated (cart= and cart_platform=): eject it first;
  - Backups/hacks/<SYS>/<stem>/<stamp>_<old version>/ gets the old ROM (moved), the .sav/.srm (copied:
    they stay in place, so the battery save carries on) and every state folder of the game
    (States/<SYS>/<core>/<stem>/: the ring, its thumbnails, resume.state, resume-refused-*; moved, so slot
    can never load an old version's snapshot into the new ROM), mirrored at their card paths, with a
    backup.json listing them;
  - the new ROM is written under the SAME file name, so labels, cart_shell, video_mode, selected_core,
    favourites, recents and the shelf memory stay attached.
  - with the settings file's "backups" (or --backups) set to a folder instead of "card", the backup goes
    to <folder>/<SYS>/<stem>/<stamp>_<old version>/: every file is copied there and checked (size and
    CRC32), and only then are the old ROM and states removed from the card. An unreachable folder refuses
    (never a silent fall back to the card); --backups card keeps one run's backup on the card.
    --migrate-backups moves the card's Backups/hacks/ there the same way.
The library copy gets the same: the old file is moved to ~/ROMHacks/backups/<SYS>/<stem>/<label>/ and the
new ROM is written loose (slot reads no zip): a zip comes back as its member's name, never beside a loose
copy. --fix-library-zips does that for hacks updated while the library copy stayed a zip. The library is the muOS card: its RetroArch
<stem>.state* and .srm files are left alone (a note says old states there may not load). Nothing is
deleted anywhere, except a card copy whose copy in the off-card backups folder has checked.
--rollback <id> moves the current ROM, saves and states into a new backup and copies the newest update
backup back, on the card and in the library.
"""
import argparse
import fnmatch
import hashlib
import importlib.util
import io
import json
import mmap
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
import zipfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("fetch_labels_for_hacks", os.path.join(HERE, "fetch-labels.py"))
fl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fl)
fl.UA = "slot-nes-snes-hacks/1.0 (+https://github.com/felipecpaiva/slot-nes-snes)"  # read by fl.Http.get

SEED = os.path.join(HERE, "hacks.json")
GITHUB = "https://api.github.com/repos/"
PATCH_EXTS = (".bps", ".ips", ".ups", ".xdelta", ".vcdiff", ".ppf")
SOURCE = re.compile(r"github:[\w.-]+/[\w.-]+|page:https?://\S+|manual(:https?://\S+)?|")
FORMATS = {"bps", "ips", "ups", "xdelta", "ppf", "rom", "unknown"}
FIELDS = {"name", "system", "card", "source", "asset", "version_regex", "format", "base_name", "base_crc32",
          "target_crc32", "saves_carry_over", "save_note", "latest_known", "home", "cite", "notes", "status", "library"}
SETTINGS = {"backups"}  # keys of the user file that are tool settings, not hack ids
HOUR = 3600
CHALLENGE = re.compile(r"Anubis|Making sure you're not a bot|cf-chl|Just a moment\.\.\.", re.I)
GITHUB_PAGE = re.compile(r"https://github\.com/([\w.-]+/[\w.-]+)/?")
RELEASES = 10  # how many GitHub releases --check tries when it must identify the installed version


class Refuse(Exception):
    """This hack cannot be updated now; nothing was written."""


class PatchError(Refuse):
    pass


def crc_hex(data):
    return f"{zlib.crc32(data) & 0xffffffff:08X}"


def norm_version(v):
    return re.sub(r"^v(?=\d)", "", (v or "").strip().lower())


def version_in_name(name):
    """The last version number in a file name: 'Sonic 3 Delta v0.1a' -> 0.1a, 'Mother 3 (English v1.3)' -> 1.3."""
    found = re.findall(r"(?<![\w.])(?:v(\d+(?:\.\d+)*[a-z]?)|(\d+(?:\.\d+)+[a-z]?))(?![\w.])",
                       os.path.splitext(name)[0], re.I)
    return "".join(found[-1]) if found else None


def stamp():
    return time.strftime("%Y-%m-%d_%H-%M-%S")  # slot's own state stamp shape, no colon (FAT)


# ---- settings ------------------------------------------------------------------------------------

def read_jsonc(path):
    """JSON with whole-line // comments."""
    text = "\n".join("" if l.lstrip().startswith("//") else l for l in fl.slurp(path, "r").splitlines())
    return json.loads(text) if text.strip() else {}


def load_registry(seed=SEED, user=None, warn=print):
    """{id: entry}: the seed, then the user file on top (override fields of a seed id, or add a new id)."""
    reg = {k: dict(v) for k, v in read_jsonc(seed).items()}
    extra = read_jsonc(user) if user and os.path.isfile(user) else {}
    for hid, fields in extra.items():
        if hid in SETTINGS:
            continue
        if not isinstance(fields, dict):
            warn(f"{user}: {hid} is not an object, ignored")
            continue
        unknown = sorted(set(fields) - FIELDS)
        if unknown:
            warn(f"{user}: {hid}: unknown field(s) {', '.join(unknown)} ignored")
        fields = {k: v for k, v in fields.items() if k in FIELDS}
        if hid in reg:
            reg[hid].update(fields)
        elif {"system", "card", "source"} <= set(fields):
            reg[hid] = fields
        else:
            warn(f"{user}: {hid} is not a seed id and has no system, card and source: ignored")
    out = {}
    for hid, h in reg.items():
        h.setdefault("name", hid)
        h.setdefault("format", "unknown")
        h.setdefault("saves_carry_over", "unknown")
        bad = [f for f, ok in (("system", h.get("system") in fl.SYSTEMS), ("card", bool(h.get("card"))),
                               ("source", isinstance(h.get("source"), str) and SOURCE.fullmatch(h["source"])),
                               ("format", h["format"] in FORMATS),
                               ("saves_carry_over", h["saves_carry_over"] in ("yes", "no", "unknown"))) if not ok]
        if bad:
            warn(f"hack {hid}: bad {', '.join(bad)}, skipped")
            continue
        out[hid] = h
    return out


def read_state(path):
    try:
        return json.loads(fl.slurp(path, "r"))
    except (OSError, ValueError):
        return {}


def write_state(path, state):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fl.spit(path + ".tmp", json.dumps(state, indent=2, sort_keys=True) + "\n", "w")
    os.replace(path + ".tmp", path)


# ---- patches (pure Python) -----------------------------------------------------------------------

def _num(p, i):
    """byuu's variable-length number (BPS and UPS)."""
    data, shift = 0, 1
    while True:
        x = p[i]
        i += 1
        data += (x & 0x7f) * shift
        if x & 0x80:
            return data, i
        shift <<= 7
        data += shift


def _footer(p, magic, src):
    if p[:4] != magic or len(p) < 16:
        raise PatchError(f"not a {magic[:3].decode()} patch")
    s_crc, t_crc, p_crc = (int.from_bytes(p[o:o + 4], "little") for o in range(len(p) - 12, len(p), 4))
    if zlib.crc32(p[:-4]) & 0xffffffff != p_crc:
        raise PatchError("the patch file is corrupt (patch CRC mismatch)")
    if zlib.crc32(src) & 0xffffffff != s_crc:
        raise PatchError(f"source CRC mismatch: the base ROM is {crc_hex(src)}, the patch wants {s_crc:08X}")
    return t_crc


def apply_bps(src, p):
    t_crc = _footer(p, b"BPS1", src)
    try:
        ss, i = _num(p, 4)
        ts, i = _num(p, i)
        ms, i = _num(p, i)
        i += ms
        if ss != len(src):
            raise PatchError(f"source size mismatch: {len(src)}, the patch wants {ss}")
        out, o, sr, tr, end = bytearray(ts), 0, 0, 0, len(p) - 12
        while i < end:
            d, i = _num(p, i)
            cmd, n = d & 3, (d >> 2) + 1
            if o + n > ts:
                raise PatchError("the patch writes past the target size")
            if cmd == 0:
                chunk = src[o:o + n]
            elif cmd == 1:
                chunk, i = p[i:i + n], i + n
            else:
                d, i = _num(p, i)
                off = -(d >> 1) if d & 1 else d >> 1
                if cmd == 2:
                    sr += off
                    chunk, sr = src[sr:sr + n] if sr >= 0 else b"", sr + n
                else:
                    tr += off
                    if tr < 0 or tr >= o:
                        raise PatchError("bad target copy")
                    for _ in range(n):  # may overlap the bytes it writes: byte by byte
                        out[o] = out[tr]
                        o, tr = o + 1, tr + 1
                    continue
            if len(chunk) != n:
                raise PatchError("the patch reads past its input")
            out[o:o + n] = chunk
            o += n
    except IndexError:
        raise PatchError("the patch is truncated") from None
    if o != ts:
        raise PatchError("the patch ends before the target is complete")
    if zlib.crc32(out) & 0xffffffff != t_crc:
        raise PatchError(f"target CRC mismatch: got {crc_hex(out)}, the patch wants {t_crc:08X}")
    return bytes(out)


def apply_ups(src, p):
    t_crc = _footer(p, b"UPS1", src)
    try:
        ss, i = _num(p, 4)
        ts, i = _num(p, i)
        if ss != len(src):
            raise PatchError(f"source size mismatch: {len(src)}, the patch wants {ss}")
        out, o, end = bytearray(src[:ts]) + bytes(max(0, ts - len(src))), 0, len(p) - 12
        while i < end:
            skip, i = _num(p, i)
            o += skip
            while True:
                x = p[i]
                i += 1
                if o < ts:
                    out[o] = (src[o] if o < len(src) else 0) ^ x
                o += 1
                if not x:
                    break
    except IndexError:
        raise PatchError("the patch is truncated") from None
    if zlib.crc32(out) & 0xffffffff != t_crc:
        raise PatchError(f"target CRC mismatch: got {crc_hex(out)}, the patch wants {t_crc:08X}")
    return bytes(out)


def apply_ips(src, p):
    if p[:5] != b"PATCH":
        raise PatchError("not an IPS patch")
    out, i = bytearray(src), 5
    try:
        while p[i:i + 3] != b"EOF":
            off, size = int.from_bytes(p[i:i + 3], "big"), int.from_bytes(p[i + 3:i + 5], "big")
            i += 5
            if size:
                data, i = p[i:i + size], i + size
            else:  # RLE record
                data, i = p[i + 2:i + 3] * int.from_bytes(p[i:i + 2], "big"), i + 3
            if len(data) != (size or len(data)) or i > len(p):
                raise IndexError
            if len(out) < off + len(data):
                out.extend(bytes(off + len(data) - len(out)))
            out[off:off + len(data)] = data
        i += 3
    except IndexError:
        raise PatchError("the IPS patch is truncated (no EOF)") from None
    if len(p) - i == 3:  # the optional truncate extension
        del out[int.from_bytes(p[i:i + 3], "big"):]
    return bytes(out)


def _code_table():
    """RFC 3284 section 5.6, the default instruction code table: (type, size, mode) pairs per byte.
    Types: 0 NOOP, 1 ADD, 2 RUN, 3 COPY."""
    t = [((2, 0, 0), (0, 0, 0))] + [((1, n, 0), (0, 0, 0)) for n in range(18)]
    for m in range(9):
        t += [((3, n, m), (0, 0, 0)) for n in [0] + list(range(4, 19))]
    for m in range(6):
        t += [((1, a, 0), (3, c, m)) for a in range(1, 5) for c in range(4, 7)]
    for m in range(6, 9):
        t += [((1, a, 0), (3, 4, m)) for a in range(1, 5)]
    t += [((3, 4, m), (1, 1, 0)) for m in range(9)]
    return t


CODE_TABLE = _code_table()


def _vint(p, i):
    """VCDIFF integer: big-endian base 128, the high bit set on every byte but the last."""
    n = 0
    while True:
        b = p[i]
        i += 1
        n = n << 7 | b & 0x7f
        if not b & 0x80:
            return n, i


def apply_vcdiff(src, p):
    """xdelta3 / VCDIFF (RFC 3284) with the default code table and no secondary compression, which is
    what Delta Patcher and xdelta3 write by default; xdelta's per-window Adler-32 is checked."""
    try:
        ind, i = p[4], 5
        if ind & 3:
            raise PatchError("xdelta patch uses secondary compression or a custom code table: not supported here")
        if ind & 4:
            n, i = _vint(p, i)
            i += n
        out = bytearray()
        while i < len(p):
            win, i = p[i], i + 1
            seg = b""
            if win & 3:
                size, i = _vint(p, i)
                pos, i = _vint(p, i)
                seg = (src if win & 1 else out)[pos:pos + size]
                if len(seg) != size:
                    raise PatchError("xdelta window reads past its source")
            _, i = _vint(p, i)
            tlen, i = _vint(p, i)
            if p[i]:
                raise PatchError("xdelta window is compressed: not supported here")
            dlen, i = _vint(p, i + 1)
            ilen, i = _vint(p, i)
            alen, i = _vint(p, i)
            adler = None
            if win & 4:
                adler, i = int.from_bytes(p[i:i + 4], "big"), i + 4
            data, inst, addr = p[i:i + dlen], p[i + dlen:i + dlen + ilen], p[i + dlen + ilen:i + dlen + ilen + alen]
            i += dlen + ilen + alen
            t, di, ii, ai, near, nxt, same = bytearray(), 0, 0, 0, [0] * 4, 0, [0] * 768
            while ii < len(inst):
                code, ii = inst[ii], ii + 1
                for typ, size, mode in CODE_TABLE[code]:
                    if not typ:
                        continue
                    if not size:
                        size, ii = _vint(inst, ii)
                    if typ == 1:
                        t += data[di:di + size]
                        di += size
                    elif typ == 2:
                        t += data[di:di + 1] * size
                        di += 1
                    else:
                        here = len(seg) + len(t)
                        if mode == 0:
                            a, ai = _vint(addr, ai)
                        elif mode == 1:
                            a, ai = _vint(addr, ai)
                            a = here - a
                        elif mode < 6:
                            a, ai = _vint(addr, ai)
                            a += near[mode - 2]
                        else:
                            a, ai = same[(mode - 6) * 256 + addr[ai]], ai + 1
                        near[nxt], nxt, same[a % 768] = a, (nxt + 1) % 4, a
                        if a + size <= len(seg):
                            t += seg[a:a + size]
                        elif a >= len(seg) and a - len(seg) + size <= len(t):
                            t += t[a - len(seg):a - len(seg) + size]
                        else:
                            for k in range(a, a + size):  # overlaps the bytes it writes: one at a time
                                t.append(seg[k] if k < len(seg) else t[k - len(seg)])
            if len(t) != tlen:
                raise PatchError("xdelta window has the wrong length")
            if adler is not None and zlib.adler32(bytes(t)) & 0xffffffff != adler:
                raise PatchError("xdelta window checksum mismatch: wrong base ROM or a corrupt patch")
            out += t
    except IndexError:
        raise PatchError("the xdelta patch is truncated") from None
    return bytes(out)


def apply_ppf(buf, p):
    """PPF 1.0, 2.0 and 3.0 (PPF-O-Matic's formats) applied in place to buf (a bytearray, or an mmap of a disc
    track: an image never grows). PPF2, and PPF3 with its block check, compare 1024 bytes of the image; PPF3
    undo data is the original bytes, compared too. Every check runs before the first write."""
    ver = p[3:5]
    if p[:3] != b"PPF" or ver not in (b"10", b"20", b"30"):
        raise PatchError("not a PPF patch")
    end = p.rfind(b"@BEGIN_FILE_ID.DIZ")  # PPF2/3 may end with a text block
    end, i, wide, undo, block, at = len(p) if end < 56 else end, 56, 4, False, None, 0x9320
    if ver == b"20":
        if int.from_bytes(p[56:60], "little") != len(buf):
            raise PatchError(f"image size mismatch: {len(buf)}, the patch wants {int.from_bytes(p[56:60], 'little')}")
        block, i = p[60:1084], 1084
    elif ver == b"30":
        wide, undo, i = 8, bool(p[58]), 60
        if p[57]:
            block, at, i = p[60:1084], 0x80A0 if p[56] else 0x9320, 1084
    if block is not None and bytes(buf[at:at + 1024]) != block:
        raise PatchError("PPF block check mismatch: not the image this patch was made for")
    recs = []
    try:
        while i < end:
            off, n = int.from_bytes(p[i:i + wide], "little"), p[i + wide]
            data, i = p[i + wide + 1:i + wide + 1 + n], i + wide + 1 + n
            if undo:
                old, i = p[i:i + n], i + n
                if bytes(buf[off:off + n]) != old:
                    raise PatchError(f"PPF undo data mismatch at {off:#x}: not the image this patch was made for")
            if len(data) != n or i > end:
                raise IndexError
            if off + n > len(buf):
                raise PatchError(f"the PPF writes past the end of the image ({off + n} > {len(buf)})")
            recs.append((off, data))
    except IndexError:
        raise PatchError("the PPF patch is truncated") from None
    for off, data in recs:
        buf[off:off + len(data)] = data
    return block is not None or undo


def apply_patch(src, p, target_crc=None, warn=print):
    """The patched ROM, or PatchError. The format is read from the patch's magic, not trusted from the name."""
    if p[:4] == b"BPS1":
        out = apply_bps(src, p)
    elif p[:4] == b"UPS1":
        out = apply_ups(src, p)
    elif p[:5] == b"PATCH":
        out = apply_ips(src, p)
        if not target_crc:
            warn("  warning: IPS has no checksums and the registry knows no target_crc32; the result is unverified")
    elif p[:4] == b"\xd6\xc3\xc4\x00":
        out = apply_vcdiff(src, p)
        if not target_crc:
            warn("  note: xdelta checks each window (Adler-32) but not the base; the base was found by CRC")
    elif p[:3] == b"PPF":
        out = bytearray(src)
        if not apply_ppf(out, p) and not target_crc:
            warn("  note: this PPF carries no block check or undo data; the base was found by CRC")
        out = bytes(out)
    else:
        raise PatchError("unknown patch format")
    if target_crc and crc_hex(out) != target_crc.upper():
        raise PatchError(f"target CRC mismatch: got {crc_hex(out)}, the registry wants {target_crc.upper()}")
    return out


# ---- the card (mounted or over adb) and the library ----------------------------------------------

class LocalCard:
    """A mounted card or a temp dir. An absolute path is taken as is (the library and its Mac backups)."""

    def __init__(self, root, expansion=None):
        self.root, self.expansion, self.moved = root, expansion, fl.expansion_systems(root)

    def p(self, rel):
        if os.path.isabs(rel):
            return rel
        parts = rel.split("/")
        if parts[0] == "Games" and len(parts) > 1 and parts[1] in self.moved:
            if not self.expansion:
                raise Refuse(f"Games/{parts[1]} is on the Expansion Card (Config/expansion.txt): "
                             f"pass --expansion <its mounted root>, or use --device")
            return os.path.join(self.expansion, *parts)
        return os.path.join(self.root, *parts)

    def exists(self, rel):
        return os.path.exists(self.p(rel))

    def isdir(self, rel):
        return os.path.isdir(self.p(rel))

    def names(self, rel):
        return sorted(n for n in os.listdir(self.p(rel)) if not n.startswith("._")) if self.isdir(rel) else []

    def read(self, rel):
        try:
            return fl.slurp(self.p(rel))
        except OSError:
            return None

    def sizes(self, rel):
        """{name: size} of the files (not folders) in rel."""
        return {n: os.path.getsize(os.path.join(self.p(rel), n)) for n in self.names(rel)
                if os.path.isfile(os.path.join(self.p(rel), n))}

    def crc_size(self, rel):
        return fl.file_crc(self.p(rel)), os.path.getsize(self.p(rel))

    def remove(self, rel):
        (shutil.rmtree if os.path.isdir(self.p(rel)) else os.remove)(self.p(rel))

    def mkdir(self, rel):
        os.makedirs(self.p(rel))

    def apply(self, op, src, dst):
        d = self.p(dst)
        if os.path.exists(d):
            raise Refuse(f"{dst} already exists, refusing to overwrite it")
        os.makedirs(os.path.dirname(d), exist_ok=True)
        if op == "write":
            fl.spit(d + ".tmp", src)
            os.replace(d + ".tmp", d)
        elif op == "copy":
            (shutil.copytree if os.path.isdir(self.p(src)) else shutil.copy2)(self.p(src), d)
        else:
            shutil.move(self.p(src), d)  # a rename, or copy then remove across filesystems (SD card -> Mac)


class AdbCard:
    """The card inside the device. Every path is shell-quoted: stems hold ', &, # and spaces."""

    def __init__(self, run, sd):
        self.run, self.sd, self.dev = run, sd, fl.Device(run, sd)

    def p(self, rel):
        return f"{self.sd}/{rel}"

    def test(self, flag, rel):
        rc, out = self.run("shell", f"[ {flag} {shlex.quote(self.p(rel))} ] && echo yes; true")
        return out.strip() == "yes"

    def exists(self, rel):
        return self.test("-e", rel)

    def isdir(self, rel):
        return self.test("-d", rel)

    def names(self, rel):
        return self.dev.names(self.p(rel))

    def sizes(self, rel):
        rc, out = self.run("shell", f'for f in {shlex.quote(self.p(rel))}/*; do [ -f "$f" ] && '
                                    f'echo "$(ls -ln "$f" | awk \'{{print $5}}\') ${{f##*/}}"; done; true')
        rows = [l.rstrip("\r").lstrip().split(" ", 1) for l in out.splitlines()]
        return {r[1]: int(r[0]) for r in rows if len(r) == 2 and r[0].isdigit()}

    def read(self, rel):
        with tempfile.TemporaryDirectory() as d:
            local = os.path.join(d, "f")
            rc, _ = self.run("pull", self.p(rel), local)
            return fl.slurp(local) if rc == 0 and os.path.isfile(local) else None

    def crc_size(self, rel):
        data = self.read(rel)
        return (crc_hex(data), len(data)) if data is not None else None

    def remove(self, rel):
        self.sh(f"rm -r {shlex.quote(self.p(rel))}")

    def mkdir(self, rel):
        self.sh(f"mkdir -p {shlex.quote(self.p(rel))}")

    def sh(self, cmd):
        rc, out = self.run("shell", cmd)
        if rc != 0:
            raise Refuse(f"device command failed ({rc}): {out.strip()[-200:]}")

    def apply(self, op, src, dst):
        d = shlex.quote(self.p(dst))
        head = f"[ -e {d} ] && exit 3; mkdir -p {shlex.quote(os.path.dirname(self.p(dst)))} && "
        if op == "write":
            self.sh(head + "true")  # refuse an existing target before pushing anything
            with tempfile.TemporaryDirectory() as t:
                local = os.path.join(t, "f")
                fl.spit(local, src)
                rc, out = self.run("push", local, self.p(dst) + ".tmp")
                if rc != 0:
                    raise Refuse(f"adb push failed: {out.strip()[-200:]}")
            self.sh(head + f"mv {shlex.quote(self.p(dst) + '.tmp')} {d}")
        else:
            self.sh(head + f"{'cp -r' if op == 'copy' else 'mv'} {shlex.quote(self.p(src))} {d}")


def tree(side, rel):
    """{sub path: size} of every file under rel ('' when rel is a file), through names and sizes only."""
    if not side.isdir(rel):
        size = side.sizes(os.path.dirname(rel)).get(os.path.basename(rel))
        if size is None:
            raise Refuse(f"{rel} is not there")
        return {"": size}
    out, sizes = {}, side.sizes(rel)
    for n in side.names(rel):
        if n in sizes:
            out[n] = sizes[n]
        else:
            out.update({f"{n}/{k}" if k else n: v for k, v in tree(side, f"{rel}/{n}").items()})
    return out


def under(rel, sub):
    return f"{rel}/{sub}" if sub else rel


class Split:
    """The card plus the Mac, for backups kept off the card: a card path is relative, a Mac path absolute.
    A copy between the two goes file by file and checks each copy's size and CRC32 against the bytes it
    read; a move between them is a copy, then a separate remove op once every copy has checked (ADR 0082)."""

    def __init__(self, card):
        self.card, self.mac = card, LocalCard("/")

    def side(self, rel):
        return self.mac if os.path.isabs(rel) else self.card

    def exists(self, rel):
        return self.side(rel).exists(rel)

    def isdir(self, rel):
        return self.side(rel).isdir(rel)

    def names(self, rel):
        return self.side(rel).names(rel)

    def read(self, rel):
        return self.side(rel).read(rel)

    def sizes(self, rel):
        return self.side(rel).sizes(rel)

    def apply(self, op, src, dst):
        if op == "remove":
            return self.side(src).remove(src)
        to = self.side(dst)
        if op == "write" or self.side(src) is to:
            return to.apply(op, src, dst)
        if op != "copy":
            raise Refuse(f"{op} between the card and the Mac: copy, check, then remove")
        frm = self.side(src)
        if to.exists(dst):
            raise Refuse(f"{dst} already exists, refusing to overwrite it")
        files = tree(frm, src)
        if not files:  # an empty folder (a state folder with no states yet)
            to.mkdir(dst)
        for sub in files:
            s, d = under(src, sub), under(dst, sub)
            data = frm.read(s)
            if data is None:
                raise Refuse(f"could not read {s}")
            to.apply("write", data, d)
            if to.crc_size(d) != (crc_hex(data), len(data)):
                raise Refuse(f"the copy {d} does not match {s} (size or CRC32): nothing removed")


def same_files(a, ra, b, rb):
    """True when rb holds exactly ra's files, each of the same size and CRC32."""
    files = tree(a, ra)
    return b.exists(rb) and tree(b, rb) == files and all(
        a.crc_size(under(ra, f)) == b.crc_size(under(rb, f)) for f in files)


def reach(root, dry):
    """Refuse unless the off-card backup root can be written. A dry run only looks (nothing is created)."""
    try:
        if dry:
            a = root
            while not os.path.exists(a):
                a = os.path.dirname(a)
            ok = os.path.isdir(a) and os.access(a, os.W_OK)
        else:
            # ponytail: an unmounted Linux mount point is a plain folder and passes; /Volumes refuses it
            os.makedirs(root, exist_ok=True)
            tempfile.TemporaryFile(dir=root).close()
            ok = True
    except OSError:
        ok = False
    if not ok:
        raise Refuse(f"the backup location {root} is not reachable (not mounted, or not writable): mount it, "
                     "or rerun with --backups card to keep this run's backup on the card")


def stem_dir(root, system, stem):
    """<root>/<SYS>/<stem>, as an existing folder spells the stem (NFC or NFD) when there is one."""
    folder = os.path.join(root, system)
    names = os.listdir(folder) if os.path.isdir(folder) else []
    return os.path.join(folder, next((n for n in names if fl.nfc(n) == fl.nfc(stem)), stem))


def seated(card, system, stem):
    """slot keeps the game in the slot in Config/slot.state: cart=<stem>, cart_platform=<system lowercase>."""
    raw = card.read("Config/slot.state")
    if raw is None and card.exists("Config/slot.state"):
        raise Refuse("Config/slot.state exists but could not be read: cannot tell whether the game is seated")
    text = (raw or b"").decode("utf-8", "replace")
    kv = dict(l.split("=", 1) for l in text.splitlines() if "=" in l)
    return kv.get("cart") == stem and kv.get("cart_platform", "").lower() in ("", system.lower())


def card_items(card, system, stem, rom):
    """[(card path, how)] of one game: the ROM and its state folders move, the battery saves are copied."""
    items = [(f"Games/{system}/{rom}", "move")]
    items += [(f"Saves/{system}/{stem}{e}", "copy") for e in (".sav", ".srm", ".disc", ".flash")
              if card.exists(f"Saves/{system}/{stem}{e}")]
    items += [(f"States/{system}/{core}/{stem}", "move") for core in card.names(f"States/{system}")
              if card.isdir(f"States/{system}/{core}/{stem}")]
    return items


def library_items(lib, system, stem):
    """[(path, "move", zip member or None)]: the library copies of stem, loose or zipped. Only the ROM: the
    library is the muOS card, and its RetroArch saves and states are its own (ADR 0082)."""
    folder, exts = os.path.join(lib, fl.SYSTEMS[system][0]), fl.SYSTEMS[system][1]
    out, key = [], fl.nfc(stem)
    for n in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        p, (base, ext) = os.path.join(folder, n), os.path.splitext(n)
        if n.startswith("._") or not os.path.isfile(p):
            continue
        if ext.lower() in exts and fl.nfc(base) == key:
            out.append((p, "move", None))
        elif ext.lower() == ".zip":
            try:
                with zipfile.ZipFile(p) as z:
                    m = next((i.filename for i in z.infolist()
                              if fl.nfc(os.path.splitext(os.path.basename(i.filename))[0]) == key
                              and os.path.splitext(i.filename)[1].lower() in exts), None)
            except zipfile.BadZipFile:
                m = None
            if m:
                out.append((p, "move", m))
    return out


def card_target(card, h, missing_ok=False):
    """The one card file this hack updates: its `card` name, compared in NFC. None on the card, or two
    spellings of it, refuse: never a guess."""
    names = [n for n in card.names(f"Games/{h['system']}") if fl.nfc(n) == fl.nfc(h["card"])]
    if not names and missing_ok:
        return h["card"]
    if not names:
        raise Refuse(f"Games/{h['system']}/{h['card']} is not on the card")
    if len(names) > 1:
        raise Refuse(f"ambiguous: {', '.join(names)} on the card: set `card` in your settings file")
    return names[0]


def library_target(lib, h):
    """(path, zip member or None) of the one library copy this hack updates, or None when there is none:
    the entry's `library` file name if set, else the copies of the card stem. Several: refuse."""
    system = h["system"]
    if h.get("library"):
        folder, exts = os.path.join(lib, fl.SYSTEMS[system][0]), fl.SYSTEMS[system][1]
        hits = [n for n in (os.listdir(folder) if os.path.isdir(folder) else []) if fl.nfc(n) == fl.nfc(h["library"])]
        if not hits:
            return None
        p = os.path.join(folder, hits[0])
        if not p.lower().endswith(".zip"):
            return p, None
        with zipfile.ZipFile(p) as z:
            roms = [i.filename for i in z.infolist() if os.path.splitext(i.filename)[1].lower() in exts
                    and not os.path.basename(i.filename).startswith("._") and not i.filename.startswith("__MACOSX/")]
        if len(roms) != 1:
            raise Refuse(f"{hits[0]} holds {len(roms)} ROMs, want exactly one")
        return p, roms[0]
    items = library_items(lib, system, os.path.splitext(h["card"])[0])
    if len(items) > 1:
        raise Refuse(f"ambiguous: {', '.join(os.path.basename(p) for p, _, _ in items)} in the library: "
                     "set `library` in your settings file")
    return (items[0][0], items[0][2]) if items else None


def target_crc(lib_target):
    p, m = lib_target
    if m:
        with zipfile.ZipFile(p) as z:
            return f"{z.getinfo(m).CRC:08X}"
    return fl.file_crc(p)


VERSION_WORDS = re.compile(r"\bv(?:ersion)?\s*\d+(?:\.\d+)*[a-z]?\b|\bversion\b|\bb\d+(?:\.\d+)+\b", re.I)


def dup_key(name, system):
    """A name without its version numbers, for spotting two versions of one hack side by side."""
    return fl.title_key(VERSION_WORDS.sub(" ", os.path.splitext(name)[0]), system)


def duplicates(reg, listing):
    """[(system, hack file, other file)] for files that look like another version of a registry hack."""
    out = []
    for h in reg.values():
        names = listing.get(h["system"], set())
        key = dup_key(h["card"], h["system"])
        stem, exts = fl.nfc(os.path.splitext(h["card"])[0]), tuple(fl.SYSTEMS[h["system"]][1]) + (".zip",)
        out += [(h["system"], h["card"], n) for n in sorted(names)
                if key and n.lower().endswith(exts) and fl.nfc(os.path.splitext(n)[0]) != stem
                and dup_key(n, h["system"]) == key]
    return out


def library_states(lib, system, stem):
    folder, key = os.path.join(lib, fl.SYSTEMS[system][0]), fl.nfc(stem)
    return [n for n in (os.listdir(folder) if os.path.isdir(folder) else []) if fl.nfc(n).startswith(key + ".state")]


def find_base(lib, system, crc):
    """(bytes, where) of the ROM in the library whose whole-file CRC32 is crc: zip headers first (free),
    then loose files. ponytail: whole file only; a headered NES/SNES base would need a header strip."""
    folder, exts = os.path.join(lib, fl.SYSTEMS[system][0]), fl.SYSTEMS[system][1]
    names = sorted(os.listdir(folder)) if os.path.isdir(folder) else []
    for n in names:
        if n.lower().endswith(".zip") and not n.startswith("._"):
            try:
                with zipfile.ZipFile(os.path.join(folder, n)) as z:
                    for i in z.infolist():
                        if os.path.splitext(i.filename)[1].lower() in exts and f"{i.CRC:08X}" == crc:
                            return z.read(i), f"{n}:{i.filename}"
            except zipfile.BadZipFile:
                continue
    for n in names:
        p = os.path.join(folder, n)
        if os.path.splitext(n)[1].lower() in exts and not n.startswith("._") and fl.file_crc(p) == crc:
            return fl.slurp(p), n
    return None, None


# ---- PS1 discs: .chd <-> bin/cue with chdman (ADR 0089) ----------------------------------------------

def chdman(*args):
    """stdout of one chdman run (MAME's tool: brew install rom-tools); Refuse when it is missing or fails."""
    exe = shutil.which("chdman")
    if not exe:
        raise Refuse("chdman not found: brew install rom-tools (PS1 discs are .chd)")
    r = subprocess.run([exe, *args], capture_output=True, text=True)
    if r.returncode:
        raise Refuse(f"chdman {args[0]} failed: {(r.stderr or r.stdout).strip()[-300:]}")
    return r.stdout


def extract_disc(chd, folder):
    """[track bin paths] of chd written as one bin per track plus disc.cue in folder."""
    os.makedirs(folder)
    cue = os.path.join(folder, "disc.cue")
    chdman("extractcd", "-i", chd, "-o", cue, "-sb")
    return [os.path.join(folder, n) for n in re.findall(r'^\s*FILE\s+"([^"]+)"', fl.slurp(cue, "r"), re.M)]


def disc_tracks(chd):
    """The CHT2 track lines of `chdman info`: type, frames and pregap of every track."""
    return [l.strip() for l in chdman("info", "-i", chd).splitlines() if "TRACK:" in l]


def disc_base(library, h):
    """The clean base disc: <base_name>.chd in the library's psx folder (by name: CRCing every disc in the
    folder would read a hundred GB). Its track 1 CRC is checked when it is built."""
    folder = os.path.join(library, fl.SYSTEMS[h["system"]][0])
    want = fl.nfc((h.get("base_name") or "") + ".chd")
    hits = [n for n in (os.listdir(folder) if os.path.isdir(folder) else []) if fl.nfc(n) == want]
    if not h.get("base_name") or not hits:
        raise Refuse(f"no base disc {want} in {folder} (PS1 entries name their base: base_name)")
    return os.path.join(folder, hits[0])


def build_disc(h, base, patch, say=print):
    """(chd bytes, patched track 1 CRC32): base extracted to bin/cue in a temp dir, track 1 checked against
    the registry's base_crc32 (the redump track CRC), patched, packed with createcd, then extracted again:
    track 1 must be the patched CRC and every other track and the track layout must be unchanged."""
    want = (h.get("base_crc32") or "").upper()
    if not want:
        raise Refuse("a PS1 entry needs base_crc32: the redump CRC32 of track 1")
    with tempfile.TemporaryDirectory(prefix="slot-hacks-") as t:
        bins = extract_disc(base, os.path.join(t, "in"))
        crcs = [fl.file_crc(b) for b in bins]
        if crcs[0] != want:
            raise Refuse(f"track 1 of {os.path.basename(base)} is {crcs[0]}, the patch wants {want}")
        if patch[:3] == b"PPF":  # in place: a track is hundreds of MB
            with open(bins[0], "r+b") as f, mmap.mmap(f.fileno(), 0) as m:
                apply_ppf(m, patch)
        else:
            fl.spit(bins[0], apply_patch(fl.slurp(bins[0]), patch, warn=say))
        new = fl.file_crc(bins[0])
        if h.get("target_crc32") and new != h["target_crc32"].upper():
            raise Refuse(f"patched track 1 is {new}, the registry wants {h['target_crc32'].upper()}")
        out = os.path.join(t, "new.chd")
        # the codecs every PS1 .chd here uses (and slot reads); pinned so a chdman upgrade cannot switch them
        chdman("createcd", "-i", os.path.join(t, "in", "disc.cue"), "-o", out, "-c", "cdlz,cdzl,cdfl")
        back = [fl.file_crc(b) for b in extract_disc(out, os.path.join(t, "back"))]
        if back != [new] + crcs[1:] or disc_tracks(out) != disc_tracks(base):
            raise Refuse(f"the packed disc does not extract to the patched tracks ({back} != {[new] + crcs[1:]})")
        say(f"  disc: {len(bins)} track(s), track 1 {want} -> {new}, other tracks unchanged, round trip checked")
        return fl.slurp(out), new


def library_ops(ctx, lib, system, stem, label, new, meta):
    """(ops, backup dir, library name) for one library copy: the old file moved to the Mac backup, the new
    ROM written loose. slot reads no zip, so a zipped copy comes back as the loose ROM under its member's
    name, and a zip and a loose copy of one hack never sit side by side (the one-file rule)."""
    path, member = lib
    folder = os.path.dirname(path)
    name = os.path.basename(member) if member else os.path.basename(path)
    if member and any(fl.nfc(n) == fl.nfc(name) for n in os.listdir(folder)):
        raise Refuse(f"{name} already sits next to {os.path.basename(path)} in the library: keep one copy, "
                     "set `library` to it")
    ldir = free_dir(LocalCard(folder), os.path.join(ctx.home, "backups", system, stem), label)
    return update_ops([(path, "move")], ldir, lib_map(ldir), [(new, os.path.join(folder, name))], meta), ldir, name


def zip_stem_note(path):
    """muOS keys RetroArch's .srm and .state* by the file stem: unzipping renames the stem."""
    stem = fl.nfc(os.path.splitext(os.path.basename(path))[0])
    left = [n for n in os.listdir(os.path.dirname(path))
            if fl.nfc(n).startswith(stem + ".state") or fl.nfc(n) == stem + ".srm"]
    if left:
        print(f"  note: muOS files keyed to the zip's name stop attaching to the loose ROM: {', '.join(sorted(left))}")


# ---- plans -----------------------------------------------------------------------------------------

def free_dir(target, base, label):
    d, n = f"{base}/{label}", 2
    while target.exists(d):
        d, n = f"{base}/{label}-{n}", n + 1
    return d


def card_map(bdir):
    return lambda live: f"{bdir}/{live}"


def lib_map(bdir):
    return lambda live: f"{bdir}/{os.path.basename(live)}"


def update_ops(items, bdir, to_backup, writes, meta):
    """Ops for one target: backup.json first, then the saves copied, the states and the ROM moved, the new
    ROM written last under the same name."""
    pairs = [(live, to_backup(live)) for live, _ in items]
    info = [("write", json.dumps(dict(meta, items=pairs), indent=2).encode(), f"{bdir}/backup.json")]
    ops, removes = [], []
    for live, how in sorted(items, key=lambda x: x[1] != "copy"):
        across = os.path.isabs(live) != os.path.isabs(bdir)  # card -> off-card backup: copy, check, remove
        ops.append(("copy" if across else how, live, to_backup(live)))
        if across and how == "move":
            removes.append(("remove", live, None))
    # off the card, backup.json comes after the checked copies: a backup that failed half way has none,
    # so --rollback never picks it; on the card it comes first, so a half-done move can be rolled back
    ops = ops + info if removes else info + ops
    return ops + removes + [("write", data, live) for data, live in writes]


def rollback_ops(target, current, bases, safety, to_backup_of, meta):
    """Move what is there now into a new backup under safety, then copy the newest update backup found
    under any of bases back. The saved paths are derived from where the backup is now (backup.json keeps
    the paths of the day it was written; a migrated backup has moved)."""
    backups = []
    for base in dict.fromkeys(bases):
        for n in target.names(base):
            info = target.read(f"{base}/{n}/backup.json")
            try:
                info = json.loads(info) if info else None
            except ValueError:
                info = None
            if info and info.get("kind") == "update":
                backups.append((n, f"{base}/{n}", info))
    if not backups:
        raise Refuse("no update backup to roll back to")
    name, found, info = max(backups, key=lambda b: b[0])
    sdir = free_dir(target, safety, f"{stamp()}_rollback")
    ops = update_ops([(live, "move") for live, _ in current], sdir, to_backup_of(sdir), [], meta)
    return ops + [("copy", to_backup_of(found)(live), live) for live, _ in info["items"]], info


def show(ops, where):
    for op, a, b in ops:
        src = f"{len(a)} bytes" if isinstance(a, bytes) else a
        print(f"    {where}: {op:<5} {src}" + (f"  ->  {b}" if b else ""))


def execute(target, ops, where, done=None):
    """True when every op ran; else says which did and returns False. done, a list, gets each op that ran."""
    for n, (op, a, b) in enumerate(ops):
        try:
            target.apply(op, a, b)
            if done is not None:
                done.append(op)
        except (Refuse, OSError) as e:
            print(f"  {where}: FAILED at op {n + 1} of {len(ops)} ({op} -> {b or a}): {e}")
            print(f"  {where}: the {n} op(s) before it were done; nothing that was not copied and checked was removed")
            return False
    return True


# ---- sources ----------------------------------------------------------------------------------------

class Ctx:
    def __init__(self, http=None, env=None, sleep=time.sleep, adb=None):
        env = os.environ if env is None else env
        self.http, self.sleep, self.adb = http or fl.Http(), sleep, adb
        base = os.path.dirname(fl.cache_dir({k: v for k, v in env.items() if k != "SLOT_LABELS_CACHE"}))
        self.cache = env.get("SLOT_HACKS_CACHE") or os.path.join(base, "hacks")
        self.config = env.get("SLOT_HACKS_CONFIG") or os.path.join(os.path.expanduser("~"), ".config", "slot-nes-snes")
        self.home = env.get("SLOT_HACKS_HOME") or os.path.join(os.path.expanduser("~"), "ROMHacks")


def latest_release(ctx, repo):
    """The GitHub latest-release JSON (cached an hour: unauthenticated callers get 60 requests an hour)."""
    text = fl.cached_text(ctx, f"github/{repo.replace('/', '__')}.json", f"{GITHUB}{repo}/releases/latest", HOUR)
    return json.loads(text)


def pick_asset(release, pattern):
    assets = [a for a in release.get("assets") or [] if fnmatch.fnmatch(a.get("name", "").lower(),
                                                                         (pattern or "*").lower())]
    return assets[0] if len(assets) == 1 else None


def check_one(ctx, hid, h, installed):
    """(latest, status, link) for one hack. Never writes outside the cache dir."""
    kind, _, rest = h["source"].partition(":")
    if kind == "github":
        try:
            rel = latest_release(ctx, rest)
        except (fl.Fail, ValueError) as e:
            return "?", f"error: {e}", f"https://github.com/{rest}/releases"
        latest = rel.get("tag_name") or rel.get("name") or "?"
        if installed == "unknown":
            status = "installed version unknown"
        else:
            status = "up to date" if norm_version(latest) == norm_version(installed) else "UPDATE AVAILABLE"
        if status != "up to date" and not pick_asset(rel, h.get("asset")):
            status += f" (no single asset matches {h.get('asset') or '*'})"
        return latest, status, rel.get("html_url") or f"https://github.com/{rest}/releases"
    if kind == "page":
        try:
            status_code, body = fl.fetch(ctx, rest)
        except fl.Fail as e:
            return "?", f"error: {e}", rest
        if status_code != 200:
            why = "the site refuses scripts, open the link" if status_code in (401, 403) else "error"
            return "?", f"{why} (HTTP {status_code})", rest
        text = body.decode("utf-8", "replace")
        if CHALLENGE.search(text[:20000]):  # a bot check page differs on every fetch: its hash means nothing
            return "?", "the site answers scripts with a bot check, open the link", rest
        repo = GITHUB_PAGE.fullmatch(rest)
        if repo and not h.get("version_regex"):  # GitHub's HTML changes per request: use the last push
            try:
                body = json.loads(fl.cached_text(ctx, f"github/{repo.group(1).replace('/', '__')}.repo.json",
                                                 GITHUB + repo.group(1), HOUR)).get("pushed_at", "").encode()
            except (fl.Fail, ValueError) as e:
                return "?", f"error: {e}", rest
        if h.get("version_regex"):
            found = [m.group(1) if m.groups() else m.group(0) for m in re.finditer(h["version_regex"], text)]
            if found:  # a page may list every version: the highest one
                latest = max(found, key=lambda v: [int(x) for x in re.findall(r"\d+", v)])
                if installed == "unknown":
                    return latest, "installed version unknown", rest
                same = norm_version(latest) == norm_version(installed)
                return latest, "up to date" if same else "UPDATE AVAILABLE", rest
        if not repo:  # the visible text only: scripts, comments and markup carry per-request noise
            body = " ".join(re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style)\b.*?</\1>|<!--.*?-->", " ",
                                                         text)).split()).encode()
        digest = hashlib.sha256(body).hexdigest()
        p = os.path.join(ctx.cache, "pages", f"{hid}-{zlib.crc32(rest.encode()) & 0xffffffff:08x}.json")
        seen = read_state(p)
        if not seen:
            write_state(p, {"sha256": digest, "date": time.strftime("%Y-%m-%d")})
            return "?", "page baseline recorded", rest
        if seen.get("sha256") == digest:
            return "?", f"page unchanged since {seen.get('date')}", rest
        return "?", f"page changed since {seen.get('date')}: look", rest
    return "?", "manual: no feed" if not rest else "manual", rest or h.get("home") or ""


def download(ctx, hid, version, asset):
    """(name, bytes) of a release asset, cached under the cache dir by version."""
    p = os.path.join(ctx.cache, "downloads", hid, re.sub(r"[^\w.-]", "_", version), asset["name"])
    if not os.path.isfile(p):
        status, body = fl.fetch(ctx, asset["browser_download_url"])
        if status != 200:
            raise Refuse(f"asset download failed (HTTP {status})")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        fl.spit(p, body)
    return asset["name"], fl.slurp(p)


def get_payload(ctx, hid, h, as_version=None):
    """(name, bytes, version) of the patch or pre-patched ROM to install. Never runs anything it reads."""
    kind, _, rest = h["source"].partition(":")
    if kind == "github":
        rel = latest_release(ctx, rest)
        asset = pick_asset(rel, h.get("asset"))
        if not asset:
            raise Refuse(f"no single release asset matches {h.get('asset') or '*'}")
        version = rel.get("tag_name") or "unknown"
        name, data = download(ctx, hid, version, asset)
        return name, data, as_version or version
    folder = os.path.join(ctx.home, "incoming", hid)
    files = [os.path.join(folder, n) for n in os.listdir(folder)] if os.path.isdir(folder) else []
    files = [f for f in files if os.path.isfile(f) and not os.path.basename(f).startswith(".")]
    if not files:
        raise Refuse(f"{h['source'] or 'no source'}: drop the patch (or patched ROM, or a zip of it) into {folder}")
    files = [f for f in files if os.path.basename(f) != "version.txt"]
    if not files:
        raise Refuse(f"only a version.txt in {folder}")
    p = max(files, key=os.path.getmtime)
    noted = fl.slurp(os.path.join(folder, "version.txt"), "r").strip() if os.path.isfile(
        os.path.join(folder, "version.txt")) else ""
    return os.path.basename(p), fl.slurp(p), as_version or noted or version_in_name(os.path.basename(p)) or "unknown"


def unpack(name, data, system):
    """('patch' or 'rom', name, bytes). A zip must hold exactly one patch or ROM; it is read in memory."""
    exts = fl.SYSTEMS[system][1]
    if name.lower().endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            hits = [i for i in z.infolist() if not i.is_dir() and not os.path.basename(i.filename).startswith(".")
                    and os.path.splitext(i.filename)[1].lower() in tuple(exts) + PATCH_EXTS]
            if len(hits) != 1:
                raise Refuse(f"{name} holds {len(hits)} patches/ROMs, want exactly one")
            name, data = os.path.basename(hits[0].filename), z.read(hits[0])
    ext = os.path.splitext(name)[1].lower()
    if ext in PATCH_EXTS or data[:4] in (b"BPS1", b"UPS1") or data[:5] == b"PATCH" or data[:3] == b"PPF":
        return "patch", name, data
    if ext in exts:
        return "rom", name, data
    raise Refuse(f"{name}: not a patch, a {system} ROM or a zip of one (7z/rar: extract it into the incoming folder)")


# ---- commands -----------------------------------------------------------------------------------------

def card_listing(card, systems):
    """{system: NFC names}: a card written from a Mac can hold NFD names (Pok\u0065\u0301mon)."""
    return {s: {fl.nfc(n) for n in card.names(f"Games/{s}")} for s in systems}


def real_name(card, system, name):
    """The name as the card spells it (NFC or NFD), so the stem keys the same saves and states."""
    return next((n for n in card.names(f"Games/{system}") if fl.nfc(n) == fl.nfc(name)), name)


def installed_version(state, hid, h):
    return (state.get(hid) or {}).get("version") or version_in_name(h["card"]) or "unknown"


def cmd_check(ctx, reg, args, card):
    state = read_state(os.path.join(ctx.config, "hacks-state.json"))
    on = card_listing(card, {h["system"] for h in reg.values()}) if card else None
    rows, absent = [], []
    for hid, h in sorted(reg.items(), key=lambda kv: (kv[1]["system"], kv[1]["name"].lower())):
        if on is not None and fl.nfc(h["card"]) not in on[h["system"]]:
            continue
        where = ""
        if on is None and args.library:
            try:
                where = "" if library_target(args.library, h) else "not in library"
            except (Refuse, zipfile.BadZipFile) as e:
                where = str(e)
            if where == "not in library" and hid not in state:
                absent.append(hid)  # never installed: no feed to fetch, no row
                continue
        inst = installed_version(state, hid, h)
        latest, status, link = check_one(ctx, hid, h, inst)
        # not for discs: identifying one by CRC means a full disc build (a minute) on every --check
        if args.library and h["system"] != "PS1" and (inst == "unknown" or not h["source"].startswith("github")):
            inst, status = by_crc(ctx, hid, h, args, card, state, inst, latest, status)
        rows.append((h["system"], hid, inst, latest, status + (f" [{where}]" if where else ""), link))
    for system, hid, inst, latest, status, link in rows:
        print(f"{system:<4} {hid:<30} installed {inst:<10} latest {latest:<12} {status}")
        if link and status != "up to date":
            print(f"     {link}")
    listing = {s: set(n) for s, n in on.items()} if on is not None else {
        s: {n for n in os.listdir(os.path.join(args.library, fl.SYSTEMS[s][0])) if not n.startswith(".")}
        for s in {h["system"] for h in reg.values()} if os.path.isdir(os.path.join(args.library, fl.SYSTEMS[s][0]))
    } if args.library else {}
    for system, mine, other in duplicates(reg, listing):
        print(f"warning: possible duplicate on the {'card' if on is not None else 'library'}: {system}/{other} "
              f"looks like another version of {mine} (left alone)")
    if absent:
        print(f"{len(absent)} registry hack(s) in neither the library nor the state file (install with --add <id>): "
              f"{', '.join(absent)}")
    print(f"\n{len(rows)} hack(s) checked. Nothing written to the card, the library or the settings; a version "
          "identified by CRC is recorded in hacks-state.json.")
    return rows


def by_crc(ctx, hid, h, args, card, state, inst, latest, status):
    """(installed, status) after building the known payloads and comparing them with the installed ROM's
    CRC32 (the library copy's, else the card's). A match is recorded in the state file."""
    crc = (state.get(hid) or {}).get("crc32") or library_crc(args.library, h)
    if not crc and card:
        data = card.read(f"Games/{h['system']}/{real_name(card, h['system'], h['card'])}")
        crc = crc_hex(data) if data else None
    if not crc:
        return inst, status
    try:
        found, newest = identify(ctx, hid, h, args.library, crc)
    except (fl.Fail, Refuse, ValueError, OSError) as e:
        return inst, f"{status}; could not build the patches: {e}"
    github = h["source"].startswith("github")
    if found:
        if found != (state.get(hid) or {}).get("version"):
            state[hid] = dict(state.get(hid) or {}, version=found, crc32=crc, date=time.strftime("%Y-%m-%d"),
                              card=h["card"], identified="by CRC")
            write_state(os.path.join(ctx.config, "hacks-state.json"), state)
        if github:
            return found, "up to date" if norm_version(found) == norm_version(latest) else "UPDATE AVAILABLE"
        return found, f"{status}; incoming {found} is what is installed"
    if newest is None:
        return inst, status
    if github:
        return inst, "UPDATE AVAILABLE (installed version unknown)"
    return inst, f"UPDATE AVAILABLE (from incoming {newest})"


def plan_update(ctx, hid, h, args, card, state, bases=()):
    """(card ops, library ops, record) or Refuse. Every refusal happens here, before any write. The card
    file and the library file are each exactly one, replaced in place under the same name."""
    system, rom = h["system"], card_target(card, h)
    stem = os.path.splitext(rom)[0]
    lib = library_target(args.library, h)
    st = state.get(hid) or {}
    moved = [f"{was!r} -> {now!r}" for was, now in ((st.get("card"), rom), (st.get("library"),
             os.path.basename(lib[0]) if lib else None)) if was and now and fl.nfc(was) != fl.nfc(now)]
    if moved and not args.accept_rename:
        raise Refuse(f"the file is not the one recorded at install ({'; '.join(moved)}): check it, then rerun "
                     "with --accept-rename")
    if h.get("base_name") and fl.nfc(stem) == fl.nfc(h["base_name"]):
        raise Refuse(f"{rom} is the clean base game, never a hack target: fix `card`")
    data = card.read(f"Games/{system}/{rom}")  # the card's own bytes: the backup records their CRC
    if data is None:
        raise Refuse(f"could not read Games/{system}/{rom}")
    card_crc = crc_hex(data)
    del data
    for where, crc in (("card file", card_crc), ("library file", target_crc(lib) if lib else None)):
        if crc and crc in bases:
            raise Refuse(f"the {where} is a clean base game ({crc}), never a hack target: fix `card`/`library`")
    if seated(card, system, stem):
        raise Refuse(f"{system}/{stem} is seated in slot (Config/slot.state cart=). Eject it first")
    if args.backup_root:
        reach(args.backup_root, args.dry_run)
    name, data, version = get_payload(ctx, hid, h, args.as_version)
    new = build(h, args.library, name, data)
    new_crc = crc_hex(new)
    old_crc = card_crc
    if old_crc == new_crc:
        raise Refuse(f"already installed ({new_crc}), nothing to do")
    old = installed_version(state, hid, h)
    label = f"{stamp()}_{re.sub(r'[^A-Za-z0-9._-]', '_', old)}"
    meta = {"kind": "update", "hack": hid, "from": old, "from_crc32": old_crc, "to": version, "to_crc32": new_crc}
    cbase = stem_dir(args.backup_root, system, stem) if args.backup_root else f"Backups/hacks/{system}/{stem}"
    cdir = free_dir(Split(card), cbase, label)
    card_ops = update_ops(card_items(card, system, stem, rom), cdir, card_map(cdir), [(new, f"Games/{system}/{rom}")], meta)
    lib_ops, ldir, lname = library_ops(ctx, lib, system, stem, label, new, meta) if lib else ([], None, None)
    record = {"version": version, "crc32": new_crc, "date": time.strftime("%Y-%m-%d"), "card": rom,
              "library": lname, "backup": cdir, "library_backup": ldir}
    return card_ops, lib_ops, record, h["saves_carry_over"], lib


def build(h, library, name, data, say=print):
    """The ROM a payload makes: a patch applied to the clean base found in the library by CRC32 (the
    registry's base_crc32, else the source CRC a BPS or UPS carries in its footer), or a pre-patched ROM."""
    system = h["system"]
    kind, name, data = unpack(name, data, system)
    if kind == "rom":
        say(f"  pre-patched ROM {name}")
        if h.get("target_crc32") and crc_hex(data) != h["target_crc32"].upper():
            raise Refuse(f"ROM CRC {crc_hex(data)} is not the registry's target_crc32 {h['target_crc32']}")
        return data
    want = (h.get("base_crc32") or "").upper()
    if not want and data[:4] in (b"BPS1", b"UPS1") and len(data) >= 12:
        want = f"{int.from_bytes(data[-12:-8], 'little'):08X}"  # the patch names its own source
    if not want:
        raise Refuse("the registry has no base_crc32 for this hack and an IPS names no source")
    if system == "PS1":
        base = disc_base(library, h)
        say(f"  base {os.path.basename(base)} track 1 ({want}), patch {name}")
        return build_disc(dict(h, base_crc32=want), base, data, say)[0]
    base, where = find_base(library, system, want)
    if base is None:
        raise Refuse(f"no clean base ROM with CRC32 {want} ({h.get('base_name') or '?'}) in "
                     f"{os.path.join(library, fl.SYSTEMS[system][0])}")
    say(f"  base {where} ({want}), patch {name}")
    return apply_patch(base, data, h.get("target_crc32"), warn=say)


def library_crc(library, h):
    """CRC32 of the library copy (zip header or loose file), else None (none, or ambiguous)."""
    try:
        t = library_target(library, h) if library else None
    except (Refuse, zipfile.BadZipFile):
        return None
    return target_crc(t) if t else None


def candidates(ctx, hid, h):
    """[(version, name, bytes)] of the payloads to try against the installed ROM: the newest GitHub releases
    with a matching asset (cached), and what waits in the incoming folder."""
    out = []
    kind, _, rest = h["source"].partition(":")
    if kind == "github":
        text = fl.cached_text(ctx, f"github/{rest.replace('/', '__')}.all.json",
                              f"{GITHUB}{rest}/releases?per_page={RELEASES}", HOUR)
        for rel in json.loads(text)[:RELEASES]:
            asset = pick_asset(rel, h.get("asset"))
            if asset:
                name, data = download(ctx, hid, rel.get("tag_name") or "unknown", asset)
                out.append((rel.get("tag_name") or "unknown", name, data))
    else:
        try:
            name, data, version = get_payload(ctx, hid, h)
            out.append((version, name, data))
        except (Refuse, OSError):
            pass
    return out


def identify(ctx, hid, h, library, installed_crc):
    """(version the installed ROM is, or None; version the newest payload builds, or None). A payload that
    does not build is skipped; when none builds, Refuse says why (the first one's reason)."""
    found = newest = None
    why = ""
    for version, name, data in candidates(ctx, hid, h):
        try:
            rom = build(h, library, name, data, say=lambda *_: None)
        except (Refuse, zipfile.BadZipFile) as e:
            why = why or f"{version}: {e}"
            continue
        newest = newest or version
        if crc_hex(rom) == installed_crc:
            found = version
            break
    if newest is None and why:
        raise Refuse(why)
    return found, newest


def confirm(args, what):
    if args.yes:
        return True
    try:
        return input(f"{what} [y/N] ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def cmd_update(ctx, reg, ids, args, card):
    path = os.path.join(ctx.config, "hacks-state.json")
    state, failed = read_state(path), 0
    bases = {(x.get("base_crc32") or "").upper() for x in reg.values()} - {""}
    for hid in ids:
        h = reg[hid]
        print(f"\n{hid}: {h['name']} ({h['system']}/{h['card']})")
        try:
            card_ops, lib_ops, record, saves, lib = plan_update(ctx, hid, h, args, card, state, bases)
        except (Refuse, fl.Fail, OSError, ValueError, zipfile.BadZipFile) as e:
            print(f"  refused: {e}")
            failed += 1
            continue
        print(f"  {installed_version(state, hid, h)} -> {record['version']} (CRC32 {record['crc32']})")
        show(card_ops, "card")
        show(lib_ops, "library")
        if saves == "no":
            print("  WARNING: the release notes say saves do NOT carry over. The .sav stays in place (and is "
                  "backed up); the new version may refuse it or start a new game.")
        elif saves == "unknown":
            print("  note: save compatibility across versions is unknown; the .sav stays in place and is backed up.")
        print("  all state folders move to the backup: slot must never load an old version's snapshot")
        if lib and lib[1]:
            zip_stem_note(lib[0])
        if library_states(args.library, h["system"], os.path.splitext(h["card"])[0]):
            print("  note: the library card's own RetroArch states are left alone; they may not work with the new version")
        if args.dry_run:
            print("  DRY RUN, nothing written")
            continue
        if not confirm(args, f"  apply {hid}?"):
            print("  skipped")
            continue
        done = []
        if not execute(Split(card), card_ops, "card", done):
            if args.backup_root and "remove" not in done:
                print(f"  the card is untouched; the partial copy in {record['backup']} has no backup.json, so "
                      "--rollback ignores it")
            else:
                print(f"  the card is half updated: run --rollback {hid} to put the old files back")
            failed += 1
            continue
        state[hid] = record  # the card is what counts: record it before the library
        write_state(path, state)
        if not execute(LocalCard(args.library), lib_ops, "library"):
            print("  WARNING: the card is updated but the library copy is not; the old library file is "
                  f"where the ops above left it (backup folder {record['library_backup']})")
            failed += 1
            continue
        print(f"  installed {record['version']}; backup {record['backup']}")
    return failed


def plan_add(ctx, hid, h, args, card, state, bases):
    """(card ops, library ops, record) that write a hack not on the card yet as a NEW loose file named
    `card` (and `library`, else the same) on the card and in the library. The base game is only read.
    Refuses, before any write, a name or a CRC32 that is already there."""
    system, name = h["system"], h["card"]
    lname, stem = h.get("library") or name, os.path.splitext(name)[0]
    if (state.get(hid) or {}).get("crc32"):
        raise Refuse(f"already installed ({state[hid]['crc32']} as {state[hid].get('card')}): use --update")
    folder = os.path.join(args.library, fl.SYSTEMS[system][0])
    on = {"card": card.names(f"Games/{system}"), "library": os.listdir(folder) if os.path.isdir(folder) else []}
    for where, names in on.items():
        same = [n for n in names if fl.nfc(os.path.splitext(n)[0]) in (fl.nfc(stem), fl.nfc(os.path.splitext(lname)[0]))]
        same += [other for _, _, other in duplicates({hid: h}, {system: set(names)})]
        if same:
            raise Refuse(f"the {where} already has {', '.join(sorted(set(same)))}: no duplicates (set `card` to it "
                         "in your settings and use --update)")
    left = [p for p, _ in card_items(card, system, stem, name)[1:]]
    if left:
        raise Refuse(f"the card already has saves or states for {stem}: {', '.join(left)} (move them first: a new "
                     "game must not load another file's snapshot)")
    pname, data, version = get_payload(ctx, hid, h, args.as_version)
    new = build(h, args.library, pname, data)
    crc = crc_hex(new)
    if crc in bases:
        raise Refuse(f"the patched ROM is a clean base game ({crc})")
    # Size first, then CRC: a library file is read on the Mac; a card file is read from its library copy of the
    # same name and size when there is one, and pulled from the card only when there is none.
    lib = {fl.nfc(n): os.path.join(folder, n) for n in on["library"]
           if os.path.isfile(os.path.join(folder, n)) and not n.startswith("._")}
    for n, p in sorted(lib.items()):
        if p.lower().endswith(".zip"):  # zip headers carry the CRC: free
            try:
                with zipfile.ZipFile(p) as z:
                    hit = any(f"{i.CRC:08X}" == crc for i in z.infolist())
            except zipfile.BadZipFile:
                hit = False
        else:
            hit = os.path.getsize(p) == len(new) and fl.file_crc(p) == crc
        if hit:
            raise Refuse(f"the library already has this ROM ({crc}) as {n}")
    for n, size in card.sizes(f"Games/{system}").items():
        if size != len(new):
            continue
        p = lib.get(fl.nfc(n))  # ponytail: same name and size taken as the same file; pull it if that ever lies
        got = fl.file_crc(p) if p and os.path.getsize(p) == size else crc_hex(card.read(f"Games/{system}/{n}") or b"")
        if got == crc:
            raise Refuse(f"the card already has this ROM ({crc}) as Games/{system}/{n}")
    card_ops = [("write", new, f"Games/{system}/{name}")]
    lib_ops = [("write", new, os.path.join(folder, lname))]
    record = {"version": version, "crc32": crc, "date": time.strftime("%Y-%m-%d"), "card": name, "library": lname,
              "added": True}
    return card_ops, lib_ops, record


def cmd_add(ctx, reg, hid, args, card):
    path = os.path.join(ctx.config, "hacks-state.json")
    state, h = read_state(path), reg[hid]
    print(f"\n{hid}: {h['name']} -> {h['system']}/{h['card']}")
    try:
        card_ops, lib_ops, record = plan_add(ctx, hid, h, args, card, state,
                                             {(x.get("base_crc32") or "").upper() for x in reg.values()} - {""})
    except (Refuse, fl.Fail, OSError, ValueError, zipfile.BadZipFile) as e:
        print(f"  refused: {e}")
        return 1
    print(f"  new {record['version']} (CRC32 {record['crc32']}); the base game is not touched")
    show(card_ops, "card")
    show(lib_ops, "library")
    if args.dry_run:
        print("  DRY RUN, nothing written")
        return 0
    if not confirm(args, f"  add {hid}?"):
        print("  skipped")
        return 0
    if not execute(card, card_ops, "card"):
        return 1
    state[hid] = record
    write_state(path, state)
    if not execute(LocalCard(args.library), lib_ops, "library"):
        print("  WARNING: on the card but not in the library")
        return 1
    print(f"  added {record['version']}; --check and --update now track it")
    return 0


def cmd_fix_zips(ctx, reg, args):
    """Unzip the library copy of every hack this tool updated (a `backup` in the state file) whose library
    copy is still a zip holding the installed ROM (its CRC is the state's crc32)."""
    path = os.path.join(ctx.config, "hacks-state.json")
    state, failed = read_state(path), 0
    for hid, st in sorted(state.items()):
        h = reg.get(hid)
        if not h or not st.get("backup"):
            print(f"{hid}: skipped, {'not in the registry' if not h else 'never updated by this tool'}")
            continue
        try:
            lib = library_target(args.library, dict(h, library=st.get("library") or h.get("library")))
            if not lib or not lib[1]:
                print(f"{hid}: {'no library copy' if not lib else 'already loose'}")
                continue
            crc = target_crc(lib)
            if crc != st.get("crc32"):
                raise Refuse(f"{os.path.basename(lib[0])} holds {crc}, the state file says {st.get('crc32')} is installed")
            with zipfile.ZipFile(lib[0]) as z:
                data = z.read(lib[1])  # zipfile checks the member's CRC
            stem = os.path.splitext(st.get("card") or h["card"])[0]
            # not "update": --rollback must skip this backup (it holds the new version) for the update's one
            meta = {"kind": "unzip", "hack": hid, "crc32": crc}
            ops, _, name = library_ops(ctx, lib, h["system"], stem, f"{stamp()}_unzip", data, meta)
        except (Refuse, OSError, zipfile.BadZipFile) as e:
            print(f"{hid}: refused: {e}")
            failed += 1
            continue
        print(f"{hid}: {os.path.basename(lib[0])} -> {name}")
        show(ops, "library")
        zip_stem_note(lib[0])
        if args.dry_run:
            print("  DRY RUN, nothing written")
            continue
        if not confirm(args, f"  unzip {hid}?"):
            print("  skipped")
            continue
        if not execute(LocalCard(args.library), ops, "library"):
            failed += 1
            continue
        state[hid] = dict(st, library=name)
        write_state(path, state)
    return failed


def cmd_rollback(ctx, reg, hid, args, card):
    h, path = reg[hid], os.path.join(ctx.config, "hacks-state.json")
    system, rom = h["system"], card_target(card, h, missing_ok=True)  # a half-done update
    stem = os.path.splitext(rom)[0]
    if seated(card, system, stem):
        raise Refuse(f"{system}/{stem} is seated in slot (Config/slot.state cart=). Eject it first")
    meta = {"kind": "rollback", "hack": hid}
    current = [(live, how) for live, how in card_items(card, system, stem, rom) if card.exists(live)]
    # every place a backup of this game can be: the card, the backups setting, the state file's last one
    bases, recorded = [f"Backups/hacks/{system}/{stem}"], (read_state(path).get(hid) or {}).get("backup") or ""
    for root in [args.backup_root] + [os.path.dirname(os.path.dirname(os.path.dirname(recorded)))
                                      if os.path.isabs(recorded) else None]:
        if root:
            reach(root, args.dry_run)
            bases.append(stem_dir(root, system, stem))
    safety = bases[1] if args.backup_root else bases[0]
    card_ops, info = rollback_ops(Split(card), current, bases, safety, card_map, meta)
    lib_ops, local = [], LocalCard(args.library) if args.library else None
    lbase = os.path.join(ctx.home, "backups", system, stem)
    if local and os.path.isdir(lbase):
        t = library_target(args.library, h)
        cur = [(t[0], "move")] if t else []
        lib_ops, _ = rollback_ops(local, cur, [lbase], lbase, lib_map, meta)
    print(f"{hid}: back to {info.get('from')} ({info.get('from_crc32')})")
    show(card_ops, "card")
    show(lib_ops, "library")
    if args.dry_run:
        print("  DRY RUN, nothing written")
        return
    if not confirm(args, f"  roll back {hid}?"):
        return
    if not execute(Split(card), card_ops, "card"):
        return 1
    if lib_ops and not execute(local, lib_ops, "library"):
        print("  WARNING: the card is rolled back but the library is not")
    state = read_state(path)
    state[hid] = {"version": info.get("from"), "crc32": info.get("from_crc32"),
                  "date": time.strftime("%Y-%m-%d"), "card": rom}
    write_state(path, state)
    print("  rolled back")


def cmd_migrate(ctx, args, card):
    """Move every backup in the card's Backups/hacks/ to the off-card backup root: each backup folder is
    copied file by file, checked (size and CRC32), and only then removed from the card. A folder already
    at the root with the same files is just removed from the card; one that differs is left alone."""
    root, path = args.backup_root, os.path.join(ctx.config, "hacks-state.json")
    if not root:
        print("refused: the backups setting is the card; give --backups <folder> or set it in hacks.json")
        return 1
    reach(root, args.dry_run)
    target, state, failed, plan = Split(card), read_state(path), 0, []
    for system in card.names("Backups/hacks"):
        for stem in card.names(f"Backups/hacks/{system}"):
            for label in card.names(f"Backups/hacks/{system}/{stem}"):
                src = f"Backups/hacks/{system}/{stem}/{label}"
                plan.append((src, f"{stem_dir(root, system, stem)}/{label}", tree(card, src)))
    for src, dst, files in plan:
        there = " (already there: checked, then removed from the card if identical)" if os.path.exists(dst) else ""
        print(f"  {src}  ->  {dst}  ({len(files)} file(s), {sum(files.values())} bytes){there}")
        for hid, st in sorted(state.items()):
            if fl.nfc(st.get("backup") or "") == fl.nfc(src):
                print(f"    hacks-state.json: {hid} backup -> {dst}")
    print(f"{len(plan)} backup(s), {sum(sum(f.values()) for _, _, f in plan)} bytes from the card to {root}")
    if args.dry_run or not plan:
        print("DRY RUN, nothing written" if args.dry_run else "nothing to migrate")
        return 0
    if not confirm(args, "move them?"):
        return 0
    for src, dst, _ in plan:
        if os.path.exists(dst) and not same_files(card, src, target.mac, dst):
            print(f"  {src}: {dst} exists with other files, left alone")
            failed += 1
            continue
        ops = ([] if os.path.exists(dst) else [("copy", src, dst)]) + [("remove", src, None)]
        if not execute(target, ops, "card"):
            failed += 1
            continue
        for hid, st in state.items():
            if fl.nfc(st.get("backup") or "") == fl.nfc(src):
                st["backup"] = dst
        write_state(path, state)
        print(f"  moved {src}")
    return failed


# a GoodTools or No-Intro region tag: a retail dump or revision, not a hack (V1.1, Rev 2)
REGION = re.compile(r"\((?:[JUEWFGSK]{1,3}|USA|Europe|Japan|World|Brazil|Korea|Unl|PD)(?:[,)]| )", re.I)
HACKISH = re.compile(r"\bv\d+(\.\d+)+[a-z]?\b|\bhack\b|\b(redux|definitive|delta|remix)\b", re.I)


def cmd_init(ctx, reg, card, library, backups="card"):
    """Write a commented example user settings file; never overwrite one."""
    path = os.path.join(ctx.config, "hacks.json")
    if os.path.exists(path):
        print(f"{path} exists, left as it is")
        return False
    have = card_listing(card, fl.SYSTEMS) if card else \
        {s: {n + ".x" for n in fl.scan_library(library, s)[0]} for s in fl.SYSTEMS} if library else {}
    known = {(h["system"], fl.nfc(h["card"])) for h in reg.values()}
    lines = ["// slot-nes-snes ROM hack settings (docs/HACKS.md), read on top of the repo's tools/hacks.json.",
             "// JSON with whole-line // comments. An id from the seed overrides only the fields given here;",
             "// a new id adds a hack and needs system, card and source.",
             "// source: \"github:<owner>/<repo>\" (with \"asset\": \"*.bps\"), \"page:<url>\" (optional",
             "// \"version_regex\"), \"manual\" or \"manual:<url>\". format: bps ips ups xdelta rom unknown.",
             "// saves_carry_over: yes no unknown. base_crc32: CRC32 of the clean No-Intro ROM the patch wants.",
             "{",
             "// Seed hacks found on this card; uncomment and edit a line to override a field:"]
    for hid, h in sorted(reg.items()):
        if not have or fl.nfc(h["card"]) in have.get(h["system"], set()) or (library and not card):
            lines.append(f'//  "{hid}": {{"source": {json.dumps(h["source"])}, "asset": {json.dumps(h.get("asset"))}}},')
    new = []
    for s, names in sorted(have.items()):
        for n in sorted(names):
            if (s, fl.nfc(n)) in known or re.search(r"\[[a-z!]", n, re.I) or not HACKISH.search(n) or REGION.search(n):
                continue
            hid = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", os.path.splitext(n)[0]).lower()).strip("-")
            new.append(f'  {json.dumps(hid)}: {{"system": "{s}", "card": {json.dumps(n)}, "source": "", '
                       f'"format": "unknown", "base_name": null, "base_crc32": null, "saves_carry_over": "unknown"}}')
    if new and not card:
        new = []  # library names carry no extension; only a card listing gives the real file names
    lines.append("// Other files on the card that look like hacks, with a blank source to fill in:")
    lines.append(",\n".join(new + ['// where --update keeps the old version (rollback backups): "card" (the card\'s\n'
                                    '// Backups/hacks/) or a mounted folder; --backups overrides it for one run\n'
                                    f'  "backups": {json.dumps(backups)}']))
    if not new:
        lines.insert(-1, "// (none detected)")
    lines.append("}")
    os.makedirs(ctx.config, exist_ok=True)
    fl.spit(path, "\n".join(lines) + "\n", "w")
    print(f"wrote {path} ({len(new)} detected hack(s) to fill in)")
    return True


def main(argv=None, ctx=None):
    ap = argparse.ArgumentParser(description="Check and update ROM hacks on a slot SD card.")
    ap.add_argument("--check", action="store_true", help="compare installed and latest versions (default, read only)")
    ap.add_argument("--update", metavar="ID", help="update one hack (id or name)")
    ap.add_argument("--all", action="store_true", help="update every hack on the card that has an update")
    ap.add_argument("--rollback", metavar="ID", help="restore the newest update backup of one hack")
    ap.add_argument("--add", metavar="ID", help="install a registry hack that is not on the card yet, as a new file")
    ap.add_argument("--init", action="store_true", help="write a commented example user settings file")
    ap.add_argument("--fix-library-zips", action="store_true",
                    help="unzip the library copies of updated hacks still in a zip (library only)")
    ap.add_argument("--card", help="a mounted SD card root")
    ap.add_argument("--device", action="store_true", help="the card inside the device, over adb")
    ap.add_argument("--expansion", help="with --card, the mounted Expansion Card root, for the systems "
                                        "Config/expansion.txt lists")
    ap.add_argument("--sd", default="/mnt/sdcard", help="device content root (default /mnt/sdcard)")
    ap.add_argument("--library", help="ROM library with gba/ gbc/ megadrive/ ... folders (needed to update)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    ap.add_argument("--yes", action="store_true", help="do not ask before applying")
    ap.add_argument("--accept-rename", action="store_true",
                    help="update although the card or library file name differs from the one recorded at install")
    ap.add_argument("--as-version", help="the version to record for a patch from the incoming folder")
    ap.add_argument("--backups", metavar="card|DIR",
                    help="where --update keeps the old version: the card, or a mounted folder (default: the "
                         "settings file's backups, else card)")
    ap.add_argument("--migrate-backups", action="store_true",
                    help="move the card's Backups/hacks/ to the off-card backups folder, checked, then removed")
    args = ap.parse_args(argv)
    ctx = ctx or Ctx()
    if args.card and args.device:
        ap.error("give at most one of --card or --device")
    args.library = os.path.abspath(os.path.expanduser(args.library)) if args.library else None
    card = LocalCard(os.path.abspath(os.path.expanduser(args.card)),
                     os.path.abspath(os.path.expanduser(args.expansion)) if args.expansion else None) if args.card else \
        AdbCard(ctx.adb or fl.adb_runner(), args.sd) if args.device else None
    if args.device:
        fl.Device(card.run, args.sd).check()
    user = os.path.join(ctx.config, "hacks.json")
    reg = load_registry(SEED, user)
    loc = args.backups or (read_jsonc(user) if os.path.isfile(user) else {}).get("backups") or "card"
    if not isinstance(loc, str):
        ap.error(f"{user}: backups must be \"card\" or a folder path")
    args.backup_root = None if loc == "card" else os.path.abspath(os.path.expanduser(loc))
    if args.init:
        return cmd_init(ctx, reg, card, args.library, loc)
    if args.migrate_backups:
        if not card:
            ap.error("--migrate-backups needs --card or --device")
        try:
            return cmd_migrate(ctx, args, card)
        except Refuse as e:
            print(f"refused: {e}")
            return 1
    if args.fix_library_zips:
        if not args.library:
            ap.error("--fix-library-zips needs --library")
        return cmd_fix_zips(ctx, reg, args)
    if args.update or args.all or args.rollback or args.add:
        if not card or not args.library:
            ap.error("--update, --all, --rollback and --add need --card or --device, and --library")

        def resolve(name):
            hit = [k for k, h in reg.items() if name.lower() in (k, h["name"].lower())]
            if not hit:
                ap.error(f"no hack {name!r} in the registry (ids: {', '.join(sorted(reg))})")
            return hit[0]
        if args.add:
            return cmd_add(ctx, reg, resolve(args.add), args, card)
        try:
            if args.rollback:
                return cmd_rollback(ctx, reg, resolve(args.rollback), args, card)
        except Refuse as e:
            print(f"refused: {e}")
            return 1
        if args.all:
            rows = cmd_check(ctx, reg, args, card)
            ids = [hid for _, hid, _, _, status, _ in rows if status.startswith("UPDATE AVAILABLE")]
            print(f"\nupdates available: {', '.join(ids) or 'none'}")
        else:
            ids = [resolve(args.update)]
        return cmd_update(ctx, reg, ids, args, card)
    return cmd_check(ctx, reg, args, card)


if __name__ == "__main__":
    try:
        r = main()
    except Refuse as e:
        sys.exit(f"refused: {e}")
    sys.exit(1 if isinstance(r, int) and not isinstance(r, bool) and r else 0)
