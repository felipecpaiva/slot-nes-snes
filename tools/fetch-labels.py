#!/usr/bin/env python3
"""Fetch real cart labels (never a screenshot) for the ROMs on a slot SD card; Master System gets the box front,
PlayStation the front cover and the disc label.

    python3 tools/fetch-labels.py --card /Volumes/SLOT                       # a mounted card
    python3 tools/fetch-labels.py --device --library ~/ROMS                  # SD card stays in the device, over adb
    python3 tools/fetch-labels.py --device --library ~/ROMS --only GBA --limit 5 --dry-run
    python3 tools/fetch-labels.py --device --library ~/ROMS --by-name --report by-name.tsv
    python3 tools/fetch-labels.py --device --library ~/ROMS --by-name --logo-fallback   # task labels:logo-tool first

--card   <root>: scans Games/<SYSTEM>/ on the card, writes Labels/<SYSTEM>/<stem>.png and Labels/cart_shell.txt.
--device:        lists Games/<SYSTEM>/ on the device with a shell glob (its ls adds colour codes), finds each
                 stem's CRC32 in --library (<library>/nes snes gba gb gbc gamegear mastersystem megadrive psx pcengine, loose or zipped; the stem of a zipped
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
  3. --by-name (opt in), for a ROM the CRC path leaves without a label (unknown CRC, no art, or with --device
     not in --library), in order:
     a. --aliases <tsv>: system, stem, ss:<game id> or sibling:<stem>, a match a human approved.
     b. a sibling: a label already on the card (or written earlier in this run) whose stem has the same
        title_key (tags, a GBA release number, The, accents and punctuation dropped; _ is a space; & 'n n' n
        read as and), or, for a name the card cut short (no tag, 30+ characters), the one title starting
        with it. The one sharing most regions, then the cleanest dump ([!] best, [b] [h] [p] [t] [f]
        last) is copied, with its cart_shell.txt line when the regions agree. With --device it comes from
        this run's stage, the cache, or adb pull into the cache. No network.
     c. a CRC the dat knows but with no label scan: that game's front box (box-2D).
     d. ScreenScraper jeuRecherche.php by the bare title (no "by <author>", a cut name without its last
        word; a Mega Drive 32X name first under the 32X id, without 32X), taken only when exactly one game
        has a name (any region) with the same title_key (a cut name: starting with it); otherwise "no
        confident match" and nothing is written. The media are the CRC path's; a missing label scan falls
        back to the front box, never a wheel or logo. Replies are cached by query, so changed rules judge
        them again offline. A dry run uses only cached answers.
     --report <file> writes a TSV row per ROM: system, stem, outcome, source (sibling stem, crc:<crc> or
     ss:<game id>), media. --suggest <file> writes, for each ROM still without a label, the nearest
     candidate (ss:<id> and its name, or sibling:<stem>) and why it was not taken; no art comes from it.
  4. --logo-fallback (opt in, needs --by-name), for a ROM still without a label after every pass above (ADR 0014):
     its logo on a generated ground (Cart Studio's Logo Only style), drawn by the slot-ui example logo_label
     (task labels:logo-tool builds build/slot/target/release/examples/logo_label; SLOT_LOGO_LABEL overrides it)
     at the label size slot draws for that system. The logo is libretro-thumbnails Named_Logos (none for GBC,
     GG, PS1, TG16; the index and the PNGs are cached under logos/) matched by title_key like a sibling (one title,
     a cut name only when one title starts with it, never a guess), else the ScreenScraper wheel of the game
     the name pass (or an ss: alias) matched. A hack ([h..] or "hack") takes a parent's logo only through
     --aliases (a sibling: alias names the title to look up). The outcome is "logo fallback", source
     libretro:<name> or ss:<id> wheel. A dry run matches and reports but downloads, renders and writes no logo.
     A ROM not searched for the quota, a stop or --limit gets none (a later run searches it). A logo label is
     a label to later runs: delete it or use --force to replace it with real art.
  PICO-8 (ADR 0101) needs no network and no dat: a cart carries its own label. A PNG cart (.p8.png, or a PNG
  under a .p8 name) is its own 160x205 picture with the label at (16, 24), 128x128; a text .p8 cart has a
  __label__ section of 128 lines of 128 palette digits (0-9 and a-v, the secret palette included). Either is
  written to Labels/PICO8/<stem>.png as a 128x128 PNG. A cart with no label is reported as missing.
  A ROM with no source is reported as missing.
The PNG is written as fetched: slot fits any PNG into the label box (cover, or contain for the Master System
box) and caches it itself (art.rs, retro_cart.rs, label_cache.rs), so a pre-cropped image buys nothing. Restart slot after pushing.
"""
import argparse
import csv
import difflib
import json
import os
import shlex
import re
import shutil
import struct
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
# libretro-thumbnails, served with a directory listing; Named_Logos exists for these (not GBC, GG, PS1 or TG16)
LOGOS = "https://thumbnails.libretro.com/"
# the Logo Only renderer, a slot-ui example (ADR 0014): task labels:logo-tool builds it
LOGO_TOOL = os.path.join(REPO, "build", "slot", "target", "release", "examples", "logo_label")
NO_INTRO = "Nintendo - "
SEGA = "Sega - "
BANDAI = "Bandai - "
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
    # PC Engine and TurboGrafx-16 HuCards: libretro-database metadat/no-intro; ScreenScraper id 31 per
    # Skyscraper's platforms_idmap.csv (Gemba/skyscraper ccd49ae, row "pcengine,31,40,34"). .pce only (patch 0058).
    "TG16": ("pcengine", {".pce"}, ["NEC - PC Engine - TurboGrafx 16"], 31),
    # One WonderSwan shelf for both handhelds, so both dats; ScreenScraper keeps them apart as wonderswan 45 and
    # wonderswancolor 46 (Skyscraper platforms_idmap.csv at ccd49ae, rows "wonderswan,45,48,4925" and
    # "wonderswancolor,46,49,4926"). The id is picked per ROM by its footer colour flag (system_id).
    "WS": ("wonderswan", {".ws", ".wsc"}, [BANDAI + "WonderSwan", BANDAI + "WonderSwan Color"], 45),
    # Atari Lynx: ScreenScraper id 28 per Skyscraper's platforms_idmap.csv (Gemba/skyscraper ccd49ae, row
    # "atarilynx,28,18,4924"); No-Intro and the core both hash a .lnx without its 64-byte header (ADR 0093).
    "Lynx": ("atarilynx", {".lnx", ".lyx"}, ["Atari - Lynx"], 28),
    # One shelf for both Neo Geo Pockets: the mono id here, the Color id from ss_id by the header byte. Ids
    # ngp 25 and ngpc 82 per Skyscraper's platforms_idmap.csv at ccd49ae, dats from libretro-database
    # metadat/no-intro (docs/research/ngp-plan.md section 6).
    "NGP": ("ngp", {".ngp", ".ngc", ".ngpc"}, ["SNK - Neo Geo Pocket", "SNK - Neo Geo Pocket Color"], 25),
    # Sega 32X: libretro-database metadat/no-intro "Sega - 32X"; ScreenScraper id 19 per Skyscraper's
    # platforms_idmap.csv (Gemba/skyscraper ccd49ae, row "sega32x,19,21,33"). .32x and .bin, as slot scans
    # (patch 0091); libretro-thumbnails has no Sega - 32X Named_Logos (checked 2026-10-20, 404).
    "32X": ("sega32x", {".32x", ".bin"}, [SEGA + "32X"], 19),
    # Atari 2600 and 7800: libretro-database metadat/no-intro "Atari - 2600" and "Atari - 7800"; ScreenScraper
    # ids 26 and 41 per Skyscraper's platforms_idmap.csv (Gemba/skyscraper c253bfe, rows "atari2600,26,28,22"
    # and "atari7800,41,34,27"). The shelf folders are A2600 and A7800, with the extensions slot scans (patch
    # 0100). The 7800 dat lists headered .a78 and headerless .bin CRCs; a headered dump is also tried without
    # its 128-byte header. libretro-thumbnails has 2600 Named_Logos and no 7800 ones (checked 2026-10-20, 404).
    "A2600": ("atari2600", {".a26", ".bin"}, ["Atari - 2600"], 26),
    "A7800": ("atari7800", {".a78"}, ["Atari - 7800"], 41),
    # Nintendo Virtual Boy: libretro-database metadat/no-intro "Nintendo - Virtual Boy"; ScreenScraper id 11 per
    # Skyscraper's platforms_idmap.csv (Gemba/skyscraper ccd49ae, row "virtualboy,11,38,4918"). .vb and .vboy, as
    # slot scans (ADR 0097); libretro-thumbnails has Nintendo - Virtual Boy Named_Logos (22, checked 2026-10-20).
    "VB": ("virtualboy", {".vb", ".vboy"}, [NO_INTRO + "Virtual Boy"], 11),
    # Arcade (ADR 0099): the zip is the romset, named after its FinalBurn Neo set, so there is no No-Intro
    # dat; ScreenScraper finds an arcade set by its file name (romnom). Ids per Skyscraper's
    # platforms_idmap.csv (Gemba/skyscraper c253bfe) row
    # "neogeo,142,36,24" for Neo Geo; CPS1 and CPS2 have no row there, and ScreenScraper's own system pages
    # name 6 "Capcom Play System" and 7 "Capcom Play System 2" (systemeinfos.php, checked 2026-10-20)
    "NEOGEO": ("neogeo", {".zip"}, [], 142),
    "CPS1": ("cps1", {".zip"}, [], 6),
    "CPS2": ("cps2", {".zip"}, [], 7),
    # PICO-8 (ADR 0101): the label is inside the cart (pico8_label), so no dat and no ScreenScraper id.
    # .p8 and .png, as slot scans; a .png only when named <name>.p8.png (pico8_admits).
    "PICO8": ("pico8", {".p8", ".png"}, [], None),
}
ARCADE = {"NEOGEO", "CPS1", "CPS2"}
# ScreenScraper media for an arcade set, in order: the cart label scan when it has one (a Neo Geo cart), else
# the flyer, which is what Skyscraper takes as an arcade game's cover (getCover), else the box front. Media
# type names from the API documentation (webapi2.php); which a given set has is not verified per game.
ARCADE_MEDIA = ("support-texture", "flyer", "box-2D")
# libretro-thumbnails folder for the arcade sets, keyed by the set's full title. It has no Named_Logos
# (checked 2026-10-20), so --logo-fallback takes the ScreenScraper wheel for an arcade set
ARCADE_THUMBS = "FBNeo - Arcade Games"
ARCADE_SETS = [os.path.join(REPO, d, "crates", "slot-store", "src", "arcade_sets.tsv")
               for d in (os.path.join("build", "slot"), os.path.join("work", "slot"))]
WS_COLOR_ID = 46
NGP_COLOR_ID = 82
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

    def spend(self):
        """One more request, or Stop when the account's daily quota is spent."""
        if not self.started:
            self.begin()
        if self.left is not None and self.asked >= self.left:
            raise Stop("ScreenScraper daily quota spent")
        self.asked += 1

    def download(self, media, png):
        """A picked media's PNG, written to png (the cache). Never prints the URL."""
        url = str(media.get("url", ""))
        if str(media.get("format", "png")).lower() != "png" and "outputformat=" not in url:
            url += ("&" if "?" in url else "?") + "outputformat=png"  # arcade flyers come as jpg; the API converts
        status, body = fetch(self.ctx, url, delay=self.pause)
        if status in (429, 430, 431):
            raise Stop("ScreenScraper quota or rate limit reached")
        if status != 200 or not body.startswith(PNG):
            raise Fail(f"ScreenScraper media download failed (HTTP {status}, not a PNG)")
        os.makedirs(os.path.dirname(png), exist_ok=True)
        spit(png, body)
        return body

    def label(self, system, crc, name, size, sysid=None):
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
            self.spend()
            data = self.call("jeuInfos.php", crc=crc, systemeid=sysid or sysid or SYSTEMS[system][3],
                             romnom=name + ".bin", romtaille=size or "")
            medias = ((data or {}).get("response", {}).get("jeu") or {}).get("medias") or []
            media = self.pick(medias, name, kind)
            os.makedirs(d, exist_ok=True)
            if not media:
                spit(none, b"")
                return None
            return self.download(media, png)
        except Stop as e:
            self.stop = str(e)
            return None

    def arcade_label(self, system, rom):
        """The first of ARCADE_MEDIA ScreenScraper has for an arcade set, asked by its file name (romnom, how
        ScreenScraper identifies arcade sets), with the zip's CRC32 and size the API asks for. Cached by set
        name. None when there is none."""
        d = os.path.join(self.ctx.cache, "ss", system, "arcade")
        png, none = os.path.join(d, rom.stem.lower() + ".png"), os.path.join(d, rom.stem.lower() + ".none")
        if os.path.isfile(png):
            return slurp(png)
        if os.path.isfile(none) or not self.ready or self.stop:
            return None
        if self.ctx.dry:
            return b""
        try:
            self.spend()
            params = dict(systemeid=SYSTEMS[system][3], romtype="rom", romnom=rom.stem + ".zip",
                          romtaille=rom.size or "")
            if rom.read:
                params["crc"] = f"{rom.whole() & 0xffffffff:08X}"
            data = self.call("jeuInfos.php", **params)
            medias = ((data or {}).get("response", {}).get("jeu") or {}).get("medias") or []
            os.makedirs(d, exist_ok=True)
            for kind in ARCADE_MEDIA:
                media = self.pick(medias, "", kind, None, ("wor", "us", "eu", "jp", "ss"))
                if media:
                    return self.download(media, png)
            spit(none, b"")
            return None
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
            self.spend()
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
                out[kind] = self.download(media, os.path.join(dirs[kind], key + ".png"))
        except Stop as e:
            self.stop = str(e)
        return {kind: out.get(kind) for kind in dirs}

    AUTH = ("devid", "devpassword", "softname", "ssid", "sspassword")

    def with_auth(self, url, add):
        """A media URL without the login (to keep in the cache), or with ours put back (to download)."""
        u = urllib.parse.urlsplit(url)
        q = [(k, v) for k, v in urllib.parse.parse_qsl(u.query, keep_blank_values=True) if k not in self.AUTH]
        q += [(k, self.auth[k]) for k in self.AUTH if add and k in self.auth]
        return urllib.parse.urlunsplit(u._replace(query=urllib.parse.urlencode(q)))

    def slim(self, g):
        """The parts of a jeu the name passes read, media URLs without the login: the cache never holds it."""
        if not isinstance(g, dict):
            return {}
        out = {"id": str(g.get("id", "")), "noms": [n for n in g.get("noms") or [] if isinstance(n, dict)],
               "systeme": {"id": str((g.get("systeme") or {}).get("id", ""))}}
        if "medias" in g:
            out["medias"] = [{"type": m.get("type"), "region": m.get("region"), "format": m.get("format"),
                              "url": self.with_auth(str(m.get("url", "")), False)}
                             for m in g.get("medias") or [] if isinstance(m, dict)]
        return out

    def cached(self, rel, ask, endpoint, **params):
        """A jeuRecherche or jeuInfos reply, slimmed and kept under ss/<rel>.json so a rerun never asks again
        (and rules changed later still judge it offline). None when it is not cached and may not be asked:
        no credentials, stopped, a dry run, or ask False. Raises Stop and Fail."""
        p = os.path.join(self.ctx.cache, "ss", rel + ".json")
        try:
            return json.loads(slurp(p, "r"))
        except (OSError, ValueError):
            pass  # not cached yet, or a torn write: ask again
        if not self.ready or self.stop or self.ctx.dry or not ask:
            return None
        self.spend()
        r = (self.call(endpoint, **params) or {}).get("response") or {}
        data = {"jeux": [self.slim(g) for g in r.get("jeux") or []]} if endpoint == "jeuRecherche.php" else \
            {"jeu": self.slim(r.get("jeu"))}
        os.makedirs(os.path.dirname(p), exist_ok=True)
        spit(p, json.dumps(data), "w")
        return data

    def search(self, system, stem, ask=True):
        """{"game", "sysid"} for the one game whose name matches stem (see judge), else {"why", "near"}: the
        best near game (id, name) for --suggest. None when a search was needed and not asked."""
        best = None
        for sysid, query, key, cut in attempts(stem, system):
            data = self.cached(f"search/{sysid}/{zlib.crc32(query.lower().encode()) & 0xffffffff:08x}-{len(query)}",
                               ask, "jeuRecherche.php", systemeid=sysid, recherche=query)
            if data is None:
                return None
            got = judge(data.get("jeux") or [], key, sysid, cut, system)
            if got.get("game"):
                return dict(got, sysid=sysid)
            best = best if best and best.get("near") else got
        return best or {"why": "no title to search", "near": None}

    def game(self, system, gid, sysid, ask=True):
        data = self.cached(f"{system}/game/{gid}", ask, "jeuInfos.php", gameid=gid, systemeid=sysid)
        return None if data is None else data.get("jeu") or {}

    def crc_game(self, system, crc, name, size, ask=True):
        """The CRC path's jeuInfos answer, kept this time, for its box front (--by-name only)."""
        data = self.cached(f"{system}/crc/{crc}", ask, "jeuInfos.php", crc=crc, systemeid=SYSTEMS[system][3],
                           romnom=name + ".bin", romtaille=size or "")
        return None if data is None else data.get("jeu") or {}

    def media(self, system, gid, game, prefer, sysid, ask=True):
        """{kind: (bytes, type used) or None} for the kinds the CRC path takes. A cart label scan nobody has
        falls back to the front box (box-2D, the ROM's region, then wor, us, eu, jp); a wheel or logo never.
        Cached by type and game id. None when the game's media list was needed and not asked."""
        d, out = os.path.join(self.ctx.cache, "ss", system, "name"), {}
        for kind in [k for k, _ in PS1_MEDIA] if system == "PS1" else [MEDIA.get(system, LABEL)]:
            out[kind] = None
            for t, order in [(kind, None)] + ([("box-2D", ("wor", "us", "eu", "jp"))] if kind == LABEL else []):
                png, none = os.path.join(d, t, gid + ".png"), os.path.join(d, t, gid + ".none")
                if os.path.isfile(png):
                    out[kind] = (slurp(png), t)
                    break
                if os.path.isfile(none):
                    continue
                if game is None or "medias" not in game:
                    game = self.game(system, gid, sysid, ask)
                    if game is None:
                        return None
                m = self.pick(game.get("medias") or [], "", t, prefer, order)
                if not m:
                    if not self.ctx.dry:
                        os.makedirs(os.path.dirname(none), exist_ok=True)
                        spit(none, b"")
                    continue
                if self.ctx.dry:
                    out[kind] = (b"", t)
                    break
                out[kind] = (self.download(dict(m, url=self.with_auth(str(m.get("url", "")), True)), png), t)
                break
        return out

    def wheel(self, system, gid, ask=True):
        """--logo-fallback only: the game's wheel (its logo) as PNG bytes (b"" in a dry run), never as a label
        itself. Cached by game id; None when it has none, or its media list was needed and not asked."""
        png = os.path.join(self.ctx.cache, "ss", system, "name", "wheel", gid + ".png")
        if os.path.isfile(png):
            return slurp(png)
        try:
            m = self.pick((self.game(system, gid, SYSTEMS[system][3], ask) or {}).get("medias") or [], "", "wheel")
            if not m or self.ctx.dry:
                return b"" if m else None
            return self.download(dict(m, url=self.with_auth(str(m.get("url", "")), True)), png)
        except Stop as e:
            self.stop = str(e)
            return None

    def pick(self, medias, name, kind=LABEL, prefer=None, order=None):
        tag = re.search(r"\(([^)]*)\)", name)
        own = (self.REGION.get(tag.group(1).split(",")[0].strip()) if tag else None) or prefer
        same = [m for m in medias if m.get("type") == kind]
        # slot decodes PNG only: a media that says it is another format goes last
        same.sort(key=lambda m: str(m.get("format", "png")).lower() != "png")
        for region in [own, *(order or ("us", "wor", "eu", "jp"))]:
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
        SNES without a 512-byte copier header (size % 1024 == 512) then the whole file, a HuCard likewise
        (size % 8192 == 512), a Mega Drive SMD dump (as Genesis Plus GX detects one) de-interleaved, since
        No-Intro hashes the raw ROM. A .lnx without its 64-byte LYNX header first, the way No-Intro and
        Beetle Lynx hash it. A headered .a78 without its 128-byte header too."""
        if system == "Lynx" and self.size > 64 and self.read()[:4] == b"LYNX":
            yield zlib.crc32(self.read()[64:])
        if system == "A7800" and self.size > 128 and self.read()[1:10] == b"ATARI7800":
            yield zlib.crc32(self.read()[128:])
        if system == "SNES" and self.size % 1024 == 512:
            yield zlib.crc32(self.read()[512:])
        if system == "TG16" and self.size % 8192 == 512:
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


def expansion_systems(card):
    """The Games/ folders Config/expansion.txt moves to the Expansion Card (ADR 0098), read as System/expansion.sh
    reads it. On the main card mounted alone, their folders are empty mount points."""
    try:
        text = slurp(os.path.join(card, "Config", "expansion.txt"), "r")
    except OSError:
        return set()
    return {w for line in text.splitlines() for w in line.split("#")[0].split() if w.isascii() and w.isalnum()}


# ---- PICO-8 labels (ADR 0101) --------------------------------------------------------------------

# The 16 colours and the 16 secret ones (128-143), as PICO-8 0.2 draws them; the label digits 0-9, a-v.
PICO8_PALETTE = [bytes.fromhex(c) for c in (
    "000000 1d2b53 7e2553 008751 ab5236 5f574f c2c3c7 fff1e8 ff004d ffa300 ffec27 00e436 29adff 83769c ff77a8 ffccaa "
    "291814 111d35 422136 125359 742f29 49333b a28879 f3ef7d be1250 ff6c24 a8e72e 00b543 065ab5 754665 ff6e59 ff9d81"
).split()]
PICO8_DIGITS = "0123456789abcdefghijklmnopqrstuv"


def pico8_admits(name):
    stem, ext = os.path.splitext(name)
    return ext.lower() != ".png" or stem.lower().endswith(".p8")


def png_rows(data):
    """(width, height, RGBA rows) of an 8-bit RGBA or RGB, non-interlaced PNG, stdlib only."""
    if not data.startswith(PNG):
        raise Fail("not a PNG")
    pos, idat, head = 8, b"", None
    while pos + 8 <= len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body, pos = data[pos + 8:pos + 8 + n], pos + 12 + n
        if kind == b"IHDR":
            head = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            idat += body
    if not head or head[2] != 8 or head[3] not in (2, 6) or head[6] != 0:
        raise Fail("not an 8-bit RGB or RGBA PNG")
    w, h, bpp = head[0], head[1], 4 if head[3] == 6 else 3
    raw, stride, rows, prev, i = zlib.decompress(idat), w * bpp, [], bytearray(w * bpp), 0
    for _ in range(h):
        f, line = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a, b = line[x - bpp] if x >= bpp else 0, prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b) & 255
            elif f == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        prev = line
        rows.append(bytes(line) if bpp == 4 else
                    b"".join(bytes(line[x:x + 3]) + b"\xff" for x in range(0, stride, 3)))
    return w, h, rows


def png_bytes(w, h, rows):
    """An RGBA PNG of rows (bytes of w * 4 each)."""
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
    raw = b"".join(b"\0" + row for row in rows)
    return PNG + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + \
        chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def pico8_label(data):
    """The cart's own 128x128 label as PNG bytes, or None when the cart has none."""
    if data.startswith(PNG):
        w, h, rows = png_rows(data)
        if (w, h) != (160, 205):
            raise Fail(f"a PICO-8 PNG cart is 160x205, this one is {w}x{h}")
        return png_bytes(128, 128, [row[16 * 4:144 * 4] for row in rows[24:152]])
    text = data.decode("latin-1").splitlines()
    if "__label__" not in text:
        return None
    lines = text[text.index("__label__") + 1:][:128]
    if len(lines) < 128 or any(len(l) < 128 for l in lines):
        raise Fail("the __label__ section is shorter than 128 lines of 128 digits")
    rows = []
    for line in lines:
        row = b""
        for d in line[:128].lower():
            if d not in PICO8_DIGITS:
                raise Fail(f"the __label__ section has a {d!r}, not a palette digit")
            row += PICO8_PALETTE[PICO8_DIGITS.index(d)] + b"\xff"
        rows.append(row)
    return png_bytes(128, 128, rows)


def process_pico8(ctx, roms, have, out, args):
    """Labels for PICO-8 carts, from the carts themselves (ADR 0101)."""
    stats = ctx.stats
    for rom in roms:
        stem, tag = rom.stem, f"PICO8/{rom.stem}"
        if args.only_stem and nfc(stem) != nfc(args.only_stem):
            continue
        if f"{stem}.png".lower() in have and not args.force:
            stats["skipped"] += 1
            continue
        if not rom.read:
            stats["unknown"] += 1
            print(f"  unknown  {tag} (not in the library)")
            continue
        stats["matched"] += 1
        try:
            body = pico8_label(rom.read())
        except (Fail, zlib.error, ValueError) as e:
            stats["errors"] += 1
            print(f"  error  {tag}: {e}")
            continue
        if body is None:
            stats["missing"] += 1
            print(f"  missing  {tag} (the cart has no label)")
            continue
        stats["written"] += 1
        note_label(ctx, "PICO8", "", stem)
        ctx.report.append(("PICO8", stem, "written", "cart", "label"))
        if ctx.dry:
            continue
        dest = os.path.join(out, "Labels", "PICO8", stem + ".png")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        spit(dest, body)
    return []


def scan_card(card, system, expansion=None):
    """(roms, collisions) for Games/<SYSTEM>/ on a mounted card, or on the mounted Expansion Card for a system
    Config/expansion.txt lists. Without --expansion such a system is skipped out loud, never read as empty."""
    d = os.path.join(card, "Games", system)
    if system in expansion_systems(card):
        if not expansion:
            print(f"{system}: skipped, Games/{system} is on the Expansion Card (Config/expansion.txt): "
                  f"pass --expansion <its mounted root>, or use --device")
            return [], []
        d = os.path.join(expansion, "Games", system)
    by_stem, clash = {}, set()
    for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        p = os.path.join(d, n)
        if n.startswith(".") or not os.path.isfile(p) or os.path.splitext(n)[1].lower() not in SYSTEMS[system][1]:
            continue
        if system == "PICO8" and not pico8_admits(n):
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
        if system == "PICO8" and not pico8_admits(n):
            continue
        if os.path.splitext(n)[1].lower() in exts:  # an arcade .zip is the romset itself
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


# ---- labels by name (--by-name) --------------------------------------------------------------------

def arcade_titles():
    """{(board, set): full title} from slot's own set table (arcade_sets.tsv in the patched tree), {} when
    neither build/slot nor work/slot is there."""
    global _ARCADE_TITLES
    if _ARCADE_TITLES is None:
        _ARCADE_TITLES = {}
        for path in ARCADE_SETS:
            if os.path.isfile(path):
                for line in slurp(path, "r").splitlines():
                    cols = line.split("\t")
                    if len(cols) == 5:
                        _ARCADE_TITLES[(cols[0], cols[1].lower())] = cols[4]
                break
    return _ARCADE_TITLES


_ARCADE_TITLES = None


def shown_name(stem, system=None):
    """The name a search or a logo is matched on: an arcade set's full title (mslug is Metal Slug - Super
    Vehicle-001), every other ROM's own stem."""
    if system in ARCADE:
        return arcade_titles().get((system, stem.lower()), stem)
    return stem


def bare_title(stem, system=None):
    """The title words of a GoodTools or No-Intro name: no [..] or (..) groups, _ read as a space, and for GBA
    no leading GoodGBA release number (0468 - ...). Other systems keep it: 1943 - The Battle of Midway is a title.
    An arcade set is read as its full title (shown_name)."""
    t = nfc(shown_name(stem, system)).replace("_", " ")
    t = re.sub(r"^\d{4}\s+-\s+", "", t) if system == "GBA" else t
    return " ".join(re.sub(r"\[[^\]]*\]?|\([^)]*\)?", " ", t).split())


def title_key(stem, system=None):
    """bare_title with a leading The or a GoodTools ", The" (". The") dropped, & 'n 'n' n' n read as and,
    accents folded, lowercase letters and digits only, so Brett Hull Hockey 95 (JUE) [b1] and Brett Hull
    Hockey '95 meet, and so do Snake Rattle'n Roll and Snake Rattle 'n' Roll."""
    t = bare_title(stem, system).lower().replace("&", " and ")
    t = re.sub(r"\s*'n'?(?=\s|$)|(?<!\S)n'(?=\s|$)|(?<=\s)n(?=\s)", " and ", t)
    t = re.sub(r"^the\s+|[,.]\s*the(?=\s*(?:$|[-:]))", "", t)
    t = "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", t)


def is_cut(stem, system=None):
    """A name the card cut short (about 40 characters): no tag at all and still 30 characters of title."""
    return not re.search(r"[(\[]", stem) and len(bare_title(stem, system)) >= 30


def attempts(stem, system):
    """(systemeid, query, key, cut) for each name search, in order. The query drops a trailing "by <author>"
    (never the key a match is judged on), and the last word of a cut name. A Mega Drive name with 32X is
    asked first under ScreenScraper's 32X id 19, without the 32X (Gemba/skyscraper ccd49ae,
    platforms_idmap.csv row "sega32x,19,21,33")."""
    title, cut = bare_title(stem, system), is_cut(stem, system)

    def query(t):
        q = re.sub(r"\s+by\s+\S.*$", "", t, flags=re.I) or t
        return q.rsplit(" ", 1)[0] if cut and " " in q else q
    out = []
    if system in ("MD", "32X") and re.search(r"\b32x\b", title, re.I):
        t32 = " ".join(re.sub(r"\b32x\b", " ", title, flags=re.I).split())
        out.append((19, query(t32), title_key(t32, system), cut))
        if system == "32X":
            return [a for a in out if a[2]]
    out.append((SYSTEMS[system][3], query(title), title_key(stem, system), cut))
    return [a for a in out if a[2]]


def judge(games, key, sysid, cut, system):
    """{"game": g} when exactly one game id of system sysid has a name (any region) whose title_key is key,
    or for a cut name starts with key; else {"why", "near": (id, name)} naming the closest name seen."""
    hits, near = {}, (0.0, None, None, "")
    for g in games:
        if not isinstance(g, dict) or not str(g.get("id", "")):
            continue
        other = str((g.get("systeme") or {}).get("id", sysid) or sysid) != str(sysid)
        for n in g.get("noms") or []:
            name = str(n.get("text", "")) if isinstance(n, dict) else ""
            k = title_key(name, system)
            if not k:
                continue
            if not other and (k == key or cut and k.startswith(key)):
                hits.setdefault(str(g["id"]), (g, name))
            score = difflib.SequenceMatcher(None, key, k).ratio()
            if score > near[0]:
                why = "other system" if other else "subtitle differs" if k.startswith(key) or key.startswith(k) \
                    else "name differs"
                near = (score, str(g["id"]), name, why)
    if len(hits) == 1:
        g, name = next(iter(hits.values()))
        return {"game": g, "name": name}
    if hits:
        gid, (g, name) = next(iter(hits.items()))
        return {"why": f"several ids ({', '.join(sorted(hits))})", "near": (gid, name)}
    if near[1]:
        return {"why": near[3], "near": (near[1], near[2])}
    return {"why": "no results", "near": None}


REGION_WORDS = {"USA", "Europe", "Japan", "World", "Brazil", "Korea", "Asia", "Australia"}


def region_tags(stem):
    """The regions a name carries: regions() reads GoodTools J, U, E; W is World here only, since
    regions() mirrors slot's own nes.rs reading."""
    r = regions(stem)
    return (r | {"World"} if "W" in r else r) & REGION_WORDS


def dump_rank(stem):
    """2 for a verified [!] dump, 1 for a plain one, 0 for a bad dump, hack, pirate, trainer, fix or translation."""
    return 0 if re.search(r"\[[bhptf]", stem, re.I) else 2 if "[!]" in stem else 1


def pick_sibling(stem, names):
    """The label file name to copy: most shared regions, then the cleanest dump, then by name."""
    own = region_tags(stem)
    return min(names, key=lambda n: (-len(own & region_tags(n)), -dump_rank(n), n))


def is_hack(stem):
    """A GoodTools [h..] or a name saying hack: it gets a parent's logo only through --aliases."""
    return bool(re.search(r"\[h|\bhack\b", stem, re.I))


def logo_index(ctx, system):
    """{title_key: [names]} of libretro-thumbnails Named_Logos for system, {} when it has none. libretro writes
    & (and : / ? and the like) as _, so a name with _ is also keyed with & read back."""
    dat = ARCADE_THUMBS if system in ARCADE else (SYSTEMS[system][2] or ["Sony - PlayStation"])[0]
    text = cached_text(ctx, f"logos/{dat}.html", LOGOS + urllib.parse.quote(dat) + "/Named_Logos/", 30 * DAY,
                       optional=True)
    index = {}
    for href in re.findall(r'href="([^"?/]+\.png)"', text):
        name = nfc(urllib.parse.unquote(href)[:-4])
        for k in {title_key(name, system), title_key(name.replace("_", "&"), system)} - {""}:
            index.setdefault(k, []).append(name)
    return index


def pick_logo(index, stem, system):
    """The logo name whose title_key is stem's (the best region, then by name), or for a cut name the one key
    starting with it. None when there is none or several keys could be meant: never a guess."""
    key = title_key(stem, system)
    names = index.get(key) if key else None
    if not names and key and is_cut(stem, system):
        keys = [k for k in index if k.startswith(key)]
        names = index[keys[0]] if len(keys) == 1 else None
    return pick_sibling(stem, names) if names else None


def logo_png(ctx, system, name):
    """A Named_Logos PNG, cached under logos/<system>/; b"" in a dry run when not cached; None when missing."""
    p = os.path.join(ctx.cache, "logos", system, name + ".png")
    if os.path.isfile(p):
        return slurp(p)
    if ctx.dry:
        return b""
    dat = ARCADE_THUMBS if system in ARCADE else (SYSTEMS[system][2] or ["Sony - PlayStation"])[0]
    status, body = fetch(ctx, LOGOS + urllib.parse.quote(f"{dat}/Named_Logos/{name}.png"))
    if status != 200 or not body.startswith(PNG):
        return None
    os.makedirs(os.path.dirname(p), exist_ok=True)
    spit(p, body)
    return body


def render_logo(system, stem, logo):
    """The Logo Only label PNG for stem, from the slot-ui example (SLOT_LOGO_LABEL overrides its path)."""
    with tempfile.TemporaryDirectory() as d:
        src, out = os.path.join(d, "logo.png"), os.path.join(d, "label.png")
        spit(src, logo)
        r = subprocess.run([os.environ.get("SLOT_LOGO_LABEL") or LOGO_TOOL, system, stem, src, out],
                           capture_output=True, text=True)
        if r.returncode or not os.path.isfile(out):
            raise Fail(f"logo_label failed: {r.stderr.strip()}")
        return slurp(out)


def note_label(ctx, system, sub, stem):
    """Record a label that is now on the card (or will be, in a dry run) so a later ROM can copy it."""
    ctx.labels.setdefault(sub, set()).add(f"{stem}.png".lower())
    if not sub:
        ctx.sib.setdefault(title_key(stem, system), []).append(stem + ".png")


def sibling_png(ctx, system, sub, fname, root, args):
    """A label already on the card: read off the card, or this run's stage, or (--device) the cache, or
    pulled from the device into the cache (never into the stage, which is pushed whole)."""
    local = os.path.join(root, "Labels", system, sub, fname)
    if os.path.isfile(local):
        return slurp(local)
    if not ctx.dev:
        return None
    stem = os.path.splitext(fname)[0]
    rom = ctx.lib.get(nfc(stem))
    if rom and not sub and system != "PS1":
        crc = resolve(system, rom, ctx.dat, ctx.art)
        kind = MEDIA.get(system, LABEL)
        for p in ([os.path.join(ctx.cache, "art", ctx.art[crc])] if crc in ctx.art else []) + \
                ([os.path.join(ctx.cache, "ss", system, *([kind] if kind != LABEL else []), crc + ".png")] if crc else []):
            if os.path.isfile(p):
                return slurp(p)
    pulled = os.path.join(ctx.cache, "device", system, sub, fname)
    if not os.path.isfile(pulled):
        os.makedirs(os.path.dirname(pulled), exist_ok=True)
        rc, _ = ctx.dev.run("pull", "/".join(x for x in (args.sd, "Labels", system, sub, fname) if x), pulled)
        if rc != 0 or not os.path.isfile(pulled):
            return None
    return slurp(pulled)


def shell_value(ctx, args, stem):
    """The cart_shell.txt value for stem: this run's, else the existing file's (read once)."""
    if stem in ctx.shell:
        return ctx.shell[stem]
    if ctx.shell_have is None:
        text = ""
        if ctx.dev:
            if "cart_shell.txt" in ctx.dev.names(f"{args.sd}/Labels"):
                local = os.path.join(ctx.stage, "cart_shell.have")
                rc, _ = ctx.dev.run("pull", f"{args.sd}/Labels/cart_shell.txt", local)
                text = slurp(local, "r") if rc == 0 and os.path.isfile(local) else ""
        elif os.path.isfile(os.path.join(args.card, "Labels", "cart_shell.txt")):
            text = slurp(os.path.join(args.card, "Labels", "cart_shell.txt"), "r")
        ctx.shell_have = {nfc(e[0]): e[1] for e in map(shell_entry, text.splitlines()) if e}
    return ctx.shell_have.get(nfc(stem))


STATS = {"alias": "alias", "sibling": "sibling", "crc box": "crc_box", "name": "by_name",
         "name, no art": "name_no_art", "no confident match": "no_match", "not searched": "name_skipped",
         "logo fallback": "logo", "error": "errors"}
LINES = {"alias": "matched by alias", "sibling": "matched by sibling", "crc box": "matched by CRC, box front",
         "name": "matched by name", "name, no art": "matched by name, no art", "not searched": "not searched by name"}
# the outcomes that leave a ROM bare, where --logo-fallback steps in
BARE = {"name, no art", "no confident match", "not searched"}


def by_name(ctx, system, left, root, args):
    """For each (stem, subs, crc) the CRC path left without a label, in order: a --aliases entry, a same-title
    sibling's label, the front box of the game the CRC found (crc is (crc, dat name, size) when it found one
    with no label scan), then a ScreenScraper search by name. subs: the Labels sub-folders still missing
    ('' and, for PS1, 'disc'). Each ROM gets one outcome line and report row; --suggest rows for the rest."""
    stats, asked = ctx.stats, [0]
    pairs = {kind: sub for kind, sub in PS1_MEDIA} if system == "PS1" else {MEDIA.get(system, LABEL): ""}
    sysid = SYSTEMS[system][3]
    cur, logos = {}, []

    def done(stem, outcome, source="", media=""):
        # a ROM skipped for quota, a stop or --limit is not bare: a later run still searches it by name
        skipped_now = outcome == "not searched" and source not in ("dry run", "no SS_DEVID/SS_DEVPASSWORD")
        if args.logo_fallback and outcome in BARE and not skipped_now and "" in cur["subs"]:
            got = logo(stem, source)
            if got:
                outcome, source, media = "logo fallback", got, "logo"
        stats[STATS[outcome]] += 1
        ctx.report.append((system, stem, outcome, source, media))
        print(f"  {LINES.get(outcome, outcome)}  {system}/{stem}" + (f" ({source}{', ' + media if media else ''})" if source else ""))

    def put(stem, sub, body):
        if not ctx.dry:
            dest = os.path.join(root, "Labels", system, sub, stem + ".png")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            spit(dest, body)
        note_label(ctx, system, sub, stem)

    def write(stem, subs, media):
        used = []
        for kind, sub in pairs.items():
            if sub in subs and media.get(kind):
                put(stem, sub, media[kind][0])
                used.append(media[kind][1])
        return "+".join(used)

    def copy(stem, subs, fname):
        """Copy the sibling label fname (and its disc label, its cart_shell line). True when one was written."""
        sib, wrote, own = os.path.splitext(fname)[0], False, region_tags(stem)
        for sub in subs:
            if sub and fname.lower() not in ctx.labels.get(sub, set()):
                continue
            try:
                body = b"" if ctx.dry else sibling_png(ctx, system, sub, fname, root, args)
            except (Fail, OSError) as e:
                body = None
                print(f"  could not read sibling {system}/{fname}: {e}")
            if body is not None and (ctx.dry or body.startswith(PNG)):
                put(stem, sub, body)
                wrote = True
        value = shell_value(ctx, args, sib) if wrote and system in ("NES", "SNES", "MD") else None
        if value and (not own or own & region_tags(sib)):
            ctx.shell[stem] = value
        return wrote

    def logo(stem, source):
        """Write a Logo Only label for a ROM every other pass left bare; returns its source or "". The logo is
        libretro's Named_Logos by the ROM's title (or an alias's sibling title), else the ScreenScraper wheel of
        the game the name pass (or an ss: alias) found. A hack takes a logo only through an alias."""
        how, _, target = ctx.aliases.get((system, nfc(stem)), "").partition(":")
        auto = not is_hack(stem)
        try:
            if not logos:
                logos.append(logo_index(ctx, system))
            name = pick_logo(logos[0], target if how == "sibling" else stem, system) if auto or how == "sibling" \
                else None
            gid = target if how == "ss" else source[3:] if auto and source.startswith("ss:") else ""
            body, src = (logo_png(ctx, system, name), f"libretro:{name}") if name else \
                (ctx.ss.wheel(system, gid, ask()), f"ss:{gid} wheel") if gid else (None, "")
        except Fail as e:
            print(f"  no logo for {system}/{stem}: {e}")
            body = None
        if body is None:
            return ""
        put(stem, "", b"" if ctx.dry else ctx.render(system, stem, body))
        return src

    def ask():
        return not (args.limit and asked[0] >= args.limit)

    def skipped(stem):
        why = "dry run" if ctx.dry else ctx.ss.stop or ("no SS_DEVID/SS_DEVPASSWORD" if not ctx.ss.ready
                                                          else f"--limit {args.limit}")
        done(stem, "not searched", why)
        return why

    def one(stem, subs, crc):
        key, own = title_key(stem, system), region_tags(stem)
        prefer = next((ScreenScraper.REGION[r] for r in ScreenScraper.REGION if r in own), None)
        alias = ctx.aliases.get((system, nfc(stem)))
        if alias:
            how, _, target = alias.partition(":")
            if how == "sibling":
                fname = next((n for n in ctx.sib.get(title_key(target, system), [])
                              if n.lower() == f"{target}.png".lower()), target + ".png")
                if copy(stem, subs, fname):
                    return done(stem, "alias", alias)
            else:
                media = ctx.ss.media(system, target, None, prefer, sysid, ask())
                if media is None:
                    return skipped(stem)
                used = write(stem, subs, media)
                if used:
                    return done(stem, "alias", alias, used)
            print(f"  alias {alias} gave no label for {system}/{stem}, trying the other passes")
        own_png = f"{stem}.png".lower()
        names = [n for n in ctx.sib.get(key, []) if n.lower() != own_png]
        sib_near = None
        if key and not names and is_cut(stem, system):
            keys = sorted(k for k in ctx.sib if k != key and k.startswith(key))
            if len(keys) == 1:
                names = [n for n in ctx.sib[keys[0]] if n.lower() != own_png]
            elif keys:
                sib_near = (pick_sibling(stem, ctx.sib[keys[0]]), f"several siblings ({len(keys)} titles)")
        if key and names:
            best = pick_sibling(stem, names)
            if copy(stem, subs, best):
                return done(stem, "sibling", os.path.splitext(best)[0])
        if crc and pairs.get(LABEL) == "":
            game = ctx.ss.crc_game(system, crc[0], crc[1] or stem, crc[2], ask())
            media = ctx.ss.media(system, game["id"], game, prefer, sysid, ask()) if game and game.get("id") else None
            used = write(stem, subs, media) if media else ""
            if used:
                return done(stem, "crc box", f"crc:{crc[0]}", used)
        old = os.path.join(ctx.cache, "ss", system, "name", key + ".id")  # a round 1 match, kept
        gid = slurp(old, "r").strip() if key and os.path.isfile(old) else ""
        found = {"game": {"id": gid}, "sysid": sysid} if gid else ctx.ss.search(system, stem, ask())
        if found is None:
            return suggest(stem, key, {"why": f"not searched ({skipped(stem)})", "near": None}, sib_near)
        if found.get("game"):
            gid = str(found["game"]["id"])
            media = ctx.ss.media(system, gid, found["game"], prefer, found["sysid"], ask())
            if media is None:
                return suggest(stem, key, {"why": f"not searched ({skipped(stem)})", "near": None}, sib_near)
            used = write(stem, subs, media)
            done(stem, "name" if used else "name, no art", f"ss:{gid}", used)
            if not used:
                suggest(stem, key, {"why": "no label or box front", "near": (gid, found.get("name", ""))}, None)
            return
        done(stem, "no confident match")
        suggest(stem, key, found, sib_near)

    def suggest(stem, key, found, sib_near):
        if not args.suggest:
            return
        hack = "hack or bad dump; " if dump_rank(stem) == 0 or re.search(r"hack", stem, re.I) else ""
        if found.get("near"):
            gid, name = found["near"]
            return ctx.suggest.append((system, stem, f"ss:{gid}", name, hack + found["why"]))
        if not sib_near and key:
            close = difflib.get_close_matches(key, list(ctx.sib), 1, 0.8)
            if close:
                sib_near = (pick_sibling(stem, ctx.sib[close[0]]), "title differs")
        if sib_near:
            sib = os.path.splitext(sib_near[0])[0]
            return ctx.suggest.append((system, stem, f"sibling:{sib}", sib, hack + sib_near[1] + "; " + found["why"]))
        ctx.suggest.append((system, stem, "", "", hack + found["why"]))

    for stem, subs, crc in left:
        before, cur["subs"] = ctx.ss.asked, subs
        try:
            one(stem, subs, crc)
        except Stop as e:  # quota or refusal mid-search: stop asking, like the CRC path; the next run resumes
            ctx.ss.stop = str(e)
            done(stem, "not searched", ctx.ss.stop)
        except (Fail, OSError) as e:
            done(stem, "error", str(e))
        finally:
            asked[0] += ctx.ss.asked > before


def load_aliases(path):
    """{(system, stem): "ss:<id>" or "sibling:<stem>"} from a system<TAB>stem<TAB>target TSV. A --suggest file
    works as is: its header, # lines and rows with no candidate are skipped, its quoting is read."""
    out = {}
    with open(path, encoding="utf-8", newline="") as f:
        for n, row in enumerate(csv.reader(f, delimiter="\t"), 1):
            if not row or row[0].startswith("#") or row[0] == "system" or len(row) < 3 or not row[2].strip():
                continue
            if row[0].upper() not in SYSTEMS or not re.fullmatch(r"ss:\d+|sibling:.+", row[2].strip()):
                sys.exit(f"--aliases line {n}: want system<TAB>stem<TAB>ss:<game id> or sibling:<stem>")
            out[(row[0].upper(), nfc(row[1]))] = row[2].strip()  # the stem unstripped: a cut one may end in a space
    return out


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
        # --by-name state: per system label listings and title index, and the run's report rows
        self.labels, self.sib, self.lib, self.dat, self.dev, self.stage = {}, {}, {}, None, None, None
        self.shell_have, self.report, self.suggest, self.aliases = None, [], [], {}
        self.render = render_logo  # --logo-fallback's renderer, a seam for the tests


def ss_id(system, rom):
    """ScreenScraper system id for one ROM: a Neo Geo Pocket Color cart (header byte 0x23 is 0x10, the
    byte Beetle NeoPop reads) asks under ngpc 82, everything else as system_id says."""
    if system == "NGP":
        head = rom.read()[:0x24]
        if len(head) == 0x24 and head[0x23] == 0x10:
            return NGP_COLOR_ID
    return system_id(system, rom)


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
    return ctx.ss.label(system, crc, name or rom.stem, rom.size, ss_id(system, rom))


def system_id(system, rom):
    """ScreenScraper's system id for one ROM: WonderSwan Color for a WonderSwan ROM whose footer colour flag
    (16 bytes from the end, byte 7) is set, else the shelf's own id."""
    if system != "WS":
        return SYSTEMS[system][3]
    data = rom.read()
    return WS_COLOR_ID if len(data) >= 16 and data[-9] else SYSTEMS[system][3]


def process(ctx, system, roms, have, out, dat, args):
    """Labels by CRC. Returns the (stem, subs) left without one, for the --by-name pass."""
    stats, tried, kept, left = ctx.stats, 0, 0, []
    for rom in roms:
        stem, tag = rom.stem, f"{system}/{rom.stem}"
        if args.only_stem and nfc(stem) != nfc(args.only_stem):
            continue
        if f"{stem}.png".lower() in have and not args.force:
            stats["skipped"] += 1
            kept += 1
            continue
        # a ROM with no read is on the device but not in --library (only passed in with --by-name)
        crc = resolve(system, rom, dat, ctx.art) if rom.read else dat.by_name.get(nfc(stem))
        if crc is None:
            stats["unknown"] += 1
            print(f"  unknown CRC  {tag}" + ("" if rom.read else " (not in the library)"))
            left.append((stem, [""], None))
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
            left.append((stem, [""], (crc, name, rom.size)))
            continue
        stats["written"] += 1
        note_label(ctx, system, "", stem)
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
    return left


def process_arcade(ctx, system, roms, have, out, args):
    """Labels for arcade sets by set name (ADR 0099). Returns the (stem, subs, None) left without one, for the
    --by-name pass, which searches by the set's full title."""
    stats, tried, left = ctx.stats, 0, []
    for rom in roms:
        stem, tag = rom.stem, f"{system}/{rom.stem}"
        if args.only_stem and nfc(stem) != nfc(args.only_stem):
            continue
        if f"{stem}.png".lower() in have and not args.force:
            stats["skipped"] += 1
            continue
        if (system, stem.lower()) not in arcade_titles() and arcade_titles():
            stats["unknown"] += 1
            print(f"  unknown set  {tag} (not a {system} set of the pinned FinalBurn Neo)")
            continue
        if args.limit and tried >= args.limit:
            break
        tried += 1
        stats["matched"] += 1
        try:
            body = ctx.ss.arcade_label(system, rom)
        except Fail as e:
            stats["errors"] += 1
            print(f"  error  {tag}: {e}")
            continue
        if body is None:
            stats["missing"] += 1
            why = f", ScreenScraper stopped: {ctx.ss.stop}" if ctx.ss.stop else ""
            print(f"  missing  {tag} ({shown_name(stem, system)}{why})")
            left.append((stem, [""], None))
            continue
        stats["written"] += 1
        note_label(ctx, system, "", stem)
        if ctx.dry:
            continue
        dest = os.path.join(out, "Labels", system, stem + ".png")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        spit(dest, body)
    return left


def process_ps1(ctx, roms, have, have_disc, out, args):
    """Cover and disc for each PlayStation game. A game is skipped when both are on the card (unless --force)."""
    stats, tried, left = ctx.stats, 0, []
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
            left.append((stem, [sub for (_, sub), g in zip(PS1_MEDIA, got) if args.force or not g], None))
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
        wrote, lack = False, []
        for (kind, sub), exists in zip(PS1_MEDIA, got):
            body = media.get(kind)
            if exists and not args.force:
                continue
            if body is None:
                stats["missing"] += 1
                why = f", ScreenScraper stopped: {ctx.ss.stop}" if ctx.ss.stop else ""
                print(f"  missing  {tag} {kind} ({ident['serial'] or 'CRC ' + (ident['crc'] or 'not hashed')}{why})")
                lack.append(sub)
                continue
            stats["written"] += 1
            note_label(ctx, "PS1", sub, stem)
            wrote = True
            if ctx.dry:
                continue
            dest = os.path.join(out, "Labels", "PS1", sub, stem + ".png")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            spit(dest, body)
        if lack:
            left.append((stem, lack, None))
        if not wrote and ctx.ss.stop:
            break
    return left


def summary(ctx, args):
    s = ctx.stats
    print("\n" + ("DRY RUN, nothing written. " if ctx.dry else "") + "Summary")
    for key, label in [("matched", "matched (CRC known)"), ("written", "would write" if ctx.dry else "written"),
                       ("skipped", "skipped (label exists)"), ("missing", "missing (no art found)"),
                       ("unknown", "unknown CRC"), ("errors", "errors"), ("collisions", "stem collisions"),
                       ("shell_added", "cart_shell lines added"), ("shell_kept", "cart_shell lines kept")]:
        print(f"  {label:<26}{s[key]}")
    if args.by_name:
        for key, label in [("alias", "matched by alias"), ("sibling", "matched by sibling"),
                           ("crc_box", "matched by CRC, box front"), ("by_name", "matched by name"),
                           ("name_no_art", "matched by name, no art"), ("no_match", "no confident match"),
                           ("name_skipped", "not searched by name")] + \
                [("logo", "logo fallback")] * bool(args.logo_fallback):
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
    ctx.dev, ctx.stage = dev, stage
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
                    if system == "PICO8" and not pico8_admits(n):
                        continue
                    stems.setdefault(nfc(stem), []).append(stem)
                for k, group in stems.items():
                    if len(group) > 1:
                        ctx.stats["collisions"] += 1
                        print(f"  collision  {system}/{group[0]} has {len(group)} files, nothing written")
                    elif k in lib:
                        src = lib[k]
                        roms.append(Rom(group[0], src.size, src.read, src.zip_crc, src.path))
                    elif args.by_name or system in ARCADE:
                        roms.append(Rom(group[0], 0, None))  # no CRC: an arcade set is asked by name, and the sibling and name passes need none
                    else:
                        ctx.stats["unknown"] += 1
                        print(f"  unknown CRC  {system}/{group[0]} (not in the library)")
                print(f"{system}: {len(names)} on the device, {len(lib)} in the library" +
                      (f", {len(bad)} bad zips" if bad else ""))
            else:
                roms, clash = scan_card(args.card, system, args.expansion)
                for k in clash:
                    ctx.stats["collisions"] += 1
                    print(f"  collision  {system}/{k} has two extensions, nothing written")
                have_list = os.listdir(os.path.join(args.card, "Labels", system)) \
                    if os.path.isdir(os.path.join(args.card, "Labels", system)) else []
                disc_dir = os.path.join(args.card, "Labels", system, "disc")
                disc_list = os.listdir(disc_dir) if system == "PS1" and os.path.isdir(disc_dir) else []
                print(f"{system}: {len(roms)} ROMs on the card")
                lib = {}
            have = {n.lower() for n in have_list}
            ctx.labels, ctx.sib, ctx.lib, ctx.dat = {"": set(have), "disc": {n.lower() for n in disc_list}}, {}, lib, dat
            for n in have_list:
                if n.lower().endswith(".png") and not n.startswith("."):
                    ctx.sib.setdefault(title_key(n[:-4], system), []).append(n)
            if system == "PS1":
                left = process_ps1(ctx, roms, have, {n.lower() for n in disc_list}, root, args)
            elif system == "PICO8":
                left = process_pico8(ctx, roms, have, root, args)
            elif system in ARCADE:
                left = process_arcade(ctx, system, roms, have, root, args)
            else:
                left = process(ctx, system, roms, have, root, dat, args)
            if args.by_name:
                by_name(ctx, system, left, root, args)
            if dev and not ctx.dry and os.path.isdir(os.path.join(stage, "Labels", system)):
                dev.push(os.path.join(stage, "Labels", system), f"{args.sd}/Labels/{system}")
        if ctx.shell:
            finish_shell(ctx, args, dev, stage)
    finally:
        if stage:
            shutil.rmtree(stage, ignore_errors=True)
    summary(ctx, args)
    for path, head, rows in ((args.report, ("system", "stem", "outcome", "source", "media"), ctx.report),
                             (args.suggest, ("system", "stem", "candidate", "name", "why not"), ctx.suggest)):
        if path:
            with open(path, "w", encoding="utf-8", newline="") as f:
                csv.writer(f, delimiter="\t", lineterminator="\n").writerows([head, *rows])
            print(f"  {len(rows)} row(s) in {path}")
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
    ap.add_argument("--only", help="one system (GBA, GB, GBC, NES, SNES, GG, SMS, MD, PS1, TG16, WS, Lynx, NGP, 32X, A2600, A7800, VB, NEOGEO, CPS1, CPS2, PICO8) or one ROM stem")
    ap.add_argument("--dry-run", action="store_true", help="report what would happen; write and push nothing")
    ap.add_argument("--force", action="store_true", help="replace labels and cart_shell lines that already exist")
    ap.add_argument("--limit", type=int, default=0, help="per system, stop after N matched ROMs (smoke test)")
    ap.add_argument("--by-name", action="store_true",
                    help="a ROM still without a label copies a same-title sibling's, else is searched by name")
    ap.add_argument("--report", help="write a TSV of the --by-name outcomes (system, stem, outcome, source, media)")
    ap.add_argument("--suggest", help="with --by-name, write a TSV of the nearest candidate for each ROM still "
                                      "without a label and why it was not taken (no art is written from it)")
    ap.add_argument("--expansion", help="with --card, the mounted Expansion Card root, for the systems "
                                        "Config/expansion.txt lists (labels still go to --card)")
    ap.add_argument("--aliases", help="with --by-name, a TSV of system, stem, ss:<game id> or sibling:<stem> "
                                      "that forces those matches")
    ap.add_argument("--logo-fallback", action="store_true",
                    help="with --by-name, a ROM still without a label gets its logo on a generated ground "
                         "(libretro Named_Logos, or the ScreenScraper wheel of a game matched by name)")
    args = ap.parse_args(argv)
    if bool(args.card) == args.device:
        ap.error("give exactly one of --card or --device")
    if args.device and not (args.library and os.path.isdir(os.path.expanduser(args.library))):
        ap.error("--device needs --library <folder>")
    if args.card and not os.path.isdir(os.path.expanduser(args.card)):
        ap.error(f"--card not found: {args.card}")
    args.card = os.path.abspath(os.path.expanduser(args.card)) if args.card else None
    args.expansion = os.path.abspath(os.path.expanduser(args.expansion)) if args.expansion else None
    args.library = os.path.abspath(os.path.expanduser(args.library)) if args.library else None
    args.only_system = args.only_stem = None
    if args.only:
        system = next((s for s in SYSTEMS if s.upper() == args.only.upper()), None)
        if system:
            args.only_system = system
        else:
            args.only_stem = args.only
    if (args.suggest or args.aliases or args.logo_fallback) and not args.by_name:
        ap.error("--suggest, --aliases and --logo-fallback need --by-name")
    ctx = ctx or Ctx(dry=args.dry_run)
    tool = os.environ.get("SLOT_LOGO_LABEL") or LOGO_TOOL
    if args.logo_fallback and not args.dry_run and ctx.render is render_logo and not os.access(tool, os.X_OK):
        ap.error(f"--logo-fallback needs the renderer at {tool}: run task labels:logo-tool")
    ctx.dry = args.dry_run
    ctx.aliases = load_aliases(os.path.expanduser(args.aliases)) if args.aliases else {}
    try:
        return run(args, ctx)
    except KeyboardInterrupt:
        print("\nstopped by hand; what was fetched is cached and pushed work is kept")
        sys.exit(130)


if __name__ == "__main__":
    main()
    sys.exit(0)
