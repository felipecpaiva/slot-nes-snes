#!/usr/bin/env python3
"""Fetch real cart labels (never a screenshot) for the ROMs on a slot SD card; Master System gets the box front,
PlayStation the front cover and the disc label.

    python3 tools/fetch-labels.py --card /Volumes/SLOT                       # a mounted card
    python3 tools/fetch-labels.py --device --library ~/ROMS                  # SD card stays in the device, over adb
    python3 tools/fetch-labels.py --device --library ~/ROMS --only GBA --limit 5 --dry-run

--card   <root>: scans Games/<SYSTEM>/ on the card, writes Labels/<SYSTEM>/<stem>.png and Labels/cart_shell.txt.
--device:        lists Games/<SYSTEM>/ on the device with a shell glob (its ls adds colour codes), finds each
                 stem's CRC32 in --library (<library>/nes snes gba gb gbc gamegear mastersystem megadrive psx, loose or zipped; the stem of a zipped
                 ROM is the stem of the ROM inside the zip, as scripts/push-roms.py names it), stages the labels
                 locally and adb pushes only the new ones.
Never overwrites a PNG or a cart_shell.txt line without --force. Reruns are cheap: everything fetched is cached
under the user's cache dir, and a stem that already has a label is skipped before it is even hashed.

Label sources, in order, per ROM:
  1. https://art.slot-cfw.fyi/ (Brandon Kowalski's art set, GBA/GB/GBC: index.json maps CRC32 to the real
     support-texture label). One request at a time, a short pause, a User-Agent naming this project.
  2. ScreenScraper support-texture, when SS_DEVID and SS_DEVPASSWORD (and usually SS_SSID, SS_SSPASSWORD) are set.
     Master System takes the front box art (box-2D) instead, for every game: its carts carry little more than the
     name, and slot draws the whole box in a tall well (ADR 0057). Labels fetched before that are kept until --force.
     Credentials are never printed. Stops cleanly when the quota is spent; the next run resumes.
     PlayStation (ADR 0069) takes the front cover (box-2D) to Labels/PS1/<stem>.png and the disc label scan
     (support-2D) to Labels/PS1/disc/<stem>.png from one jeuInfos call. A disc has no CRC in any dat, so it is
     matched by its serial (SYSTEM.CNF of a .cue's first track, DISC_ID of a .pbp's PARAM.SFO, sent as
     serialnum) plus the CRC32 and size of the disc file and its name (romnom); a .chd has no readable serial
     and goes by CRC and name. An .m3u stands for its first disc, the discs it names are skipped, and
     (Disc N) files with no playlist are one game under the stem slot gives them (Labels/PS1/<title>.png).
  A ROM with neither is reported as missing. (libretro Named_Logos on a generated ground needs image code
  beyond the standard library, so that fallback is not implemented.)
The PNG is written as fetched: slot fits any PNG into the label box (cover, or contain for the Master System
box) and caches it itself (art.rs, retro_cart.rs, label_cache.rs), so a pre-cropped image buys nothing. Restart slot after pushing.
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
SEGA = "Sega - "
# system -> (library folder, ROM extensions, libretro dats, ScreenScraper system id). The Sega dat names
# and ids are cited in docs/cart-art/SEGA.md (libretro-database metadat/no-intro; Skyscraper's platform map).
SYSTEMS = {
    "GBA": ("gba", {".gba"}, [NO_INTRO + "Game Boy Advance"], 12),
    "GB": ("gb", {".gb", ".gbc"}, [NO_INTRO + "Game Boy"], 9),
    "GBC": ("gbc", {".gb", ".gbc"}, [NO_INTRO + "Game Boy Color"], 10),
    "NES": ("nes", {".nes", ".unf"},
            [NO_INTRO + "Nintendo Entertainment System", NO_INTRO + "Nintendo Entertainment System (Headered)"], 3),
    "SNES": ("snes", {".sfc", ".smc", ".swc", ".fig"}, [NO_INTRO + "Super Nintendo Entertainment System"], 4),
    "GG": ("gamegear", {".gg"}, [SEGA + "Game Gear"], 21),
    "SMS": ("mastersystem", {".sms"}, [SEGA + "Master System - Mark III"], 2),
    "MD": ("megadrive", {".md", ".gen", ".bin"}, [SEGA + "Mega Drive - Genesis"], 1),
    # PlayStation discs are not in a No-Intro dat; ScreenScraper id 57 per Skyscraper's platforms_idmap.csv
    # (Gemba/skyscraper ccd49ae, row "psx,57,6,10"). The extensions are the ones slot scans (patch 0034).
    "PS1": ("psx", {".cue", ".chd", ".pbp", ".m3u"}, [], 57),
}
ART_SYSTEMS = {"GBA", "GB", "GBC"}
# ScreenScraper media type per system: the cart label scan, or the front box for Master System (ADR 0057)
MEDIA = {"SMS": "box-2D"}
LABEL = "support-texture"
# PlayStation: (ScreenScraper media type, folder under Labels/PS1) for the case cover and the disc (ADR 0069)
PS1_MEDIA = (("box-2D", ""), ("support-2D", "disc"))
# slot's own plastic for a cart with no per-title colour (patch 0012), so a line only sets the outline
SHELL_COLOUR = {"famicom": "7a7a7a", "sfc": "949696", "megadrive": "26242a"}
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
        kind = MEDIA.get(system, LABEL)
        # a box is cached apart from the label scans, so a scan cached before ADR 0057 is never served as a box
        d = os.path.join(self.ctx.cache, "ss", system, *([kind] if kind != LABEL else []))
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
            media = self.pick(medias, name, kind)
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

    def disc_media(self, key, ident, name, prefer):
        """{kind: bytes or None} for the PlayStation cover and disc of one game, from one jeuInfos call. The
        documentation (webapi2.php, jeuInfos.php) asks for a crc, md5 or sha1 and the size with every request;
        serialnum "Forcer la recherche du jeu avec le numero de série de la rom (iso)"."""
        dirs = {kind: os.path.join(self.ctx.cache, "ss", "PS1", kind) for kind, _ in PS1_MEDIA}
        out, want = {}, []
        for kind, d in dirs.items():
            png, none = os.path.join(d, key + ".png"), os.path.join(d, key + ".none")
            if os.path.isfile(png):
                out[kind] = slurp(png)
            elif os.path.isfile(none):
                out[kind] = None
            else:
                want.append(kind)
        if not want or not self.ready or self.stop:
            return {kind: out.get(kind) for kind in dirs}
        if self.ctx.dry:
            return {kind: out.get(kind, b"") for kind in dirs}
        try:
            if not self.started:
                self.begin()
            if self.left is not None and self.asked >= self.left:
                raise Stop("ScreenScraper daily quota spent")
            self.asked += 1
            params = dict(crc=ident["crc"], systemeid=SYSTEMS["PS1"][3], romtype="iso", romnom=ident["romnom"],
                          romtaille=ident["size"])
            if ident["serial"]:
                params["serialnum"] = ident["serial"]
            data = self.call("jeuInfos.php", **params)
            medias = ((data or {}).get("response", {}).get("jeu") or {}).get("medias") or []
            for kind in want:
                media = self.pick(medias, name, kind, prefer)
                os.makedirs(dirs[kind], exist_ok=True)
                if not media:
                    spit(os.path.join(dirs[kind], key + ".none"), b"")
                    out[kind] = None
                    continue
                status, body = fetch(self.ctx, str(media.get("url", "")), delay=self.pause)
                if status in (429, 430, 431):
                    raise Stop("ScreenScraper quota or rate limit reached")
                if status != 200 or not body.startswith(PNG):
                    raise Fail(f"ScreenScraper media download failed (HTTP {status}, not a PNG)")
                spit(os.path.join(dirs[kind], key + ".png"), body)
                out[kind] = body
        except Stop as e:
            self.stop = str(e)
        return {kind: out.get(kind) for kind in dirs}

    def pick(self, medias, name, kind=LABEL, prefer=None):
        tag = re.search(r"\(([^)]*)\)", name)
        own = (self.REGION.get(tag.group(1).split(",")[0].strip()) if tag else None) or prefer
        same = [m for m in medias if m.get("type") == kind]
        # slot decodes PNG only: a media that says it is another format goes last
        same.sort(key=lambda m: str(m.get("format", "png")).lower() != "png")
        for region in [own, "us", "wor", "eu", "jp"]:
            for m in same:
                if region and (m.get("region") or "").lower() == region:
                    return m
        return same[0] if same else None


# ---- ROMs and CRCs -------------------------------------------------------------------------------

class Rom:
    """One ROM, hashed lazily. zip_crc comes free from a zip header, a loose file is read on demand."""

    def __init__(self, stem, size, read, zip_crc=None, path=None):
        self.stem, self.size, self.read, self.zip_crc, self.path = stem, size, read, zip_crc, path

    def whole(self):
        if self.zip_crc is None:
            self.zip_crc = zlib.crc32(self.read())
        return self.zip_crc

    def crcs(self, system):
        """CRC32 candidates in the order the issue gives: NES whole file then without the 16-byte header,
        SNES without a 512-byte copier header (size % 1024 == 512) then the whole file, a Mega Drive SMD
        dump (as Genesis Plus GX detects one) de-interleaved, since No-Intro hashes the raw ROM."""
        if system == "SNES" and self.size % 1024 == 512:
            yield zlib.crc32(self.read()[512:])
        if system == "MD" and self.size % 512 == 0 and (self.size // 512) % 2 == 1:
            data = self.read()
            if data[0x100:0x104] != b"SEGA":
                yield zlib.crc32(deinterleave(data[512:]))
        yield self.whole()
        if system == "NES" and self.size > 16:
            yield zlib.crc32(self.read()[16:])


def deinterleave(smd):
    """Genesis Plus GX's deinterleave_block (core/loadrom.c): in each 16 KB block the second 8 KB are the
    even bytes and the first 8 KB the odd ones."""
    out = bytearray(len(smd))
    for at in range(0, len(smd) - len(smd) % 0x4000, 0x4000):
        out[at:at + 0x4000:2] = smd[at + 0x2000:at + 0x4000]
        out[at + 1:at + 0x4000:2] = smd[at:at + 0x2000]
    return bytes(out)


# ---- PlayStation discs -----------------------------------------------------------------------------

SECTOR, RAW_SECTOR, PVD = 2048, 2352, 16
SYNC = b"\x00" + b"\xff" * 10 + b"\x00"
SERIAL = re.compile(r"([A-Za-z]{4})[_-]?(\d{3})\.?(\d{2})")
DISC_TAG = re.compile(r"\(disc (\d+)(?: of \d+)?\)", re.I)
SERIAL_REGION = {"SLUS": "us", "SCUS": "us", "SLES": "eu", "SCES": "eu", "SLPS": "jp", "SCPS": "jp", "SLPM": "jp"}


def norm_serial(text):
    """SYSTEM.CNF says SLUS_005.94 and PARAM.SFO SLUS00594; both become the Redump form SLUS-00594."""
    m = SERIAL.search(text or "")
    if not m or m.group(1).upper() not in SERIAL_REGION:
        return None
    return f"{m.group(1).upper()}-{m.group(2)}{m.group(3)}"


def iso_serial(path):
    """The boot file named in SYSTEM.CNF, read the way slot's ps1.rs reads it (raw 2352 or plain 2048 sectors)."""
    try:
        with open(path, "rb") as f:
            f.seek(PVD * RAW_SECTOR)
            raw = f.read(12) == SYNC

            def sector(lba):
                if raw:
                    f.seek(lba * RAW_SECTOR + 15)
                    at = lba * RAW_SECTOR + (24 if f.read(1) == b"\x02" else 16)
                else:
                    at = lba * SECTOR
                f.seek(at)
                data = f.read(SECTOR)
                if len(data) != SECTOR:
                    raise ValueError("short sector")
                return data
            pvd = sector(PVD)
            if pvd[1:6] != b"CD001":
                return None
            lba, size = int.from_bytes(pvd[158:162], "little"), int.from_bytes(pvd[166:170], "little")
            cnf = None
            for n in range(min(4, -(-size // SECTOR))):
                d, at = sector(lba + n), 0
                while at < len(d) and d[at]:
                    rec = d[at:at + d[at]]
                    if rec[33:33 + rec[32]].split(b";")[0] == b"SYSTEM.CNF":
                        cnf = int.from_bytes(rec[2:6], "little")
                    at += d[at]
            if cnf is None:
                return None
            for line in sector(cnf).decode("latin-1").splitlines():
                if line.strip().upper().startswith("BOOT"):
                    return norm_serial(re.split(r"[\\:/]", line)[-1].split(";")[0].strip())
    except (OSError, ValueError, IndexError):
        return None
    return None


def pbp_serial(path):
    """DISC_ID from the PARAM.SFO at the offset the PBP header gives (PSF key and data tables)."""
    try:
        with open(path, "rb") as f:
            head = f.read(40)
            if head[:4] != b"\x00PBP":
                return None
            start, end = int.from_bytes(head[8:12], "little"), int.from_bytes(head[12:16], "little")
            f.seek(start)
            sfo = f.read(max(0, min(end - start, 65536)))
        if sfo[:4] != b"\x00PSF":
            return None
        keys, data, count = (int.from_bytes(sfo[o:o + 4], "little") for o in (8, 12, 16))
        for i in range(count):
            e = sfo[20 + 16 * i:36 + 16 * i]
            k = keys + int.from_bytes(e[0:2], "little")
            if sfo[k:sfo.index(b"\x00", k)] == b"DISC_ID":
                v = data + int.from_bytes(e[12:16], "little")
                return norm_serial(sfo[v:v + int.from_bytes(e[4:8], "little")].split(b"\x00")[0].decode("latin-1"))
    except (OSError, ValueError, IndexError):
        return None
    return None


def m3u_entries(path):
    """The disc paths an .m3u names, relative to the .m3u's folder, # lines and blanks skipped (slot's ps1.rs)."""
    base = os.path.dirname(path)
    lines = slurp(path, "r").replace("\r", "\n").split("\n")
    return [l if l.startswith(("/", "\\")) or l[1:3] in (":/", ":\\") else os.path.join(base, l)
            for l in lines if l and not l.startswith("#")]


def cue_track(path):
    for line in slurp(path, "r").splitlines():
        line = line.strip()
        if line[:5].lower() == "file ":
            rest = line[5:].strip()
            name = rest[1:].split('"')[0] if rest.startswith('"') else rest.split()[0]
            return os.path.join(os.path.dirname(path), name)
    return None


def file_crc(path):
    c = 0
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            c = zlib.crc32(block, c)
    return f"{c & 0xffffffff:08X}"


def crc_cache(ctx, hash_new):
    """A disc's CRC32, kept under the cache dir by path, size and mtime so a rerun never reads a disc
    twice. hash_new False only answers from that cache (a dry run, or nothing could be fetched)."""
    def crc_of(path):
        st = os.stat(path)
        key = f"{zlib.crc32(os.path.abspath(path).encode()) & 0xffffffff:08X}-{st.st_size}-{int(st.st_mtime)}"
        p = os.path.join(ctx.cache, "crc", "PS1", key)
        if os.path.isfile(p):
            return slurp(p, "r").strip()
        if not hash_new:
            return None
        crc = file_crc(path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        spit(p, crc, "w")
        return crc
    return crc_of


def disc_ident(path, crc_of=file_crc, depth=0):
    """{crc, size, romnom, serial} for the file that holds the game: an .m3u's first disc, a .cue's first track."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".m3u" and depth == 0:
        first = next(iter(m3u_entries(path)), None)
        return disc_ident(first, crc_of, 1) if first and os.path.isfile(first) else None
    if ext == ".cue":
        track = cue_track(path)
        return disc_ident(track, crc_of, depth + 1) if track and os.path.isfile(track) else None
    if not os.path.isfile(path):
        return None
    serial = pbp_serial(path) if ext == ".pbp" else iso_serial(path) if ext in (".bin", ".iso", ".img") else None
    return {"crc": crc_of(path), "size": os.path.getsize(path), "romnom": os.path.basename(path), "serial": serial}


def ps1_games(roms):
    """(stem, rom) as slot shows them: discs an .m3u names are dropped, (Disc N) files without one become one game
    named for the title without the tag, played from its lowest disc (slot's ps1::tidy and disc_tag)."""
    named = set()
    for r in roms:
        if r.path and r.path.lower().endswith(".m3u"):
            try:
                named |= {os.path.normcase(os.path.abspath(p)).lower() for p in m3u_entries(r.path)}
            except OSError:
                pass
    left = [r for r in roms if not (r.path and os.path.normcase(os.path.abspath(r.path)).lower() in named)]
    groups = {}
    for r in left:
        m = DISC_TAG.search(r.stem)
        if m and not (r.path or "").lower().endswith(".m3u"):
            base = " ".join((r.stem[:m.start()] + " " + r.stem[m.end():]).split())
            groups.setdefault(base, []).append((int(m.group(1)), r))
    out, gone = [], set()
    for base, discs in groups.items():
        if len(discs) > 1:
            discs.sort(key=lambda d: d[0])
            out.append((base, discs[0][1]))
            gone |= {id(r) for _, r in discs}
    return [(r.stem, r) for r in left if id(r) not in gone] + out


def loose_rom(path):
    def read():
        with open(path, "rb") as f:
            return f.read()
    return Rom(os.path.splitext(os.path.basename(path))[0], os.path.getsize(path), read, path=path)


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


GOODTOOLS = {"J": "Japan", "U": "USA", "E": "Europe"}


def regions(name):
    """Every bracket group's tags, a GoodTools code such as J, JU or UE read as its regions, as slot's nes.rs reads a stem."""
    out = set()
    for group in re.findall(r"\(([^)]*)", name):
        for t in (t.strip() for t in group.split(",")):
            out |= {GOODTOOLS[c] for c in t} if t and all(c in GOODTOOLS for c in t) else {t}
    return out


def shell_word(system, stem, dat_name):
    """'famicom', 'sfc' or 'megadrive' when the dat's region says so and slot might not pick it itself, else
    None. slot already reads a NES stem's (Japan) tag and a SNES or Mega Drive ROM's header; a line only adds
    what it misses (a Japanese Mega Drive release whose header also lists U or E)."""
    t = tags(dat_name or "")
    if system == "NES":
        japan = lambda s: "Japan" in regions(s) and not regions(s) & {"USA", "Europe", "World"}
        return "famicom" if japan(dat_name or "") and not japan(stem) else None
    if system == "SNES":
        return "sfc" if t and not t & {"USA", "Canada", "World"} else None
    if system == "MD":
        return "megadrive" if "Japan" in t and not t & {"USA", "Europe", "World", "Brazil"} else None
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
    stats, tried, kept = ctx.stats, 0, 0
    for rom in roms:
        stem, tag = rom.stem, f"{system}/{rom.stem}"
        if args.only_stem and nfc(stem) != nfc(args.only_stem):
            continue
        if f"{stem}.png".lower() in have and not args.force:
            stats["skipped"] += 1
            kept += 1
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
    if kept and system in MEDIA:
        print(f"  kept {kept} existing {system} label(s); any fetched before ADR 0057 is a cart scan, not the "
              f"{MEDIA[system]} box front. Rerun with --force --only {system} to replace them.")


def process_ps1(ctx, roms, have, have_disc, out, args):
    """Cover and disc for each PlayStation game. A game is skipped when both are on the card (unless --force)."""
    stats = ctx.stats
    tried = 0
    crc_of = crc_cache(ctx, ctx.ss.ready and not ctx.dry)
    for stem, rom in ps1_games(roms):
        tag = f"PS1/{stem}"
        if args.only_stem and nfc(stem) != nfc(args.only_stem):
            continue
        got = (f"{stem}.png".lower() in have, f"{stem}.png".lower() in have_disc)
        if all(got) and not args.force:
            stats["skipped"] += 1
            continue
        if args.limit and tried >= args.limit:
            break
        try:
            ident = disc_ident(rom.path, crc_of) if rom.path else None
        except OSError as e:
            ident = None
            print(f"  error  {tag}: {e.strerror or e}")
        if ident is None:
            stats["unknown"] += 1
            print(f"  unreadable disc  {tag} (no track file to identify)")
            continue
        tried += 1
        stats["matched"] += 1
        if not ident["serial"]:
            print(f"  no serial  {tag}, matched by CRC {ident['crc'] or '(not hashed in this run)'} and name")
        prefer = SERIAL_REGION.get((ident["serial"] or "")[:4])
        key = ident["serial"] or ident["crc"]
        try:
            if key:
                media = ctx.ss.disc_media(key, ident, stem, prefer)
            else:
                media = {kind: b"" if ctx.dry else None for kind, _ in PS1_MEDIA}
        except Fail as e:
            stats["errors"] += 1
            print(f"  error  {tag}: {e}")
            continue
        wrote = False
        for (kind, sub), exists in zip(PS1_MEDIA, got):
            body = media.get(kind)
            if exists and not args.force:
                continue
            if body is None:
                stats["missing"] += 1
                why = f", ScreenScraper stopped: {ctx.ss.stop}" if ctx.ss.stop else ""
                print(f"  missing  {tag} {kind} ({ident['serial'] or 'CRC ' + (ident['crc'] or 'not hashed')}{why})")
                continue
            stats["written"] += 1
            wrote = True
            if ctx.dry:
                continue
            dest = os.path.join(out, "Labels", "PS1", sub, stem + ".png")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            spit(dest, body)
        if not wrote and ctx.ss.stop:
            break


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
                disc_list = dev.names(f"{args.sd}/Labels/{system}/disc") if system == "PS1" else []
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
                        roms.append(Rom(group[0], src.size, src.read, src.zip_crc, src.path))
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
                disc_dir = os.path.join(args.card, "Labels", system, "disc")
                disc_list = os.listdir(disc_dir) if system == "PS1" and os.path.isdir(disc_dir) else []
                print(f"{system}: {len(roms)} ROMs on the card")
            have = {n.lower() for n in have_list}
            if system == "PS1":
                process_ps1(ctx, roms, have, {n.lower() for n in disc_list}, root, args)
            else:
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
    ap.add_argument("--only", help="one system (GBA, GB, GBC, NES, SNES, GG, SMS, MD, PS1) or one ROM stem")
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
