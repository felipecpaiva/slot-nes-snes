#!/usr/bin/env python3
"""Render docs/UPSTREAM-TOUCHPOINTS.md from the net diff of the patch set against the pinned release.

    touchpoints.py DIFF PATCHFILES OLD_MAP OUT

DIFF is `git diff -U0 --no-renames --diff-filter=MD` of the patched tree against the pinned release.
PATCHFILES has one "<patch name>\t<path>" line per file each patch touches.
OLD_MAP is the committed map; its "Why" cells are carried over to the new hunks.

A hunk is identified by its file, the function context git prints after @@, the first upstream
line it changes and a short hash of its changed lines. Upstream line numbers only move on a rebase,
never when a patch adds or drops a hunk elsewhere in the file, so a reason first follows its exact
(file, context, upstream start). Rows left over after that are matched within the same
(file, context) group: by a hash only one leftover row and one new hunk share (a hunk the rebase
moved but did not change), then by one offset that every leftover old row shares, when there are at
least two of them (a rebase that moved changed hunks together). A lone dropped hunk and a lone new
one in the same context look exactly like one moved hunk, so they are never paired. Anything left
is "TODO: explain", naming the reasons it could have been, never a guess.
New hunks get "TODO: explain"; diffsurface:check fails until every row has a reason.
"""
import hashlib
import re
import sys

TODO = "TODO: explain"
HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@ ?(.*)$")


def esc(s):
    return s.replace("|", "\\|").strip()


def hunks(diff):
    out, path, cur = [], None, None
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            path = line.split(" b/", 1)[1]
            cur = None
        elif line.startswith("@@"):
            m = HUNK.match(line)
            start, count = int(m.group(1)), int(m.group(2) or "1")
            cur = {"file": path, "start": start, "count": count, "ctx": esc(m.group(5)), "add": 0, "del": 0, "body": []}
            out.append(cur)
        elif cur is not None and line[:1] == "+" and not line.startswith("+++"):
            cur["add"] += 1
            cur["body"].append(line)
        elif cur is not None and line[:1] == "-" and not line.startswith("---"):
            cur["del"] += 1
            cur["body"].append(line)
    for r in out:
        r["hash"] = hashlib.sha1("\n".join(r.pop("body")).encode()).hexdigest()[:8]
    return out


def old_rows(text):
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
        if len(cells) != 6 or cells[0] in ("File", "---") or cells[5].startswith("TODO"):
            continue
        start = re.match(r"\d+", cells[2])
        if not start:
            continue
        ctx = "" if cells[4] == "(top of file)" else cells[4]
        tail = cells[1].rsplit("#", 1)[-1]
        digest = tail if re.fullmatch(r"[0-9a-f]{8}", tail) else None
        rows.append({"file": cells[0].strip("`"), "ctx": ctx, "start": int(start.group()), "hash": digest, "why": cells[5]})
    return rows


def assign(rows, old):
    for r in rows:
        r["why"] = None
    exact = {(o["file"], o["ctx"], o["start"]): o for o in old}
    used = set()
    for r in rows:
        o = exact.get((r["file"], r["ctx"], r["start"]))
        if o is not None:
            r["why"] = o["why"]
            used.add(id(o))
    groups = {}
    for r in rows:
        if r["why"] is None:
            groups.setdefault((r["file"], r["ctx"]), ([], []))[0].append(r)
    for o in old:
        if id(o) not in used and (o["file"], o["ctx"]) in groups:
            groups[(o["file"], o["ctx"])][1].append(o)
    for new, left in groups.values():
        new.sort(key=lambda r: r["start"])
        left.sort(key=lambda o: o["start"])
        for r in list(new):
            same_new = [n for n in new if n["hash"] == r["hash"]]
            same_old = [o for o in left if o["hash"] == r["hash"]]
            if len(same_new) == 1 and len(same_old) == 1:
                r["why"] = same_old[0]["why"]
                new.remove(r)
                left.remove(same_old[0])
        if not left or not new:
            continue
        starts = {r["start"]: r for r in new}
        offsets = {r["start"] - o["start"] for r in new for o in left}
        fits = [d for d in offsets if all(o["start"] + d in starts for o in left)]
        if len(left) >= 2 and len(fits) == 1:
            for o in left:
                starts[o["start"] + fits[0]]["why"] = o["why"]
            continue
        maybe = " / ".join(o["why"] for o in left)
        for r in new:
            if r["why"] is None:
                r["why"] = f"{TODO} (ambiguous, one of: {maybe})"
    for r in rows:
        r["why"] = r["why"] or TODO
    return rows


def render(rows, by_file):
    for r in rows:
        r["key"] = f'{r["file"]}#{r["ctx"] or "top"}#L{r["start"]}#{r["hash"]}'
    files = sorted({r["file"] for r in rows})
    lines = [
        "# Upstream touch points",
        "",
        "Every place where the patch set changes a file that upstream slot already has, at the pinned",
        "release. Generated by `task diffsurface` from `patches/`; `task check` fails if this file is stale",
        "or a row has no reason. After a rebase, review every row against the new upstream and update",
        "the reasons (docs/REBASE.md).",
        "",
        "| File | Hunks | Lines changed (+/-) | Patches |",
        "|---|---|---|---|",
    ]
    for f in files:
        fr = [r for r in rows if r["file"] == f]
        a, d = sum(r["add"] for r in fr), sum(r["del"] for r in fr)
        lines.append(f'| `{f}` | {len(fr)} | {a + d} (+{a}/-{d}) | {", ".join(sorted(set(by_file.get(f, []))))} |')
    lines += ["", "## Hunks", "", "| File | Key | Upstream lines | +/- | Context | Why |", "|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["file"], r["start"])):
        span = f'{r["start"]}' if r["count"] <= 1 else f'{r["start"]}-{r["start"] + r["count"] - 1}'
        lines.append(f'| `{r["file"]}` | {r["key"]} | {span} | +{r["add"]}/-{r["del"]} | {r["ctx"] or "(top of file)"} | {r["why"]} |')
    return "\n".join(lines) + "\n"


def main():
    diff, patchfiles, old, out = sys.argv[1:5]
    rows = hunks(open(diff).read())
    by_file = {}
    for line in open(patchfiles).read().splitlines():
        name, path = line.split("\t", 1)
        by_file.setdefault(path, []).append(name)
    try:
        previous = old_rows(open(old).read())
    except FileNotFoundError:
        previous = []
    open(out, "w").write(render(assign(rows, previous), by_file))


if __name__ == "__main__":
    main()
