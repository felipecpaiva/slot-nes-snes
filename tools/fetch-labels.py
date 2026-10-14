#!/usr/bin/env python3
"""Fetch real cart labels (never box art, never a screenshot) for the ROMs on a slot SD card.

    python3 tools/fetch-labels.py --card /Volumes/SLOT                       # a mounted card
    python3 tools/fetch-labels.py --device --library ~/ROMS                  # SD card stays in the device, over adb
    python3 tools/fetch-labels.py --device --library ~/ROMS --only GBA --limit 5 --dry-run

--card   <root>: scans Games/<SYSTEM>/ on the card, writes Labels/<SYSTEM>/<stem>.png and Labels/cart_shell.txt.
--device:        lists Games/<SYSTEM>/ on the device with a shell glob (its ls adds colour codes), finds each
                 stem's CRC32 in --library (<library>/nes snes gba gb gbc, loose or zipped; the stem of a zipped
                 ROM is the stem of the ROM inside the zip, as scripts/push-roms.py names it), stages the labels
                 locally and adb pushes only the new ones.
Never overwrites a PNG or a cart_shell.txt line without --force. Reruns are cheap: everything fetched is cached
under the user's cache dir, and a stem that already has a label is skipped before it is even hashed.

Label sources, in order, per ROM:
  1. https://art.slot-cfw.fyi/ (Brandon Kowalski's art set, GBA/GB/GBC: index.json maps CRC32 to the real
     support-texture label). One request at a time, a short pause, a User-Agent naming this project.
  2. ScreenScraper support-texture, when SS_DEVID and SS_DEVPASSWORD (and usually SS_SSID, SS_SSPASSWORD) are set.
     Credentials are never printed. Stops cleanly when the quota is spent; the next run resumes.
  A ROM with neither is reported as missing. (libretro Named_Logos on a generated ground needs image code
  beyond the standard library, so that fallback is not implemented.)
The PNG is written as fetched: slot cover-fits any PNG into the label box and caches it itself (art.rs,
label_cache.rs), so a pre-cropped image buys nothing. Restart slot after pushing.
"""
import argparse
import json
import os
import shlex
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import zlib
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "slot-nes-snes-fetch-labels/1.0 (+https://github.com/felipecpaiva/slot-nes-snes)"
ART = "https://art.slot-cfw.fyi/"
DAT = "https://raw.githubusercontent.com/libretro/libretro-database/master/metadat/no-intro/"
SS_API = "https://api.screenscraper.fr/api2/"
NO_INTRO = "Nintendo - "
# system -> (library folder, ROM extensions, libretro dats, ScreenScraper system id)
SYSTEMS = {
    "GBA": ("gba", {".gba"}, [NO_INTRO + "Game Boy Advance"], 12),
    "GB": ("gb", {".gb", ".gbc"}, [NO_INTRO + "Game Boy"], 9),
    "GBC": ("gbc", {".gb", ".gbc"}, [NO_INTRO + "Game Boy Color"], 10),
    "NES": ("nes", {".nes", ".unf"},
            [NO_INTRO + "Nintendo Entertainment System", NO_INTRO + "Nintendo Entertainment System (Headered)"], 3),
    "SNES": ("snes", {".sfc", ".smc", ".swc", ".fig"}, [NO_INTRO + "Super Nintendo Entertainment System"], 4),
}
ART_SYSTEMS = {"GBA", "GB", "GBC"}
# slot's own plastic for a cart with no per-title colour (patch 0012), so a line only sets the outline
SHELL_COLOUR = {"famicom": "7a7a7a", "sfc": "949696"}
PNG = b"\x89PNG\r\n\x1a\n"
DAY = 86400


class Stop(Exception):
    """A source is done for this run (rate limit, quota, refused). Not a per-ROM failure."""


class Fail(Exception):
    """One ROM could not be fetched. The message never holds a URL (they can carry credentials)."""


def slurp(path, mode="rb"):
    with open(path, mode, **({} if "b" in mode else {"encoding": "utf-8", "errors": "replace"})) as f:
        return f.read()


def spit(path, data, mode="wb"):
    with open(path, mode, **({} if "b" in mode else {"encoding": "utf-8", "newline": "\n"})) as f:
        f.write(data)


def nfc(s):
    return unicodedata.normalize("NFC", s)


def cache_dir(env):
    if env.get("SLOT_LABELS_CACHE"):
        return env["SLOT_LABELS_CACHE"]
    home = os.path.expanduser("~")
    base = os.path.join(home, "Library", "Caches") if sys.platform == "darwin" else \
        env.get("XDG_CACHE_HOME") or os.path.join(home, ".cache")
    return os.path.join(base, "slot-nes-snes", "labels")


# ---- network ---------------------------------------------------------------------------------

class Http:
    def get(self, url):
        """(status, body, retry_after). Network trouble raises Fail without the URL."""
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read(), None
        except urllib.error.HTTPError as e:
            return e.code, b"", e.headers.get("Retry-After")
        except (urllib.error.URLError, OSError):
            raise Fail("network error") from None


def fetch(ctx, url, delay=0.3, tries=4):
    """One request, politely: a pause after it, and 429 retried with the server's own Retry-After."""
    for attempt in range(tries):
        status, body, retry = ctx.http.get(url)
        ctx.sleep(delay)
        if status != 429:
            return status, body
        if attempt < tries - 1:
            ctx.sleep(int(retry) if retry and retry.isdigit() else 20 * (attempt + 1))
    return 429, b""


def cached_text(ctx, rel, url, ttl, optional=False):
    p = os.path.join(ctx.cache, rel)
    if os.path.isfile(p) and time.time() - os.path.getmtime(p) < ttl:
        return slurp(p, "r")
    status, body = fetch(ctx, url)
    if status == 404 and optional:
        return ""
    if status != 200:
        raise Fail(f"HTTP {status} for {os.path.basename(rel)}")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    spit(p, body)
    return body.decode("utf-8", "replace")


class Dat:
    def __init__(self, text):
        self.names, self.by_name = {}, {}
        for block in re.finditer(r"game\s*\((.*?)\n\)", text, re.S):
            name = re.search(r'name\s+"([^"]+)"', block.group(1))
            if not name:
                continue
            self.by_name.setdefault(nfc(name.group(1)), None)
            for crc in re.finditer(r"\bcrc\s+([0-9A-Fa-f]{8})", block.group(1)):
                self.names[crc.group(1).upper()] = name.group(1)
                self.by_name[nfc(name.group(1))] = crc.group(1).upper()


def load_dat(ctx, system):
    texts = [cached_text(ctx, f"dats/{n}.dat", DAT + urllib.parse.quote(n) + ".dat", 30 * DAY, optional=i > 0)
             for i, n in enumerate(SYSTEMS[system][2])]
    return Dat("\n".join(texts))


ART_PATH = re.compile(r"[A-Za-z0-9_-]+/[A-Za-z0-9_-]+/[0-9A-Fa-f]{8}\.png")


def load_art_index(ctx):
    """CRC32 -> art path for the art host, {} (with a clear message) when it will not serve us."""
    try:
        text = cached_text(ctx, "art/index.json", ART + "index.json", DAY)
        index = json.loads(text)
        return {k.upper(): v["support-texture"] for k, v in index.items()
                if isinstance(v, dict) and ART_PATH.fullmatch(str(v.get("support-texture", "")))}
    except (Fail, ValueError) as e:
        why = str(e)
        if "HTTP 403" in why or "HTTP 401" in why:
            why = f"the host refuses non-browser clients ({why.split(' for')[0]})"
        print(f"art host unavailable: {why}. Falling back to ScreenScraper where credentials are set.")
        return {}


def art_label(ctx, path):
    p = os.path.join(ctx.cache, "art", path)
    if os.path.isfile(p):
        return slurp(p)
    status, body = fetch(ctx, ART + urllib.parse.quote(path))
    if status == 404:
        return None
    if status == 429:
        raise Stop("art host rate limit")
    if status != 200 or not body.startswith(PNG):
        raise Fail(f"art host answered HTTP {status}")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    spit(p, body)
    return body


class ScreenScraper:
    REGION = {"USA": "us", "World": "wor", "Europe": "eu", "Japan": "jp"}

    def __init__(self, ctx):
        env = ctx.env
        self.ctx, self.stop, self.asked, self.left, self.pause = ctx, None, 0, None, 1.0
        self.ready = bool(env.get("SS_DEVID") and env.get("SS_DEVPASSWORD"))
        self.auth = {"devid": env.get("SS_DEVID", ""), "devpassword": env.get("SS_DEVPASSWORD", ""),
                     "softname": env.get("SS_SOFTNAME", "slot-nes-snes"), "output": "json"}
        if env.get("SS_SSID"):
            self.auth.update(ssid=env["SS_SSID"], sspassword=env.get("SS_SSPASSWORD", ""))
        self.started = False

    def call(self, endpoint, **params):
        status, body = fetch(self.ctx, SS_API + endpoint + "?" + urllib.parse.urlencode({**self.auth, **params}),
                             delay=self.pause)
        if status == 404:
            return None
        if status in (429, 430, 431):
            raise Stop("ScreenScraper quota or rate limit reached")
        if status in (401, 403):
            raise Stop(f"ScreenScraper refused the credentials (HTTP {status})")
        if status != 200:
            raise Fail(f"ScreenScraper answered HTTP {status}")
        try:
            return json.loads(body.decode("utf-8", "replace"))
        except ValueError:
            raise Fail("ScreenScraper sent an unreadable reply") from None

    def begin(self):
        """Read the account's own limits once, as the API's documentation asks of a client."""
        self.started = True
        if "ssid" not in self.auth:
            return  # ssuserInfos.php needs a member login; a developer-only login keeps the default pace
        user = ((self.call("ssuserInfos.php") or {}).get("response", {}).get("ssuser") or {})
        num = lambda *ks: next((int(str(user[k]).strip()) for k in ks if str(user.get(k, "")).strip().isdigit()), None)
        per_day, per_min = num("maxrequestsperday"), num("maxrequestspermin")
        if per_day is not None:
            self.left = max(0, per_day - (num("requeststoday") or 0))
        if per_min:
            self.pause = 60.0 / per_min

    def label(self, system, crc, name, size):
        d = os.path.join(self.ctx.cache, "ss", system)
        png, none = os.path.join(d, crc + ".png"), os.path.join(d, crc + ".none")
        if os.path.isfile(png):
            return slurp(png)
        if os.path.isfile(none) or not self.ready or self.stop:
            return None
        if self.ctx.dry:
            return b""
        try:
            if not self.started:
                self.begin()
            if self.left is not None and self.asked >= self.left:
                raise Stop("ScreenScraper daily quota spent")
            self.asked += 1
            data = self.call("jeuInfos.php", crc=crc, systemeid=SYSTEMS[system][3], romnom=name + ".bin",
                             romtaille=size or "")
            medias = ((data or {}).get("response", {}).get("jeu") or {}).get("medias") or []
            media = self.pick(medias, name)
            os.makedirs(d, exist_ok=True)
            if not media:
                spit(none, b"")
                return None
            status, body = fetch(self.ctx, str(media.get("url", "")), delay=self.pause)
            if status in (429, 430, 431):
                raise Stop("ScreenScraper quota or rate limit reached")
            if status != 200 or not body.startswith(PNG):
                raise Fail(f"ScreenScraper media download failed (HTTP {status}, not a PNG)")
            spit(png, body)
            return body
        except Stop as e:
            self.stop = str(e)
            return None

    def pick(self, medias, name):
        tag = re.search(r"\(([^)]*)\)", name)
        own = self.REGION.get(tag.group(1).split(",")[0].strip()) if tag else None
        same = [m for m in medias if m.get("type") == "support-texture"]
        for region in [own, "us", "wor", "eu", "jp"]:
            for m in same:
                if region and (m.get("region") or "").lower() == region:
                    return m
        return same[0] if same else None


# ---- ROMs and CRCs -------------------------------------------------------------------------------

class Rom:
    """One ROM, hashed lazily. zip_crc comes free from a zip header, a loose file is read on demand."""

    def __init__(self, stem, size, read, zip_crc=None):
        self.stem, self.size, self.read, self.zip_crc = stem, size, read, zip_crc

    def whole(self):
        if self.zip_crc is None:
            self.zip_crc = zlib.crc32(self.read())
        return self.zip_crc

    def crcs(self, system):
        """CRC32 candidates in the order the issue gives: NES whole file then without the 16-byte header,
        SNES without a 512-byte copier header (size % 1024 == 512) then the whole file."""
        if system == "SNES" and self.size % 1024 == 512:
            yield zlib.crc32(self.read()[512:])
        yield self.whole()
        if system == "NES" and self.size > 16:
            yield zlib.crc32(self.read()[16:])


def loose_rom(path):
    def read():
        with open(path, "rb") as f:
            return f.read()
    return Rom(os.path.splitext(os.path.basename(path))[0], os.path.getsize(path), read)


def scan_card(card, system):
    """(roms, collisions) for Games/<SYSTEM>/ on a mounted card."""
    d = os.path.join(card, "Games", system)
    by_stem, clash = {}, set()
    for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        p = os.path.join(d, n)
        if n.startswith(".") or not os.path.isfile(p) or os.path.splitext(n)[1].lower() not in SYSTEMS[system][1]:
            continue
        rom = loose_rom(p)
        key = nfc(rom.stem)
        if key in by_stem:
            clash.add(key)
        by_stem.setdefault(key, rom)
    return [r for k, r in by_stem.items() if k not in clash], sorted(clash)


def scan_library(lib, system):
    """nfc(stem) -> Rom for <lib>/<folder>. A zipped ROM is named for the ROM inside the zip."""
    folder, exts = SYSTEMS[system][0], SYSTEMS[system][1]
    d = os.path.join(lib, folder)
    out, bad = {}, []
    for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        p = os.path.join(d, n)
        if n.startswith("._") or not os.path.isfile(p):
            continue
        if os.path.splitext(n)[1].lower() in exts:
            rom = loose_rom(p)
            out.setdefault(nfc(rom.stem), rom)
        elif n.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(p) as z:
                    for i in z.infolist():
                        base = os.path.basename(i.filename)
                        if i.is_dir() or base.startswith("._") or os.path.splitext(base)[1].lower() not in exts:
                            continue
                        read = (lambda p=p, name=i.filename: zipfile.ZipFile(p).read(name))
                        out.setdefault(nfc(os.path.splitext(base)[0]), Rom(os.path.splitext(base)[0], i.file_size, read, i.CRC))
            except zipfile.BadZipFile:
                bad.append(n)
    return out, bad


def resolve(system, rom, dat, art):
    """The CRC32 (8 upper hex digits) that the dat or the art set knows, else a name match, else None."""
    for c in rom.crcs(system):
        crc = f"{c & 0xffffffff:08X}"
        if crc in dat.names or crc in art:
            return crc
    return dat.by_name.get(nfc(rom.stem))


# ---- cart_shell.txt ------------------------------------------------------------------------------

def tags(name):
    m = re.search(r"\(([^)]*)\)", name)
    return {t.strip() for t in m.group(1).split(",")} if m else set()


def shell_word(system, stem, dat_name):
    """'famicom' or 'sfc' when the dat's region says so and slot would not pick it itself, else None.
    slot already reads a NES stem's (Japan) tag and a SNES ROM's header; a line only adds what it misses."""
    t = tags(dat_name or "")
    if system == "NES":
        japan = lambda s: "Japan" in tags(s) and not tags(s) & {"USA", "Europe", "World"}
        return "famicom" if japan(dat_name or "") and not japan(stem) else None
    if system == "SNES":
        return "sfc" if t and not t & {"USA", "Canada", "World"} else None
    return None


def shell_entry(line):
    """slot's ini grammar (crates/slot-store/src/ini.rs): key = value, no #, ; or [ lines."""
    line = line.strip()
    if not line or line[0] in "#;[" or "=" not in line:
        return None
    key, value = line.split("=", 1)
    return (key.strip(), value.strip()) if key.strip() else None


def merge_shell(text, new, force):
    """(text, added, kept). Existing lines stay as they are unless force replaces the same key."""
    have = {nfc(e[0]) for e in map(shell_entry, text.splitlines()) if e}
    added = kept = 0
    if force:
        drop = {nfc(k) for k in new}
        text = "".join(l + "\n" for l in text.splitlines() if not (shell_entry(l) and nfc(shell_entry(l)[0]) in drop))
        have -= drop
    for stem, value in new.items():
        if nfc(stem) in have:
            kept += 1
            continue
        entry = f"{stem} = {value}"
        if shell_entry(entry) != (stem, value):
            print(f"  cannot hold a cart_shell line for {stem!r}")
            continue
        text += ("\n" if text and not text.endswith("\n") else "") + entry + "\n"
        added += 1
    return text, added, kept


# ---- adb ---------------------------------------------------------------------------------------

def adb_runner():
    if os.environ.get("ADB"):
        cmd, cwd = shlex.split(os.environ["ADB"]), None
    elif shutil.which("adb"):
        cmd, cwd = ["adb"], None
    else:
        cmd, cwd = ["mise", "exec", "--", "adb"], REPO

    def run(*args):
        r = subprocess.run([*cmd, *args], cwd=cwd, capture_output=True)
        return r.returncode, r.stdout.decode("utf-8", "replace")
    return run


class Device:
    def __init__(self, run, sd):
        self.run, self.sd = run, sd

    def check(self):
        rc, out = self.run("devices")
        if rc != 0 or not any(l.endswith("\tdevice") for l in out.splitlines()):
            sys.exit("No device found. Check the USB cable and run `adb devices`.")

    def names(self, path):
        # a shell glob, not ls: the device's ls colours names even through adb, so they never match
        q = "'" + path.replace("'", "'\\''") + "'"
        rc, out = self.run("shell", f'for f in {q}/*; do [ -e "$f" ] && echo "${{f##*/}}"; done; true')
        if rc != 0:
            sys.exit(f"could not list {path} on the device, refusing to go on blind")
        return [l.rstrip("\r") for l in out.splitlines() if l.strip()]

    def push(self, src, dest):
        self.run("shell", f"mkdir -p '{dest}'")
        rc, out = self.run("push", src + "/.", dest + "/")
        if rc != 0:
            print(f"  adb push to {dest} failed: {out.strip()[-200:]}")
        return rc == 0


# ---- the run -----------------------------------------------------------------------------------

class Ctx:
    def __init__(self, http=None, adb=None, env=None, sleep=time.sleep, dry=False):
        self.env = os.environ if env is None else env
        self.http, self.adb, self.sleep, self.dry = http or Http(), adb, sleep, dry
        self.cache = cache_dir(self.env)
        self.stats, self.art, self.ss, self.art_off = Counter(), {}, ScreenScraper(self), None
        self.shell, self.warned = {}, 0


def get_label(ctx, system, crc, rom, name):
    """(bytes or None). Never raises Stop; a stopped source is recorded and the next one tried."""
    path = ctx.art.get(crc)
    if path and not ctx.art_off:
        if ctx.dry:
            return b""
        try:
            body = art_label(ctx, path)
            if body:
                return body
        except Stop as e:
            ctx.art_off = str(e)
            print(f"  stopped using the art host: {e}. Rerun later; what is cached is kept.")
    return ctx.ss.label(system, crc, name or rom.stem, rom.size)


def process(ctx, system, roms, have, out, dat, args):
    stats, tried = ctx.stats, 0
    for rom in roms:
        stem, tag = rom.stem, f"{system}/{rom.stem}"
        if args.only_stem and nfc(stem) != nfc(args.only_stem):
            continue
        if f"{stem}.png".lower() in have and not args.force:
            stats["skipped"] += 1
            continue
        crc = resolve(system, rom, dat, ctx.art)
        if crc is None:
            stats["unknown"] += 1
            print(f"  unknown CRC  {tag}")
            continue
        if args.limit and tried >= args.limit:
            break
        tried += 1
        stats["matched"] += 1
        name = dat.names.get(crc)
        if name and re.sub(r"[^a-z0-9]", "", re.sub(r"\(.*?\)", "", name).lower()) != \
                re.sub(r"[^a-z0-9]", "", re.sub(r"\(.*?\)", "", stem).lower()):
            print(f"  renamed? {tag} is {name} by CRC")
        try:
            body = get_label(ctx, system, crc, rom, name)
        except Fail as e:
            stats["errors"] += 1
            print(f"  error  {tag}: {e}")
            continue
        if body is None:
            stats["missing"] += 1
            why = f", ScreenScraper stopped: {ctx.ss.stop}" if ctx.ss.stop else ""
            print(f"  missing  {tag} (CRC {crc}{', ' + name if name else ''}{why})")
            continue
        stats["written"] += 1
        word = shell_word(system, stem, name)
        if word:
            ctx.shell[stem] = f"{word} {SHELL_COLOUR[word]} solid"
        if ctx.dry:
            continue
        dest = os.path.join(out, "Labels", system, stem + ".png")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        spit(dest, body)


def summary(ctx, args):
    s = ctx.stats
    print("\n" + ("DRY RUN, nothing written. " if ctx.dry else "") + "Summary")
    for key, label in [("matched", "matched (CRC known)"), ("written", "would write" if ctx.dry else "written"),
                       ("skipped", "skipped (label exists)"), ("missing", "missing (no art found)"),
                       ("unknown", "unknown CRC"), ("errors", "errors"), ("collisions", "stem collisions"),
                       ("shell_added", "cart_shell lines added"), ("shell_kept", "cart_shell lines kept")]:
        print(f"  {label:<26}{s[key]}")
    for why in (ctx.art_off, ctx.ss.stop):
        if why:
            print(f"  stopped early: {why}. Rerun to resume.")
    if ctx.dry and ctx.ss.ready:
        print("  (a dry run never calls ScreenScraper: ROMs that would need it count as would-write, an upper bound)")


def run(args, ctx):
    systems = [s for s in SYSTEMS if not args.only_system or s == args.only_system]
    dev = Device(ctx.adb or adb_runner(), args.sd) if args.device else None
    if dev:
        dev.check()
    if ART_SYSTEMS & set(systems):
        ctx.art = load_art_index(ctx)
    if not ctx.art and not ctx.ss.ready:
        print("note: no art host index and no SS_DEVID/SS_DEVPASSWORD, so nothing can be fetched.")
    stage = tempfile.mkdtemp(prefix="fetch-labels-") if dev else None
    root = stage or args.card
    try:
        for system in systems:
            try:
                dat = load_dat(ctx, system)
            except Fail as e:
                ctx.stats["errors"] += 1
                print(f"{system}: no dat ({e}), skipped")
                continue
            if dev:
                names = dev.names(f"{args.sd}/Games/{system}")
                have_list = dev.names(f"{args.sd}/Labels/{system}")
                lib, bad = scan_library(args.library, system)
                stems, roms = {}, []
                for n in names:
                    stem, ext = os.path.splitext(n)
                    if n.startswith(".") or ext.lower() not in SYSTEMS[system][1]:
                        continue
                    stems.setdefault(nfc(stem), []).append(stem)
                for k, group in stems.items():
                    if len(group) > 1:
                        ctx.stats["collisions"] += 1
                        print(f"  collision  {system}/{group[0]} has {len(group)} files, nothing written")
                    elif k in lib:
                        src = lib[k]
                        roms.append(Rom(group[0], src.size, src.read, src.zip_crc))
                    else:
                        ctx.stats["unknown"] += 1
                        print(f"  unknown CRC  {system}/{group[0]} (not in the library)")
                print(f"{system}: {len(names)} on the device, {len(lib)} in the library" +
                      (f", {len(bad)} bad zips" if bad else ""))
            else:
                roms, clash = scan_card(args.card, system)
                for k in clash:
                    ctx.stats["collisions"] += 1
                    print(f"  collision  {system}/{k} has two extensions, nothing written")
                have_list = os.listdir(os.path.join(args.card, "Labels", system)) \
                    if os.path.isdir(os.path.join(args.card, "Labels", system)) else []
                print(f"{system}: {len(roms)} ROMs on the card")
            have = {n.lower() for n in have_list}
            process(ctx, system, roms, have, root, dat, args)
            if dev and not ctx.dry and os.path.isdir(os.path.join(stage, "Labels", system)):
                dev.push(os.path.join(stage, "Labels", system), f"{args.sd}/Labels/{system}")
        if ctx.shell:
            finish_shell(ctx, args, dev, stage)
    finally:
        if stage:
            shutil.rmtree(stage, ignore_errors=True)
    summary(ctx, args)
    return ctx.stats


def finish_shell(ctx, args, dev, stage):
    """Merge the new lines into Labels/cart_shell.txt (pulled from the device, or read off the card)."""
    local = os.path.join(stage, "cart_shell.txt") if dev else os.path.join(args.card, "Labels", "cart_shell.txt")
    text = ""
    if dev:
        if "cart_shell.txt" in dev.names(f"{args.sd}/Labels"):
            rc, _ = dev.run("pull", f"{args.sd}/Labels/cart_shell.txt", local)
            if rc != 0:
                sys.exit("could not pull Labels/cart_shell.txt, refusing to overwrite it blind")
            text = slurp(local, "r")
    elif os.path.isfile(local):
        text = slurp(local, "r")
    merged, added, kept = merge_shell(text, ctx.shell, args.force)
    ctx.stats["shell_added"], ctx.stats["shell_kept"] = added, kept
    if ctx.dry or merged == text:
        return
    os.makedirs(os.path.dirname(local), exist_ok=True)
    spit(local, merged, "w")
    if dev:
        dev.run("shell", f"mkdir -p '{args.sd}/Labels'")
        dev.run("push", local, f"{args.sd}/Labels/cart_shell.txt")


def main(argv=None, ctx=None):
    ap = argparse.ArgumentParser(description="Fetch real cart labels for the ROMs on a slot SD card.")
    ap.add_argument("--card", help="a mounted SD card root (spec mode: CRC from the files on the card)")
    ap.add_argument("--device", action="store_true", help="work on the card inside the device over adb")
    ap.add_argument("--library", help="ROM library with nes/ snes/ gba/ gb/ gbc/ folders (needed by --device)")
    ap.add_argument("--sd", default="/mnt/sdcard", help="device content root (default /mnt/sdcard)")
    ap.add_argument("--only", help="one system (GBA, GB, GBC, NES, SNES) or one ROM stem")
    ap.add_argument("--dry-run", action="store_true", help="report what would happen; write and push nothing")
    ap.add_argument("--force", action="store_true", help="replace labels and cart_shell lines that already exist")
    ap.add_argument("--limit", type=int, default=0, help="per system, stop after N matched ROMs (smoke test)")
    args = ap.parse_args(argv)
    if bool(args.card) == args.device:
        ap.error("give exactly one of --card or --device")
    if args.device and not (args.library and os.path.isdir(os.path.expanduser(args.library))):
        ap.error("--device needs --library <folder>")
    if args.card and not os.path.isdir(os.path.expanduser(args.card)):
        ap.error(f"--card not found: {args.card}")
    args.card = os.path.abspath(os.path.expanduser(args.card)) if args.card else None
    args.library = os.path.abspath(os.path.expanduser(args.library)) if args.library else None
    args.only_system = args.only_stem = None
    if args.only:
        if args.only.upper() in SYSTEMS:
            args.only_system = args.only.upper()
        else:
            args.only_stem = args.only
    ctx = ctx or Ctx(dry=args.dry_run)
    ctx.dry = args.dry_run
    try:
        return run(args, ctx)
    except KeyboardInterrupt:
        print("\nstopped by hand; what was fetched is cached and pushed work is kept")
        sys.exit(130)


if __name__ == "__main__":
    main()
    sys.exit(0)
