#!/usr/bin/env python3
"""Create (or sync) the slot-nes-snes GitHub Project from .github/issues/*.md.

    python3 scripts/setup-github-project.py            # create or sync everything
    python3 scripts/setup-github-project.py --dry-run  # print what would happen

Idempotent: labels and milestones are created only if missing, issues are matched by
exact title and their bodies re-synced, the board is found by title. Issue files refer to
each other by filename stem (e.g. `02-pin-and-fetch`); those become `#<number>` links.
Needs the gh `project` scope.
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

OWNER = "felipecpaiva"
REPO = f"{OWNER}/slot-nes-snes"
TITLE = "slot-nes-snes"
ISSUES = Path(__file__).resolve().parent.parent / ".github" / "issues"
DRY = "--dry-run" in sys.argv

PHASES = {
    "1": "Phase 1: NES boots on the RG35XXSP",
    "2": "Phase 2: SNES",
    "3": "Phase 3: full parity",
    "4": "Phase 4: real cart art with variants",
    "5": "Phase 5: release and CI with the device gate",
    "6": "Deferred",
    "7": "Phase 7: Game Gear, Master System and Mega Drive",
    "8": "Phase 8: PlayStation",
    "10": "Phase 10: TurboGrafx-16",
    "11": "Phase 11: WonderSwan",
}
COLOURS = {"phase": "5319e7", "area": "0e8a16", "type": "1d76db", "size": "fbca04"}
FIELDS = {"Phase": list(PHASES.values()),
          "Area": ["infra", "platform", "cores", "video", "input", "ui-art", "tests", "release", "docs", "device"],
          "Size": ["S", "M", "L"]}


def gh(*args, json_out=False, write=True):
    if DRY and write:
        print("DRY gh", " ".join(a if len(a) < 80 else a[:77] + "..." for a in args))
        return {} if json_out else ""
    for attempt in range(4):  # GitHub's secondary rate limit fails bursts of edits
        run = subprocess.run(["gh", *args], capture_output=True, text=True)
        if run.returncode == 0:
            return json.loads(run.stdout) if json_out else run.stdout.strip()
        print(f"gh {args[0]} {args[1]} failed ({run.stderr.strip()[:120]}), retry {attempt + 1}")
        time.sleep(10 * (attempt + 1))
    sys.exit(f"gh {' '.join(args[:3])} kept failing")


def parse(path):
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        sys.exit(f"{path.name}: missing frontmatter")
    meta = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(":")
        value = value.strip()
        if value.startswith("["):
            value = [v.strip() for v in value.strip("[]").split(",") if v.strip()]
        else:
            value = value.strip('"')
        meta[key.strip()] = value
    for key in ("title", "phase", "area", "type", "size"):
        if key not in meta:
            sys.exit(f"{path.name}: frontmatter lacks {key}")
    return meta, m.group(2).strip()


def ensure_labels(metas):
    have = {l["name"] for l in gh("label", "list", "--repo", REPO, "--limit", "200",
                                   "--json", "name", json_out=True, write=False)}
    want = {f"{k}:{m[k]}" for m in metas for k in ("phase", "area", "type", "size")}
    for name in sorted(want - have):
        gh("label", "create", name, "--repo", REPO, "--color", COLOURS[name.split(":")[0]])


def ensure_milestones():
    have = {m["title"]: m["number"] for m in gh(
        "api", f"repos/{REPO}/milestones?state=all&per_page=100", json_out=True, write=False)}
    for title in PHASES.values():
        if title not in have:
            gh("api", f"repos/{REPO}/milestones", "-f", f"title={title}")


def existing_issues():
    rows = gh("issue", "list", "--repo", REPO, "--state", "all", "--limit", "500",
              "--json", "number,title,url", json_out=True, write=False)
    return {r["title"]: r for r in rows}


def link(body, numbers):
    # NN-slug stems become #N; leave anything unknown untouched.
    return re.sub(r"\b(\d{2}-[a-z0-9-]+)\b",
                  lambda m: f"#{numbers[m.group(1)]}" if m.group(1) in numbers else m.group(1), body)


def ensure_project():
    projects = gh("project", "list", "--owner", OWNER, "--format", "json", "--limit", "100",
                  json_out=True, write=False)["projects"]
    found = next((p for p in projects if p["title"] == TITLE), None)
    if found:
        number = found["number"]
    else:
        number = gh("project", "create", "--owner", OWNER, "--title", TITLE,
                    "--format", "json", json_out=True).get("number")
    if number is None:
        return None, None
    gh("project", "link", str(number), "--owner", OWNER, "--repo", REPO)
    fields = {f["name"]: f for f in gh("project", "field-list", str(number), "--owner", OWNER,
                                        "--format", "json", json_out=True, write=False)["fields"]}
    for name, options in FIELDS.items():
        if name not in fields:
            gh("project", "field-create", str(number), "--owner", OWNER, "--name", name,
               "--data-type", "SINGLE_SELECT", "--single-select-options", ",".join(options))
    fields = {f["name"]: f for f in gh("project", "field-list", str(number), "--owner", OWNER,
                                        "--format", "json", json_out=True, write=False)["fields"]}
    return number, fields


def main():
    files = sorted(p for p in ISSUES.glob("[0-9][0-9]-*.md"))
    parsed = [(p.stem, *parse(p)) for p in files]
    print(f"{len(parsed)} issue files")
    ensure_labels([m for _, m, _ in parsed])
    ensure_milestones()

    issues = existing_issues()
    numbers = {}
    for stem, meta, _ in parsed:  # pass 1: make sure every issue exists
        if meta["title"] in issues:
            numbers[stem] = issues[meta["title"]]["number"]
            continue
        url = gh("issue", "create", "--repo", REPO, "--title", meta["title"], "--body", "Draft, synced next.",
                 "--milestone", PHASES[meta["phase"]],
                 *sum((["--label", f"{k}:{meta[k]}"] for k in ("phase", "area", "type", "size")), []))
        numbers[stem] = int(url.rsplit("/", 1)[-1]) if url else 0

    for stem, meta, body in parsed:  # pass 2: bodies with real #links
        deps = meta.get("depends_on") or []
        head = f"Depends on: {', '.join(f'#{numbers[d]}' for d in deps if d in numbers)}\n\n" if deps else ""
        gh("issue", "edit", str(numbers[stem]), "--repo", REPO, "--body",
           head + link(body, numbers) + f"\n\n<sub>Source: `.github/issues/{stem}.md`</sub>")

    number, fields = ensure_project()
    if number is None:
        return
    current = existing_issues()
    project_id = gh("project", "view", str(number), "--owner", OWNER, "--format", "json",
                    "--jq", ".id", write=False)
    for stem, meta, _ in parsed:
        item = gh("project", "item-add", str(number), "--owner", OWNER, "--url",
                  current[meta["title"]]["url"], "--format", "json", json_out=True)
        if not item:
            continue
        for name, value in (("Phase", PHASES[meta["phase"]]), ("Area", meta["area"]), ("Size", meta["size"])):
            option = next((o["id"] for o in fields[name]["options"] if o["name"] == value), None)
            if option is None:  # an option added to FIELDS after the field was made; add it on the board
                print(f"note: board field {name} has no option {value!r}, left unset")
                continue
            gh("project", "item-edit", "--id", item["id"], "--project-id", project_id,
               "--field-id", fields[name]["id"], "--single-select-option-id", option)
    (ISSUES / "numbers.json").write_text(json.dumps(numbers, indent=2) + "\n")
    print(f"done: https://github.com/users/{OWNER}/projects/{number}")


if __name__ == "__main__":
    main()
