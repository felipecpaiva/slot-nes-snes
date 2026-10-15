# 0038. Rebase the patch set onto slot v1.7.0

- Status: Accepted
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [REBASE.md](../REBASE.md), [UPSTREAM-TOUCHPOINTS.md](../UPSTREAM-TOUCHPOINTS.md), ADRs 0039 to 0046, `SLOT_PIN`

## Context

slot v1.7.0 (commit 34ac380, tarball sha256 8219512f...0ab1) changed 218 files: skeuomorphic
bitmap carts with light and dark themes, an in-game menu, Favorites and Recents shelves, shelf
memory at power off (#53), per-platform bezels (#77), per-platform Shader and Color Correction
rows (#83), GBA run-ahead, a pacer for the released audio device and logs under `Logs/`. The dry
run stopped at patch 0001 in `crates/slot-ui/src/cart.rs`. MGBA_COMMIT and GPSP_COMMIT did not
move, so the `gpsp_*` pins stay.

## Decision

Re-apply the 23 patches one by one onto a fresh v1.7.0 tree, resolving each by intent, and keep
one commit per patch. Three patches are dropped because v1.7.0 does the same job (shelf-memory,
lazy-shelf, audio-release-pace), three are reshaped onto the new upstream code (cart art,
quick-menu shaders, canvas stretch), the rest port with small conflict fixes. The set is now 20
patches, renumbered 0001 to 0020 with the same slugs.

| Old | New | Result |
|---|---|---|
| 0001 to 0011 | 0001 to 0011 | ported; new upstream Platform matches get NES and SNES arms; canvas keeps the SNES height crop, ADR 0046 |
| 0012 cart-art | 0012 | reshaped, ADR 0042 |
| 0013 cart-shell-region | 0013 | ported; SNES region read cached |
| 0014 shaders | 0014 | ported |
| 0015 lazy-shelf | none | dropped, ADR 0040 |
| 0016 audio-release-pace | none | dropped, ADR 0041 |
| 0017 frame-trace | 0015 | ported as is |
| 0018 quick-menu-retro-shaders | 0016 | reshaped, ADR 0043 |
| 0019 shelf-memory | none | dropped, ADR 0039 |
| 0020 retro-shaders | 0017 | ported; retro draw takes upstream's rect |
| 0021 audio-reopen | 0018 | ported onto upstream's Pacer; the start prefill now runs once before the worker loop, since upstream's new `runahead.rs` sound test showed it depended on when the worker first saw Normal |
| 0022 retro-line-pixel | 0019 | ported |
| 0023 label-top | 0020 | ported; art.rs touch is now one visibility token |

## Consequences

- Upstream test sites: (c) is gone because upstream deleted `label_top` from
  `render_shelves.rs` (ADR 0044). Sites (a), (b), (d), (e) and (f) hold unchanged.
- Two upstream frame-hash tests in `slot-gfx/tests/layout.rs` fail on the unpatched v1.7.0 tree on
  the M5 Max; they now run in both trees and gate on "no new failure" (ADR 0045).
- Device scripts read `Logs/slot.log` (untested without the device).
- `harness/frame_dump.rs` follows v1.7.0's menus (General first, a platform list under Screen),
  treats the in-game menu as not running, and retries the composite rig's first tick until the
  worker locks. The legs and hashes are compared between trees as before.
- `task bench:compare` is over the 2% line on the M5 Max (gpSP 240pee 102.8 to 102.9%, mGBA
  240pee up to 103.6%, GB and GBC 101.0 to 101.4%). The ns.0 tree on v1.6.0 shows the same 2.7 to
  3.3% over v1.6.0 upstream on this machine today (core_bench run side by side), so it predates
  the rebase; v1.7.0-ns.1 and ns.0 are within 0.5% of each other. Open for the maintainer.
- Needs the device: boot time, perf:play gate titles, carts in both themes, Favorites and Recents.
