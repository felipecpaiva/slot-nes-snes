---
title: "Patch: Remember the last shelf and each shelf's cart across restarts"
phase: 3
area: platform
type: feature
size: S
depends_on: [12-platform-snes]
---

## Why
With five shelves (GBA, GB, GBC, NES, SNES) users switch platforms often. Each shelf already keeps its own cart position in memory, but after a restart slot opens on the first non-empty shelf at index 0. slot has no favorites or recents, so the last shelf and its last cart are how a user jumps back in.

## Scope
`patches/NNNN-shelf-memory.patch`:
- [x] New `crates/slot/src/shelf_recall.rs`: `ShelfMemory` (current platform plus one stem per platform), its file text, `read`, `restore` and `note`.
- [x] Stored in `Config/shelf.state`, not `slot.state`: `shelf=<platform>` and `shelf_<platform>=<stem>`, platform as lowercase dir name (`gba`, `gb`, `gbc`, `nes`, `snes`). `SlotState` gets no field because upstream's `durability.rs` builds it as an exhaustive literal, and editing it is outside the named test exceptions. slot.state stays byte-identical, so old and new builds read each other's cards.
- [x] Carts are kept by stem, so adding or removing ROMs does not shift them.
- [x] Written by the existing state writer thread: `StateWriter::save_file` adds a second latest-wins job next to slot.state, so `flush` (poweroff, doze, eject, drop) also covers it and a failed write raises the card alarm.
- [x] Saved from `App::timers` while on the shelf, only when the selection or shelf changed and no direction is held (`Shelf::held`), so a held direction writes once when it is let go, not on every repeat step.
- [x] Restored in `App::start`: every shelf selects its remembered cart (index 0 when the stem is gone); with no seated cart, slot opens on the remembered shelf unless it is missing or empty. A seated cart (auto-resume) still wins.

## Tests
| ID | File | Asserts |
|---|---|---|
| T64 | `slot/tests/shelf_memory.rs` | shelf.state text round-trips; a missing or damaged file reads as no memory |
| T65 | `slot/tests/shelf_memory.rs` | an old card with no shelf.state opens on the first cart |
| T66 | `slot/tests/shelf_memory.rs` | boot opens the remembered shelf on its remembered cart, and the other shelf keeps its own |
| T67 | `slot/tests/shelf_memory.rs` | a gone stem falls back to index 0; an empty remembered shelf falls back to the first non-empty one |
| T68 | `slot/tests/shelf_memory.rs` | a seated cart still wins |
| T69 | `slot/tests/shelf_memory.rs` | moving and switching shelves is remembered across a restart, slot.state is not rewritten; a held direction is written only after release |

Upstream tests stay unmodified.

## Edge cases
| Case | Expected handling |
|---|---|
| Two carts with the same stem on different shelves | Kept per platform, no clash |
| Remembered platform unknown (`shelf=pce`) | Ignored, first non-empty shelf |
| Clock not set at boot | Nothing is recorded until the shelf is shown |
| Write fails (read-only card) | Card alarm, same as slot.state |

## Acceptance
- [x] T64 to T69 green.
- [x] rustfmt --check clean on files added or changed.
- [x] `task check` green.
- [x] `docs/UPSTREAM-TOUCHPOINTS.md` regenerated with the new hunks and reasons.

## Device check (RG34XXSP)
Pick a cart on the NES shelf, switch to GBA and pick another, power off from the menu, power on: slot opens on GBA with that cart; R/L back to NES shows the NES cart.

## Review notes
- `persist_soon` has no time debounce (one latest-wins pending job, fsync per write), which is why saving waits for the cursor to be at rest.

## References
- docs/DECISIONS.md (2026-10-13)
