# 0022. Default NES and SNES to the Stretch picture mode

- Status: Accepted. Amended by [0061](0061-per-system-picture-row.md) and [0062](0062-crop-overscan-picture.md)
- Date: 2026-10-12
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 43](../../.github/issues/43-nes-snes-default-stretch.md), [patch 0008](../../patches/0008-default-stretch.patch)

## Context

Maintainer's device test on the RG34XXSP: the 2x NES and SNES picture left black bars at the sides
of the 720x480 panel. GBA and GB must stay exactly as upstream.

## Decision

NES and SNES default to the Stretch picture mode; GBA, GB and GBC keep upstream's Actual. A cart
with no line in `Config/video_mode.txt` takes its platform's default; a saved line always wins.

## Consequences

- The picture fills the screen, about 40% wider than 8:7. Accepted by the maintainer.
- The per-game toggle switches back to Actual and the choice is saved.
- Nothing is written to the card until the user toggles. `VideoMode::default()` stays Actual.
- On 4:3 devices Stretch fills the window above the bezel.
