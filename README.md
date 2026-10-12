# slot-nes-snes

NES and SNES shelves for [slot](https://github.com/BrandonKowalski/slot), as a patch set on top of
slot's own releases.

> [!IMPORTANT]
> This is **not** part of slot, and it is not endorsed by its author. slot is Game Boy-centric by
> design, and its author has said plainly that slot will not add more systems
> ([#30](https://github.com/BrandonKowalski/slot/issues/30#issuecomment-6091021879)). That decision
> is respected here: nothing in this repo asks slot to change.
>
> **Please do not report bugs from this patch set to slot's tracker.** Open them here.

## What it does

slot keeps GBA, GB and GBC on their own shelves, each with its own cores and settings. This patch
set adds two more shelves the same way:

| Shelf | Folder | Default core | Alternative |
|---|---|---|---|
| NES | `Games/NES` | fceumm | nestopia |
| SNES | `Games/SNES` | snes9x | snes9x2005_plus |

The goal is that a NES or SNES cart feels like a GBA cart in slot: same insert, same saves and
save states, same rewind and fast-forward, same menus. GBA, GB and GBC behaviour stays
byte-identical to upstream. That is the goal. The first version has known gaps, listed in [docs/QUALITY-BAR.md](docs/QUALITY-BAR.md#known-gaps-not-hidden).

## How it works

slot builds mGBA from a pinned upstream commit plus a few `.patch` files. This repo does the same
thing to slot: a pinned slot release, plus the patches in `patches/`, built into a replacement
`System/slot` with the extra cores.

## Setup

```sh
brew install mise colima docker
brew install zbar            # optional: the barcode test skips without it
mise trust && mise install   # in the repo: rust 1.96, task, cmake 3.x, adb (macOS)
colima start
```

## Install on a device

Build the zip with `task zip` (it runs `task dist:device` and `task src-tarball` itself). It lands in `build/` as
`slot-nes-snes-<slot tag>-<ns.N>-h700.zip`. `sh scripts/zip-check.sh <zip>` checks it.

**Without adb (how most people install):** unzip, then copy the contents of the one top folder
(`System/`, `BIOS/`, `Config/`, `Games/`, ...) onto the root of the SD card, merging with what is
there. An update replaces `System/` and keeps `Config/`, `Saves/` and `States/`. Put NES carts in
`Games/NES`.

**With adb:** `task deploy:device` pushes `System/` to `/mnt/sdcard` and reboots the device
(`SD=/other/path` overrides the target), then `task log:device` prints `slot.log`.

## Status

Planned. No patches yet. Work starts with Phase 1 of [docs/PLAN.md](docs/PLAN.md).

Progress is tracked on the [project board](https://github.com/users/felipecpaiva/projects/8), one issue per pull request, with a milestone per phase. The issues are generated from [.github/issues/](.github/issues/) by `python3 scripts/setup-github-project.py` (safe to re-run).

- [docs/RESEARCH.md](docs/RESEARCH.md): code map of slot v1.6.0, core choices for the H700, licence notes
- [docs/EVAL.md](docs/EVAL.md): the options considered (upstream PR, shim core, patch set) and why
- [docs/PLAN.md](docs/PLAN.md): the phased build plan, with tests per phase
- [docs/DECISIONS.md](docs/DECISIONS.md): binding decisions and why
- [docs/QUALITY-BAR.md](docs/QUALITY-BAR.md): what "done" means, and the known gaps

## Licences

slot is GPL-3.0-or-later, so this patch set is too (see [LICENSE](LICENSE)). fceumm and nestopia
are GPL-2.0-or-later. **snes9x is not GPL**: it is free for non-commercial use only. Builds that
include it ship its licence file (`System/licenses/snes9x-LICENSE.txt`) and must never be sold or
bundled with anything sold. See [LICENSING.md](LICENSING.md).

## Credit

All of the hard work is Brandon Kowalski's [slot](https://github.com/BrandonKowalski/slot). Go
star it.
