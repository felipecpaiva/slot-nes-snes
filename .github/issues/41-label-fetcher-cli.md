---
title: "Fetch real NES and SNES cart labels onto the SD card with a small script"
phase: 4
area: ui-art
type: feature
size: M
depends_on: [26-cart-art, 27-cart-shell-grammar-region]
---

## Why
Carts must show the real physical cartridge label, never a screenshot (maintainer goal, 2026-10-12). Until Cart Studio supports NES and SNES (40-cart-studio-nes-snes), users need a way to put real labels on the card without hand-sizing images. A script on the user's own machine fetches art at user time, so nothing from Nintendo is ever committed.

## Scope
- [ ] `tools/fetch-labels.py`, python3 standard library only, `--card <root>`.
- [ ] Scan `Games/NES` (`.nes`) and `Games/SNES` (`.sfc`, `.smc`); ignore `._` sidecar files.
- [ ] CRC32 per ROM: NES over the whole file including the iNES header; SNES after stripping 512 bytes when `len % 1024 == 512`.
- [ ] Download the libretro-database no-intro dats for NES and SNES (cached under the user's cache dir) and map CRC to the No-Intro name.
- [ ] Label source, in order: ScreenScraper `support-texture` (user's credentials from `SS_*` environment variables), then libretro-thumbnails `Named_Logos` on a generated ground (Logo Only look), else skip. Never box art, never a screenshot.
- [ ] Pre-crop with the same centred cover fit as `slot: crates/slot-ui/src/art.rs` to the variant's label box from 26-cart-art (one table, tested against the patch constants), and write `Labels/<DIR>/<stem>.png` named after the user's own ROM stem.
- [ ] Write `stem = <outline> RRGGBB <finish>` lines to `Labels/cart_shell.txt`: outline `nes` or `famicom`, `snes` or `sfc`, picked from the dat name's region. Never overwrite an existing line or PNG without `--force`.
- [ ] Flags `--dry-run`, `--only <stem>`, `--force`; a summary of matched, missing and skipped.
- [ ] README section: credentials, art terms, and why outline overrides belong in `Config/cart_shell.txt`.

## Tests
| ID | File | Asserts |
|---|---|---|
| T49 | `tools/tests/test_fetch_labels.py` | Offline, with fixture mini-dats and a fake HTTP layer: headered NES CRC match, SNES with a 512-byte copier header, unknown CRC, 404, rate limit, a libretro symlink stub body; output PNGs have exactly the variant's label size; every cart_shell.txt line parses under slot's grammar |

## Edge cases
| Case | Expected handling |
|---|---|
| ROM renamed to another game | CRC wins; warn on the name mismatch |
| Missing or bad iNES header, unknown CRC | Try the CRC after the 16-byte header, then a name match, else skip and report |
| Same stem with two extensions | Report the collision, write nothing for that stem |
| Unicode NFC vs NFD stems (exFAT on macOS) | Normalise the same way slot does before matching |
| ScreenScraper quota exhausted | Stop cleanly, keep what was written, resumable on the next run |
| Credentials | Never printed or logged |

## Acceptance
- [ ] On a sample card of 10 NES, 10 SNES and 2 Famicom/Super Famicom ROMs: correctly sized PNGs, valid cart_shell.txt lines, a clear report.
- [ ] T49 passes offline on macOS and Linux with no third-party packages.
- [ ] Nothing from Nintendo committed.

## Device check (RG34XXSP)
After running the script on the card: every matched NES and SNES cart shows its real label on the right cart shape.

## Review notes
- The script's label sizes must come from the same numbers as patch 0010; a mismatch shows as a cropped or blurred label on the device.
- Fetching at user time is the licence boundary: no art in the repo, no art in releases.

## References
- 40-cart-studio-nes-snes; docs/PLAN.md Phase 4
- libretro-database `metadat/no-intro/Nintendo - Nintendo Entertainment System.dat`, `Nintendo - Super Nintendo Entertainment System.dat`
- `slot: crates/slot-store/src/scan.rs:75-90`, `slot: crates/slot-ui/src/art.rs:3-25`, `slot: crates/slot-store/src/cart_shell.rs`
