# 0087. Add a 4:3 picture choice to the NES, SNES, Master System and Mega Drive Picture rows

- Status: Accepted. Amends [0061](0061-per-system-picture-row.md) and [0062](0062-crop-overscan-picture.md)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0004](0004-fixed-2x-canvas.md), [ADR 0007](0007-snes-select-x-picture-mode.md), [ADR 0065](0065-ps1-canvas-and-screen-section.md), [fork review 2026-10-18](../research/fork-review-2026-10-18.md) item 22, [unslot review](../research/fork-unslot.md) section 3, patches/0055-four-three.patch

## Context

The Picture rows offer Crop, Stretch and Actual (ADRs 0061, 0062). None of them shows a TV
console the way a 4:3 television did: Actual is square pixels (a NES picture is 8:7, 512x480),
Stretch and Crop fill the 3:2 panel. cloudwithax/unslot gets the TV aspect from each core's
reported geometry on a variable frame size (4cf8468), which is our deferred Option B (ADR 0004).
The savethefails review found the same gap.

On our fixed canvas the game quad always fills the 720x480 panel and only the source rect moves.
The canvas around the picture is black, and Actual already shows those margins as pillars.

## Decision

- `VideoMode` gains `FourThree`, appended after `Crop`, stored as `4:3` in `Config/video_mode.txt`
  and `Config/picture.txt`, shown as `4:3` (a `QuickValue` appended after the CPU row's `Balanced`, ADR 0085).
- `FourThree` draws the picture at a 4:3 display aspect at full height, 640x480 centred. The source
  rect is the picture's full height and 9/8 of its width (720 / 640), centred on the canvas, so the
  black canvas margins become 40 px pillars. NES, SNES and Master System (256 wide) take 288 of the
  360 canvas columns, Mega Drive H40 (320) takes all 360, H32 (256) takes 288. No renderer change
  and no frame size change.
- Offered on NES, SNES, Master System and Mega Drive (`platform_video::offers_four_three`), last in
  the Picture row: Crop, Stretch, Actual, 4:3 on NES and SNES; Stretch, Actual, 4:3 on Master
  System and Mega Drive.
- Not offered on the Game Gear: it is a handheld LCD, never shown on a 4:3 television, and its LCD
  shader is tuned for whole-number scales. Not offered on the PlayStation: its 640x480 canvas
  already shows Actual at 4:3 full height (ADR 0065).
- The in-game chords include it where they already move between modes: SELECT+X on SNES and Mega
  Drive steps through the Picture row, so it reaches 4:3 after Actual. L1 on NES moves Crop,
  Stretch, 4:3, back to Crop; on the Master System Stretch, 4:3, back to Stretch. R1 still gives
  Actual. Game Boy, Game Boy Color and Game Gear L1 stays Stretch (upstream's
  `render_picture_modes.rs` pins the Game Boy behaviour).
- Factory defaults are unchanged (NES and SNES Crop, Master System and Mega Drive Stretch). The
  user's pick in the row, or the cart's own line, stays the default as before.

## Consequences

- No upstream test site; GBA, GB and GBC frames are untouched (the rect code returns before any
  of theirs).
- The picture is scaled 2.5x across and 2x (NES), 2.14x (SNES), 2.5x (Master System) down, so it
  is not whole-number on either axis. Line and Sharp are the shaders to check for shimmer on the
  device.
- The 4:3 aspect is of the whole picture, overscan included. A NES or SNES player who wants the
  overscan hidden keeps Crop.
- Ported onto upstream main 1b20432 (ADR 0083): the chords follow upstream's remapping and our
  reshaped 0007. SELECT+X steps the Picture row only while no user shortcut is bound to SELECT+X
  (the user's binding wins); L1 keeps upstream's guards (slot owns the shoulders, and L1 is not
  plainly bound to a game button), so a user who binds L1 to a game button gets the button, not
  the picture step. R1 the same for Actual.
- On a rebase, check `video_mode::source_rect` keeps its early returns and that the canvas outside
  the picture is still cleared to black.
