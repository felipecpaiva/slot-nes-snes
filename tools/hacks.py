#!/usr/bin/env python3
"""Check and update the ROM hacks on a slot SD card (and their library copies on the Mac).

    python3 tools/hacks.py --library /Volumes/MuOs/ROMS                      # --check, read only (default)
    python3 tools/hacks.py --device --library ~/ROMS --check                  # only the hacks on the card
    python3 tools/hacks.py --device --library ~/ROMS --update pokemon-unbound --dry-run
    python3 tools/hacks.py --device --library ~/ROMS --update pokemon-unbound
    python3 tools/hacks.py --device --library ~/ROMS --all --dry-run
    python3 tools/hacks.py --device --library ~/ROMS --rollback pokemon-unbound
    python3 tools/hacks.py --device --init                                    # write the user settings file

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
.bps .ips .ups, ROM, or a .zip holding exactly one of them). Nothing downloaded is ever executed. A patch is
applied in pure Python to the clean base ROM found in --library by CRC32 (BPS and UPS check the source,
target and patch CRCs; IPS has none, so the entry's target_crc32 is checked when known, else a warning).
Any mismatch refuses. Then, on the card (ADR 0082):
  - refuses while Config/slot.state has the game seated (cart= and cart_platform=): eject it first;
  - Backups/hacks/<SYS>/<stem>/<stamp>_<old version>/ gets the old ROM (moved), the .sav/.srm (copied:
    they stay in place, so the battery save carries on) and every state folder of the game
    (States/<SYS>/<core>/<stem>/: the ring, its thumbnails, resume.state, resume-refused-*; moved, so slot
    can never load an old version's snapshot into the new ROM), mirrored at their card paths, with a
    backup.json listing them;
  - the new ROM is written under the SAME file name, so labels, cart_shell, video_mode, selected_core,
    favourites, recents and the shelf memory stay attached.
The library copy gets the same: the old file (loose or zip, rewritten under the same zip and member name)
and RetroArch's <stem>.state* files next to it are moved to ~/ROMHacks/backups/<SYS>/<stem>/<label>/, the
.srm copied. Nothing is deleted anywhere.
--rollback <id> moves the current ROM, saves and states into a new backup and copies the newest update
backup back, on the card and in the library.
"""
import argparse
import fnmatch
import hashlib
import importlib.util
import io
import json
import os
import re
import shlex
import shutil
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
PATCH_EXTS = (".bps", ".ips", ".ups")
SOURCE = re.compile(r"github:[\w.-]+/[\w.-]+|page:https?://\S+|manual(:https?://\S+)?|")
FORMATS = {"bps", "ips", "ups", "xdelta", "rom", "unknown"}
FIELDS = {"name", "system", "card", "source", "asset", "version_regex", "format", "base_name", "base_crc32",
          "target_crc32", "saves_carry_over", "save_note", "latest_known", "home", "cite", "notes"}
HOUR = 3600


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
    elif p[:3] == b"\xd6\xc3\xc4":
        raise PatchError("xdelta patch: no pure-Python path here. Patch it yourself (e.g. xdelta3 -d) and drop "
                         "the ROM in the incoming folder")
    else:
        raise PatchError("unknown patch format")
    if target_crc and crc_hex(out) != target_crc.upper():
        raise PatchError(f"target CRC mismatch: got {crc_hex(out)}, the registry wants {target_crc.upper()}")
    return out


# ---- the card (mounted or over adb) and the library ----------------------------------------------

class LocalCard:
    """A mounted card or a temp dir. An absolute path is taken as is (the library and its Mac backups)."""

    def __init__(self, root):
        self.root = root

    def p(self, rel):
        return rel if os.path.isabs(rel) else os.path.join(self.root, *rel.split("/"))

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
            os.rename(self.p(src), d)


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

    def read(self, rel):
        with tempfile.TemporaryDirectory() as d:
            local = os.path.join(d, "f")
            rc, _ = self.run("pull", self.p(rel), local)
            return fl.slurp(local) if rc == 0 and os.path.isfile(local) else None

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


def seated(card, system, stem):
    """slot keeps the game in the slot in Config/slot.state: cart=<stem>, cart_platform=<system lowercase>."""
    text = (card.read("Config/slot.state") or b"").decode("utf-8", "replace")
    kv = dict(l.split("=", 1) for l in text.splitlines() if "=" in l)
    return kv.get("cart") == stem and kv.get("cart_platform", "").lower() in ("", system.lower())


def card_items(card, system, stem, rom):
    """[(card path, how)] of one game: the ROM and its state folders move, the battery saves are copied."""
    items = [(f"Games/{system}/{rom}", "move")]
    items += [(f"Saves/{system}/{stem}{e}", "copy") for e in (".sav", ".srm", ".disc")
              if card.exists(f"Saves/{system}/{stem}{e}")]
    items += [(f"States/{system}/{core}/{stem}", "move") for core in card.names(f"States/{system}")
              if card.isdir(f"States/{system}/{core}/{stem}")]
    return items


def library_items(lib, system, stem):
    """[(path, how, zip member or None)]: the library copies of stem (loose or zipped) and RetroArch's
    <stem>.state* files next to them move, its .srm is copied."""
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
        elif fl.nfc(n).startswith(key + ".state"):
            out.append((p, "move", None))
        elif fl.nfc(n) == key + ".srm":
            out.append((p, "copy", None))
    return out


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


def rezip(path, member, data):
    """path's zip rewritten with member holding data (the other members kept)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(path) as old, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as new:
        for i in old.infolist():
            new.writestr(i, data if i.filename == member else old.read(i))
    return buf.getvalue()


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
    ops = [("write", json.dumps(dict(meta, items=pairs), indent=2).encode(), f"{bdir}/backup.json")]
    ops += [(how, live, to_backup(live)) for live, how in sorted(items, key=lambda x: x[1] != "copy")]
    return ops + [("write", data, live) for data, live in writes]


def rollback_ops(target, current, base, to_backup_of, meta):
    """Move what is there now into a new backup, then copy the newest update backup back."""
    backups = []
    for n in target.names(base):
        info = target.read(f"{base}/{n}/backup.json")
        try:
            info = json.loads(info) if info else None
        except ValueError:
            info = None
        if info and info.get("kind") == "update":
            backups.append((n, info))
    if not backups:
        raise Refuse("no update backup to roll back to")
    name, info = max(backups, key=lambda b: b[0])
    sdir = free_dir(target, base, f"{stamp()}_rollback")
    ops = update_ops([(live, "move") for live, _ in current], sdir, to_backup_of(sdir), [], meta)
    return ops + [("copy", saved, live) for live, saved in info["items"]], info


def show(ops, where):
    for op, a, b in ops:
        src = f"{len(a)} bytes" if isinstance(a, bytes) else a
        print(f"    {where}: {op:<5} {src}  ->  {b}")


def execute(target, ops):
    for op, a, b in ops:
        target.apply(op, a, b)


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
        if h.get("version_regex"):
            found = [m.group(1) if m.groups() else m.group(0) for m in re.finditer(h["version_regex"], text)]
            if found:  # a page may list every version: the highest one
                latest = max(found, key=lambda v: [int(x) for x in re.findall(r"\d+", v)])
                if installed == "unknown":
                    return latest, "installed version unknown", rest
                same = norm_version(latest) == norm_version(installed)
                return latest, "up to date" if same else "UPDATE AVAILABLE", rest
        digest = hashlib.sha256(body).hexdigest()
        p = os.path.join(ctx.cache, "pages", hid + ".json")
        seen = read_state(p)
        if not seen:
            write_state(p, {"sha256": digest, "date": time.strftime("%Y-%m-%d")})
            return "?", "page baseline recorded", rest
        if seen.get("sha256") == digest:
            return "?", f"page unchanged since {seen.get('date')}", rest
        return "?", f"page changed since {seen.get('date')}: look", rest
    return "?", "manual: no feed" if not rest else "manual", rest or h.get("home") or ""


def get_payload(ctx, hid, h, as_version=None):
    """(name, bytes, version) of the patch or pre-patched ROM to install. Never runs anything it reads."""
    kind, _, rest = h["source"].partition(":")
    if kind == "github":
        rel = latest_release(ctx, rest)
        asset = pick_asset(rel, h.get("asset"))
        if not asset:
            raise Refuse(f"no single release asset matches {h.get('asset') or '*'}")
        version = rel.get("tag_name") or "unknown"
        p = os.path.join(ctx.cache, "downloads", hid, re.sub(r"[^\w.-]", "_", version), asset["name"])
        if not os.path.isfile(p):
            status, body = fl.fetch(ctx, asset["browser_download_url"])
            if status != 200:
                raise Refuse(f"asset download failed (HTTP {status})")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            fl.spit(p, body)
        return asset["name"], fl.slurp(p), as_version or version
    folder = os.path.join(ctx.home, "incoming", hid)
    files = [os.path.join(folder, n) for n in os.listdir(folder)] if os.path.isdir(folder) else []
    files = [f for f in files if os.path.isfile(f) and not os.path.basename(f).startswith(".")]
    if not files:
        raise Refuse(f"{h['source'] or 'no source'}: drop the patch (or patched ROM, or a zip of it) into {folder}")
    p = max(files, key=os.path.getmtime)
    return os.path.basename(p), fl.slurp(p), as_version or version_in_name(os.path.basename(p)) or "unknown"


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
    if ext in PATCH_EXTS or data[:4] in (b"BPS1", b"UPS1") or data[:5] == b"PATCH":
        return "patch", name, data
    if ext in exts:
        return "rom", name, data
    raise Refuse(f"{name}: not a patch, a {system} ROM or a zip of one (7z/rar: extract it into the incoming folder)")


# ---- commands -----------------------------------------------------------------------------------------

def card_listing(card, systems):
    return {s: set(card.names(f"Games/{s}")) for s in systems}


def installed_version(state, hid, h):
    return (state.get(hid) or {}).get("version") or version_in_name(h["card"]) or "unknown"


def cmd_check(ctx, reg, args, card):
    state = read_state(os.path.join(ctx.config, "hacks-state.json"))
    on = card_listing(card, {h["system"] for h in reg.values()}) if card else None
    rows = []
    for hid, h in sorted(reg.items(), key=lambda kv: (kv[1]["system"], kv[1]["name"].lower())):
        if on is not None and h["card"] not in on[h["system"]]:
            continue
        if on is None and args.library and not library_items(args.library, h["system"], os.path.splitext(h["card"])[0]):
            where = "not in library"
        else:
            where = ""
        inst = installed_version(state, hid, h)
        latest, status, link = check_one(ctx, hid, h, inst)
        rows.append((h["system"], hid, inst, latest, status + (f" [{where}]" if where else ""), link))
    for system, hid, inst, latest, status, link in rows:
        print(f"{system:<4} {hid:<30} installed {inst:<10} latest {latest:<12} {status}")
        if link and status != "up to date":
            print(f"     {link}")
    print(f"\n{len(rows)} hack(s) checked. Read only: nothing written to the card, the library or the settings.")
    return rows


def plan_update(ctx, hid, h, args, card, state):
    """(card ops, library ops, record) or Refuse. Every refusal happens here, before any write."""
    system, rom = h["system"], h["card"]
    stem = os.path.splitext(rom)[0]
    if not card.exists(f"Games/{system}/{rom}"):
        raise Refuse(f"Games/{system}/{rom} is not on the card")
    if seated(card, system, stem):
        raise Refuse(f"{system}/{stem} is seated in slot (Config/slot.state cart=). Eject it first")
    name, data, version = get_payload(ctx, hid, h, args.as_version)
    kind, name, data = unpack(name, data, system)
    if kind == "patch":
        if not h.get("base_crc32"):
            raise Refuse("the registry has no base_crc32 for this hack")
        base, where = find_base(args.library, system, h["base_crc32"].upper())
        if base is None:
            raise Refuse(f"no clean base ROM with CRC32 {h['base_crc32']} ({h.get('base_name') or '?'}) in "
                         f"{os.path.join(args.library, fl.SYSTEMS[system][0])}")
        print(f"  base {where} ({h['base_crc32'].upper()}), patch {name}")
        new = apply_patch(base, data, h.get("target_crc32"))
    else:
        print(f"  pre-patched ROM {name}")
        new = data
        if h.get("target_crc32") and crc_hex(new) != h["target_crc32"].upper():
            raise Refuse(f"ROM CRC {crc_hex(new)} is not the registry's target_crc32 {h['target_crc32']}")
    new_crc = crc_hex(new)
    lib = library_items(args.library, system, stem)
    old_crc = (state.get(hid) or {}).get("crc32")
    for p, _, m in lib:
        if m:
            with zipfile.ZipFile(p) as z:
                old_crc = old_crc or f"{z.getinfo(m).CRC:08X}"
        elif p.lower().endswith(tuple(fl.SYSTEMS[system][1])):
            old_crc = old_crc or fl.file_crc(p)
    if old_crc == new_crc:
        raise Refuse(f"already installed ({new_crc}), nothing to do")
    old = installed_version(state, hid, h)
    label = f"{stamp()}_{re.sub(r'[^A-Za-z0-9._-]', '_', old)}"
    meta = {"kind": "update", "hack": hid, "from": old, "from_crc32": old_crc, "to": version, "to_crc32": new_crc}
    cbase = f"Backups/hacks/{system}/{stem}"
    cdir = free_dir(card, cbase, label)
    card_ops = update_ops(card_items(card, system, stem, rom), cdir, card_map(cdir), [(new, f"Games/{system}/{rom}")], meta)
    lbase = os.path.join(ctx.home, "backups", system, stem)
    local = LocalCard(args.library)
    ldir = free_dir(local, lbase, label)
    writes = [(rezip(p, m, new) if m else new, p) for p, how, m in lib if how == "move" and
              (m or p.lower().endswith(tuple(fl.SYSTEMS[system][1])))]
    lib_ops = update_ops([(p, how) for p, how, _ in lib], ldir, lib_map(ldir), writes, meta) if lib else []
    record = {"version": version, "crc32": new_crc, "date": time.strftime("%Y-%m-%d"), "card": rom,
              "backup": cdir, "library_backup": ldir if lib else None}
    return card_ops, lib_ops, record, h["saves_carry_over"]


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
    for hid in ids:
        h = reg[hid]
        print(f"\n{hid}: {h['name']} ({h['system']}/{h['card']})")
        try:
            card_ops, lib_ops, record, saves = plan_update(ctx, hid, h, args, card, state)
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
        if args.dry_run:
            print("  DRY RUN, nothing written")
            continue
        if not confirm(args, f"  apply {hid}?"):
            print("  skipped")
            continue
        execute(card, card_ops)
        execute(LocalCard(args.library), lib_ops)
        state[hid] = record
        write_state(path, state)
        print(f"  installed {record['version']}; backup {record['backup']}")
    return failed


def cmd_rollback(ctx, reg, hid, args, card):
    h, path = reg[hid], os.path.join(ctx.config, "hacks-state.json")
    system, rom = h["system"], h["card"]
    stem = os.path.splitext(rom)[0]
    if seated(card, system, stem):
        raise Refuse(f"{system}/{stem} is seated in slot (Config/slot.state cart=). Eject it first")
    meta = {"kind": "rollback", "hack": hid}
    current = [(live, how) for live, how in card_items(card, system, stem, rom) if card.exists(live)]
    card_ops, info = rollback_ops(card, current, f"Backups/hacks/{system}/{stem}", card_map, meta)
    lib_ops, local = [], LocalCard(args.library) if args.library else None
    if local and os.path.isdir(os.path.join(ctx.home, "backups", system, stem)):
        cur = [(p, how) for p, how, _ in library_items(args.library, system, stem)]
        lib_ops, _ = rollback_ops(local, cur, os.path.join(ctx.home, "backups", system, stem), lib_map, meta)
    print(f"{hid}: back to {info.get('from')} ({info.get('from_crc32')})")
    show(card_ops, "card")
    show(lib_ops, "library")
    if args.dry_run:
        print("  DRY RUN, nothing written")
        return
    if not confirm(args, f"  roll back {hid}?"):
        return
    execute(card, card_ops)
    if lib_ops:
        execute(local, lib_ops)
    state = read_state(path)
    state[hid] = {"version": info.get("from"), "crc32": info.get("from_crc32"),
                  "date": time.strftime("%Y-%m-%d"), "card": rom}
    write_state(path, state)
    print("  rolled back")


HACKISH = re.compile(r"\bv\d+(\.\d+)+[a-z]?\b|\bhack\b|\b(redux|definitive|delta|remix)\b", re.I)


def cmd_init(ctx, reg, card, library):
    """Write a commented example user settings file; never overwrite one."""
    path = os.path.join(ctx.config, "hacks.json")
    if os.path.exists(path):
        print(f"{path} exists, left as it is")
        return False
    have = {s: set(card.names(f"Games/{s}")) for s in fl.SYSTEMS} if card else \
        {s: {n + ".x" for n in fl.scan_library(library, s)[0]} for s in fl.SYSTEMS} if library else {}
    known = {(h["system"], h["card"]) for h in reg.values()}
    lines = ["// slot-nes-snes ROM hack settings (docs/HACKS.md), read on top of the repo's tools/hacks.json.",
             "// JSON with whole-line // comments. An id from the seed overrides only the fields given here;",
             "// a new id adds a hack and needs system, card and source.",
             "// source: \"github:<owner>/<repo>\" (with \"asset\": \"*.bps\"), \"page:<url>\" (optional",
             "// \"version_regex\"), \"manual\" or \"manual:<url>\". format: bps ips ups xdelta rom unknown.",
             "// saves_carry_over: yes no unknown. base_crc32: CRC32 of the clean No-Intro ROM the patch wants.",
             "{",
             "// Seed hacks found on this card; uncomment and edit a line to override a field:"]
    for hid, h in sorted(reg.items()):
        if not have or h["card"] in have.get(h["system"], set()) or (library and not card):
            lines.append(f'//  "{hid}": {{"source": {json.dumps(h["source"])}, "asset": {json.dumps(h.get("asset"))}}},')
    new = []
    for s, names in sorted(have.items()):
        for n in sorted(names):
            if (s, n) in known or re.search(r"\[[a-z]", n, re.I) or not HACKISH.search(n):
                continue
            hid = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", os.path.splitext(n)[0]).lower()).strip("-")
            new.append(f'  {json.dumps(hid)}: {{"system": "{s}", "card": {json.dumps(n)}, "source": "", '
                       f'"format": "unknown", "base_name": null, "base_crc32": null, "saves_carry_over": "unknown"}}')
    if new and not card:
        new = []  # library names carry no extension; only a card listing gives the real file names
    lines.append("// Other files on the card that look like hacks, with a blank source to fill in:")
    lines.append(",\n".join(new) if new else "// (none detected)")
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
    ap.add_argument("--init", action="store_true", help="write a commented example user settings file")
    ap.add_argument("--card", help="a mounted SD card root")
    ap.add_argument("--device", action="store_true", help="the card inside the device, over adb")
    ap.add_argument("--sd", default="/mnt/sdcard", help="device content root (default /mnt/sdcard)")
    ap.add_argument("--library", help="ROM library with gba/ gbc/ megadrive/ ... folders (needed to update)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    ap.add_argument("--yes", action="store_true", help="do not ask before applying")
    ap.add_argument("--as-version", help="the version to record for a patch from the incoming folder")
    args = ap.parse_args(argv)
    ctx = ctx or Ctx()
    if args.card and args.device:
        ap.error("give at most one of --card or --device")
    args.library = os.path.abspath(os.path.expanduser(args.library)) if args.library else None
    card = LocalCard(os.path.abspath(os.path.expanduser(args.card))) if args.card else \
        AdbCard(ctx.adb or fl.adb_runner(), args.sd) if args.device else None
    if args.device:
        fl.Device(card.run, args.sd).check()
    reg = load_registry(SEED, os.path.join(ctx.config, "hacks.json"))
    if args.init:
        return cmd_init(ctx, reg, card, args.library)
    if args.update or args.all or args.rollback:
        if not card or not args.library:
            ap.error("--update, --all and --rollback need --card or --device, and --library")

        def resolve(name):
            hit = [k for k, h in reg.items() if name.lower() in (k, h["name"].lower())]
            if not hit:
                ap.error(f"no hack {name!r} in the registry (ids: {', '.join(sorted(reg))})")
            return hit[0]
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
    r = main()
    sys.exit(1 if isinstance(r, int) and not isinstance(r, bool) and r else 0)
