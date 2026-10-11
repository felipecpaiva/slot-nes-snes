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

## Notes

- `240pee_mb.gba` is a multiboot image. mGBA and gpSP both run it as a cartridge, which the
  harness and `bench:compare` rely on.
- None of the three carts has a battery, RTC or other wall-clock input, so their output depends
  only on the scripted buttons.
- The label art under `harness/root-template/Labels/` is generated gradient art made for this
  repository, not taken from any game.
