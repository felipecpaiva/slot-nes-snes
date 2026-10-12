# Harness carts

Freely licensed homebrew used by `task harness:*` and `task bench:compare`. No commercial
ROM belongs here. Each cart has its licence text in `LICENSES/`, copied from the upstream
repository at the version below. Licences were read from the primary source on 2026-10-11.

| File | Platform | What it is | Version | Source | Licence | sha256 |
|---|---|---|---|---|---|---|
| `240pee_mb.gba` | GBA | 160p Test Suite (multiboot build), Damian Yerrick's port of Artemio Urbina's 240p Test Suite | v0.23 (2023-03-03), tag commit `019a524b6b042c1ea1c2e8414e79f152d5997ab3` | https://github.com/pinobatch/240p-test-mini/releases/download/v0.23/240pee_mb.gba | GPL-2.0-or-later (`LICENSES/240p-test-mini-GPL-2.0.txt`) | `47844f7140738a06f8f3bc09780da3ab095539a250b870f614feed561d9d6f34` |
| `gb240p.gb` | GB, runs on GBC (header flag 0x80) | 144p Test Suite, same author and release | v0.23 | https://github.com/pinobatch/240p-test-mini/releases/download/v0.23/gb240p.gb | GPL-2.0-or-later (`LICENSES/240p-test-mini-GPL-2.0.txt`) | `733eb6e7ec0719752ddd5fcda4e715c2f2e20f4ac4bc971c4bd1d49272f9bb04` |
| `cgb-acid2.gbc` | GBC (colour only) | cgb-acid2 PPU test by Matt Currie | v1.1 (2020-04-14), tag commit `fa5b7f86d6fb599f79e55169494d981a7af75a31` | https://github.com/mattcurrie/cgb-acid2/releases/download/v1.1/cgb-acid2.gbc | MIT (`LICENSES/cgb-acid2-MIT.txt`) | `197fb0bcec544f0400527fc707e0a94f55435974986e6986b424ace5de81720e` |

## Licence evidence

- 240p-test-mini: the repository README states "Like Artemio's original versions, these ports
  of 240p Test Suite are free software under the GNU General Public License, version 2 or
  later", and its `LICENSE` file is the GPL version 2 text. It also says test graphics were
  replaced "to keep the software free". Corresponding source is the tag above at
  https://github.com/pinobatch/240p-test-mini.
- cgb-acid2: the repository `LICENSE` is the MIT licence, copyright 2020 Matt Currie.

## Source and written offer (GPL-2.0-or-later)

`240pee_mb.gba` and `gb240p.gb` are redistributed here in binary form under the GNU General
Public License, version 2 or later. Their complete corresponding source is shipped in this
repository as `LICENSES/240p-test-mini-v0.23-source.tar.gz`, the GitHub archive of tag v0.23
(commit `019a524b6b042c1ea1c2e8414e79f152d5997ab3`, recorded in the archive header and matching
`git ls-remote https://github.com/pinobatch/240p-test-mini refs/tags/v0.23`).
sha256 `3c01ab1264248c91c5783d110fb347bb9377fdc36f2cefb957a74af0fa291fdc`, identical from
`github.com/.../archive/refs/tags/v0.23.tar.gz` and `codeload.github.com/.../tar.gz/refs/tags/v0.23`.

Written offer: for at least three years from the date a binary was last distributed from this
repository, we will give anyone who asks a complete machine-readable copy of the corresponding
source of these two programs, for no more than the cost of physically performing the copy. Ask by
opening an issue on this repository. The tarball above is that source today, so the offer is
already met for as long as it stays in the repository.

`cgb-acid2.gbc` is MIT licensed and needs no source offer; its licence text is kept in `LICENSES/`.

## Generated at run time

`harness/make_assets.py` builds two things into a temporary copy of the harness root, and neither
is committed: a DMG-only cart `zdmg-blank.gb` (the GB palette option only applies to DMG-only
carts, and the three carts above all declare CGB support) made from the Nintendo logo bytes of
`gb240p.gb` and zeros, and the large label PNGs used by `task harness:inject`.

## Notes

- `240pee_mb.gba` is a multiboot image. mGBA and gpSP both run it as a cartridge, which the
  harness and `bench:compare` rely on.
- None of the three carts has a battery, RTC or other wall-clock input, so their output depends
  only on the scripted buttons.
- The label art under `harness/root-template/Labels/` is generated gradient art made for this
  repository, not taken from any game.
