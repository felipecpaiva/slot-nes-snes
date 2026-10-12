---
title: "Patch 0002: Add Platform::Nes with its own shelf, folders and placeholder cart"
phase: 1
area: platform
type: feature
size: M
depends_on: [06-step0-exhaustive-matches]
---

## Why
NES gets a first-class shelf with `Games/NES`, `Labels/NES`, `Saves/NES`, `States/NES`, without changing any upstream constant that tests pin (docs/PLAN.md Phase 1 deliverables, Approach "Upstream test code stays literally unmodified", Build steps 6, 7, 22).

## Scope
`patches/0002-platform-nes.patch`:
- [ ] Named upstream test exception (maintainer decision 2026-10-12): add `| Platform::Nes` to `label_band` in `slot: crates/slot-ui/tests/chrome.rs:43` and `| CartPlatform::Nes` to `label_top` in `slot: crates/slot/tests/render_shelves.rs:637`, nothing else; `scripts/check-upstream-tests.sh` allows exactly those tokens.
- [ ] Named upstream test exception (maintainer decision 2026-10-12): in `slot: crates/slot-store/tests/durability.rs` test `an_unreadable_platform_reads_as_a_card_that_never_said`, the example `cart_platform=nes` becomes `cart_platform=pce`, nothing else; `slot_state.rs:240` stays on `SHELVES` so NES resume works.
- [ ] Reviewed and left on purpose (no change for NES): `slot: crates/slot/src/session.rs:465` and `app.rs:2701` stay GBA only (link cable); the `Core` comparisons at `slot: crates/slot/src/core.rs:162` and `app.rs:2688,2713,2840` skip safely for a non-mGBA, non-gpSP core. Re-check them if a later patch gives NES a link or a new core path.
- [ ] `slot: crates/slot-store/src/platform.rs`: append `Platform::Nes`; `dir_name` "NES"; extensions `["nes"]`; `picture` (256, 240). `Platform::ALL` stays at 3.
- [ ] `Platform::SHELVES = [Gba, Gb, Gbc, Nes]` in `platform_policy.rs`; switch `slot: crates/slot-store/src/scan.rs:65`, `slot: crates/slot/src/app.rs:365` and `slot: crates/slot-store/src/slot_state.rs:240` to it.
- [ ] `slot: crates/slot/src/root.rs` DIRS: add `Games/NES`, `Labels/NES`, `Saves/NES`, `States/NES` (`[&str; 20]` becomes `[&str; 24]`).
- [ ] Title stays empty and the display name is the file stem (no NES header parse), even when the bytes look like a GB header.
- [ ] Provisional shader arms: `slot: crates/slot/src/app.rs:1046` and `:1409` map Nes to `shader_gb` / `Shader::GB` (replaced in 21-shaders).
- [ ] Policy arms: `has_gb_palettes(Nes) = false`, `owns_shoulders(Nes) = true` (picture toggle like GB).
- [ ] `slot: crates/slot-store/src/core.rs:49,56`: gpSP `runs(Nes) = false`; `default_for(Nes) = Mgba` as a temporary value that issue 08 replaces with Fceumm (never shipped on its own, patches ship together).
- [ ] `slot: crates/slot-store/src/scan.rs`: explicit `Platform::Nes => {}` arm (no header parse).
- [ ] `picker_cores(Nes) = None`.
- [ ] Placeholder cart arms in `slot: crates/slot-ui/src/shell.rs:92`, `slot: crates/slot-ui/src/cart.rs:91,157,164`: GBA Spec, solid `#8c8c8c`.

## Tests
| ID | File | Asserts |
|---|---|---|
| T4 | `slot-store/tests/nes_platform.rs` | `SHELVES == [Gba, Gb, Gbc, Nes]` (Phase 2 adds `Snes`); `ALL` unchanged; `Nes.accepts("x.nes")`, `!Nes.accepts("x.gba")` |
| T5 | `slot-store/tests/nes_scan.rs` | `Games/NES/Super Mario Bros. 3 (USA).nes` gives one cart, platform Nes, title stays empty and the display name is the file stem (no NES header parse), even when the bytes look like a GB header |
| T7 | `slot/tests/nes_palette.rs` | `palette_for(Some(p), Nes, rom_0x143_clear, None)` is None |
| T12 | `slot/tests/nes_dist.rs` | `--init-root` creates the NES dirs plus every upstream DIRS entry |

Upstream tests stay unmodified, in particular `slot: crates/slot-store/tests/platform.rs:5,11` (pins `Platform::ALL`) and the DIRS iterators in `slot: crates/slot/tests/dist.rs:11,20,45`, `slot: crates/slot/tests/bios.rs:118`, `slot: crates/slot/tests/boot.rs:254`.

## Edge cases
| Case | Expected handling |
|---|---|
| (none specific) | Downgrade with `cart_platform=nes` is covered in 23-states-quickmenu-resume |

## Acceptance
- [x] T4, T5, T7, T12 green; `task check` green (1408 passed).
- [x] GBA harness compare 0 diffs (H1, H1G, H2, B1).
- [x] `Platform::ALL.len() == 3` still.
- [x] `app.rs` hunks are one token each: 8 changed lines for 0002, 14 total.

## Device check (RG34XXSP)
None on its own; NES needs a core and the canvas to play. The phase device check is in 01-phase-1-nes-boots.

## Review notes
- Gotcha 11 (upstream tests pin enum and menu shapes): `slot: crates/slot-store/tests/platform.rs:5,11`, `slot: crates/slot-store/tests/core.rs:203`, both `quick_menu.rs` tests and `slot: crates/slot/tests/render_shelf.rs:49-62`. Only source consumers switch to `SHELVES`; `ALL` is not touched. The same rule applies to `Core::EVERY` in 08-core-fceumm.
- Enums are append-only: `Nes` goes after `Gbc`.
- The placeholder cart is temporary; 26-cart-art replaces it.

## References
- docs/PLAN.md: Phase 1 deliverables (0002), Approach, Build steps 6, 7, 22, Signature impact table (`root::DIRS`), Consumer-grep evidence (`Platform::ALL`)
- `slot: crates/slot-store/src/scan.rs:65`; `slot: crates/slot/src/app.rs:365,1046,1409`; `slot: crates/slot-store/src/slot_state.rs:240`; `slot: crates/slot-ui/src/shell.rs:92`; `slot: crates/slot-ui/src/cart.rs:91,157,164`
