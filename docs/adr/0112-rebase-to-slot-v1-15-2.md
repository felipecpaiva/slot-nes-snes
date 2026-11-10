# 0112. Rebase the patch set onto slot v1.15.2

- Status: Accepted. Amends [0110](0110-rebase-to-slot-v1-14-0.md) when accepted
- Date: 2026-11-10
- Deciders: maintainer (Felipe Paiva)
- Related: [REBASE.md](../REBASE.md), [ADR 0110](0110-rebase-to-slot-v1-14-0.md), [ADR 0111](0111-gamebit-on-the-added-shelves.md), `SLOT_PIN`

## Context

Upstream tagged v1.15.0 on 2026-11-08 (02:31 UTC), v1.15.1 an hour later and v1.15.2 at 06:31 (commit 3449869,
tarball sha256 cac8b745...f8cc). Together they are 51 commits and 272 files past v1.14.0, 20,800 new lines, 10,500 of
them in `app.rs`. `MGBA_COMMIT`, `GPSP_COMMIT` and `GAMBATTE_COMMIT` did not move; two core patches changed
(`gb-audio-centred-channels`), which made the host cores rebuild. The dry run stopped at patch 0001, so this is a heavy
rebase: 163 of the 164 patches were cherry-picked one by one onto the tag, with one adaptation patch (0164) added.
The old `rustfmt-1-14-0` patch is dropped and the new lines are formatted by the format check instead.

| Upstream | What it touches in ours |
|---|---|
| 1.15.0 Collections, Shelf Mode, `Rack::Collection` and `Rack::AllGames` | the rack chain walks `Platform::SHELVES`, collections stack behind Favorites, All Games is last; a game of any shelf can be in a collection (`recent_value` reads `Platform::SHELVES`); the shelf order sort gives collections and All Games their own keys |
| 1.15.0 Game Boy Advance Video behind Game Boy Advance (L2 / R2) | followed upstream: the shelf walk skips Game Boy Advance Video, our shelf order tests expect 26 shelves |
| 1.15.0 Kid Mode | `kid::allowed` drops every action it does not list, so our chords and quick menu rows are locked in Kid Mode and no row of ours is shown there |
| 1.15.0 Nintendo DS (`Platform::Nds`, `Core::Dsperate`) | behind `feature = "nds"`, off in the H700 build; our exhaustive matches carry the cfg arms so the feature can be turned on |
| 1.15.0 rom names with a space or a dot at the end are renamed at boot | `sweep_names` walks `Platform::ALL`, so the added shelves are not swept; their per system files (`video_mode.txt`, `selected_core.txt`, `retro_scale.txt`) would not follow a rename, so this is left alone on purpose |
| 1.15.0 core choice per platform and stem (`core_key`) | our core picker writes `NES/Contra`; reads still accept the old stem only key |
| 1.15.0 Auto Load State (`AutoLoad`), eject write on a thread | `state.auto_load` is an enum; our save on eject tests wait with `settle_saves` |
| 1.15.0 overlays (`overlay_gba`, `overlay_gb`, `overlay_gbc`) | the added shelves share the Game Boy Advance slot, like their bezels |
| 1.15.0 frame pacing by `due` ticks, audio `ring.awake()` | PAL pacing sums `owed_frames` over the ticks due; our audio hold keeps `listen` and ORs `awake()` |
| 1.15.0 `foot_y`, `rest_y`, `quick_window` take a `Canvas` | threaded through our lid fit, disc insert and tests |
| 1.15.0 LCD3x renamed LCD, `ScreenEffect::LcdGrid` | the stored key stays `lcd3x`; `mode()` maps `LcdGrid` to 6 |

## Decision

1. **Follow upstream** for Game Boy Advance Video, Collections, Kid Mode and Auto Load State; ours adapts to them.
2. **`sweep_names` is not extended** to the added shelves (see the table).
3. **Our `shader_nes` and `shader_snes` lines stay the last two of `slot.state`**, after upstream's new
   `shelf_mode`, `kid_mode`, `kid_shelf`, `collection` and `gba_video` lines, so a Game Boy only card is upstream's text
   plus two lines.
4. **Named exceptions to upstream's test files** (`scripts/check-upstream-tests.sh`): upstream 1.15.2's own
   `durability.rs` does not compile (its `SlotState` literal lacks eight fields), so ours adds them; `layout_golden.txt`
   has our two `settings-long-list` hashes and `render_canvas_fill.rs` looks for the first menu row 26 pixels higher,
   both because the General page has the CPU row.
5. **Test lists** (`scripts/run-tests.sh`): `art_jobs` and `romm_gifts` run in both trees, `clock` runs one test at a
   time with the Gamebit tests (it sets the process wide TZ and flakes in both trees).

## Lessons

- A merge that takes upstream's side of a moved function can silently drop our edits to the old body: the Scale rows
  of the 23 shelves vanished from the hidden rows loop and only a test noticed. After a heavy rebase, diff the lines our
  series added against the new tree (`added lines of slot-vX..HEAD missing from the new files`).
- Do not let a structural merge helper treat a line that exists only in upstream as a deletion.
- After the host cores rebuild, macOS can kill every test that loads one ("Code Signature Invalid"): copy the dylib to a
  new file and `codesign --force -s -` it.
