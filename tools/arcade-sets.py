#!/usr/bin/env python3
"""Write the Neo Geo, CPS1 and CPS2 set table slot reads, from the pinned FBNeo source (ADR 0097).

    python3 tools/arcade-sets.py vendor/fbneo-src.tar.gz > build/arcade-sets.tsv
    python3 tools/arcade-sets.py build/fbneo-host/FBNeo-<commit> --all   # every field, for the romset audit

The table is one line per set the pinned core runs: board, short name, parent, flags, title. It comes from the
BurnDriver structs in d_neogeo.cpp, d_cps1.cpp and d_cps2.cpp, the same source the core is built from, so a
set the pinned core does not know is never named. Sets the core's full driverlist.h compiles only under
FBNEO_DEBUG are left out, and so are BIOS sets (BDF_BOARDROM) and the Neo Geo system drivers (neogeo, ng_mv*, neocdz): they are never games on a shelf.

Flags: v vertical, c clone, b bootleg, h hack, p prototype, d demo or homebrew, w not working.
"""
import re
import sys
import tarfile

BOARDS = [
    ("NEOGEO", "src/burn/drv/neogeo/d_neogeo.cpp"),
    ("CPS1", "src/burn/drv/capcom/d_cps1.cpp"),
    ("CPS2", "src/burn/drv/capcom/d_cps2.cpp"),
]
DRIVERLIST = "src/dep/generated/driverlist.h"

BDF = {
    "BDF_GAME_WORKING": 1 << 0,
    "BDF_ORIENTATION_FLIPPED": 1 << 1,
    "BDF_ORIENTATION_VERTICAL": 1 << 2,
    "BDF_BOARDROM": 1 << 3,
    "BDF_CLONE": 1 << 4,
    "BDF_BOOTLEG": 1 << 5,
    "BDF_PROTOTYPE": 1 << 6,
    "BDF_HACK": 1 << 7,
    "BDF_HOMEBREW": 1 << 8,
    "BDF_DEMO": 1 << 9,
}

STRUCT = re.compile(r"struct\s+BurnDriver\s+(\w+)\s*=\s*\{(.*?)\};", re.S)


def fields(body):
    out, cur, i, depth = [], [], 0, 0
    while i < len(body):
        ch = body[i]
        if ch == '"':
            j = i + 1
            while body[j] != '"':
                j += 2 if body[j] == "\\" else 1
            cur.append(body[i : j + 1])
            i = j + 1
            continue
        if ch == "/" and body[i : i + 2] == "//":
            i = body.index("\n", i)
            continue
        if ch == "/" and body[i : i + 2] == "/*":
            i = body.index("*/", i) + 2
            continue
        if ch in "({":
            depth += 1
        elif ch in ")}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    if "".join(cur).strip():
        out.append("".join(cur).strip())
    return out


def text(field):
    if field in ("NULL", "0"):
        return ""
    parts = re.findall(r'"((?:[^"\\]|\\.)*)"', field)
    s = "".join(parts)
    s = s.split("\\0")[0]
    return bytes(s, "latin-1").decode("unicode_escape")


def flag_bits(field, table):
    bits = 0
    for word in re.findall(r"[A-Z_0-9]+", field):
        bits |= table.get(word, 0)
    return bits


def debug_only(driverlist):
    hidden, inside = set(), False
    for line in driverlist.splitlines():
        s = line.strip()
        if s.startswith("#if") and "FBNEO_DEBUG" in s:
            inside = True
        elif s.startswith("#endif"):
            inside = False
        elif inside:
            hidden.update(re.findall(r"BurnDrv\w+", s))
    return hidden


def sets(src):
    if src.endswith(".tar.gz"):
        with tarfile.open(src) as t:
            names = {m.name.split("/", 1)[1]: m for m in t.getmembers() if "/" in m.name}
            read = {p: t.extractfile(names[p]).read().decode("latin-1") for p in [DRIVERLIST] + [b[1] for b in BOARDS]}
    else:
        read = {p: open(f"{src}/{p}", encoding="latin-1").read() for p in [DRIVERLIST] + [b[1] for b in BOARDS]}
    hidden = debug_only(read[DRIVERLIST])
    rows = []
    for board, path in BOARDS:
        for name, body in STRUCT.findall(read[path]):
            if name in hidden:
                continue
            f = fields(body)
            flags = flag_bits(f[13], BDF)
            if flags & BDF["BDF_BOARDROM"]:
                continue
            if text(f[0]) in ("neogeo", "neocdz") or text(f[0]).startswith("ng_mv"):
                continue
            marks = ""
            marks += "v" if flags & BDF["BDF_ORIENTATION_VERTICAL"] else ""
            marks += "c" if flags & BDF["BDF_CLONE"] else ""
            marks += "b" if flags & BDF["BDF_BOOTLEG"] else ""
            marks += "h" if flags & BDF["BDF_HACK"] else ""
            marks += "p" if flags & BDF["BDF_PROTOTYPE"] else ""
            marks += "d" if flags & (BDF["BDF_DEMO"] | BDF["BDF_HOMEBREW"]) else ""
            marks += "" if flags & BDF["BDF_GAME_WORKING"] else "w"
            genre = " ".join(g[4:].lower() for g in re.findall(r"GBF_[A-Z_]+", f[16]))
            rows.append(
                {
                    "board": board,
                    "name": text(f[0]),
                    "parent": text(f[1]),
                    "flags": marks or "-",
                    "year": text(f[4]),
                    "title": text(f[5]),
                    "maker": text(f[7]),
                    "genre": genre or "-",
                    "size": "x".join(f[-4:-2]),
                }
            )
    rows.sort(key=lambda r: (r["board"], r["name"]))
    return rows


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    full = "--all" in argv[2:]
    for r in sets(argv[1]):
        cols = ["board", "name", "parent", "flags", "title"]
        if full:
            cols = ["board", "name", "parent", "flags", "year", "maker", "genre", "size", "title"]
        print("\t".join(r[c] or "-" for c in cols))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
