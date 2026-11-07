# 0110. Rebase the patch set onto slot v1.14.0, hide upstream's slot updater and keep the BaseOS check

- Status: Accepted. Amends [0109](0109-rebase-to-slot-v1-9-0.md) when accepted
- Date: 2026-11-06
- Deciders: maintainer (Felipe Paiva)
- Related: [REBASE.md](../REBASE.md), [ADR 0109](0109-rebase-to-slot-v1-9-0.md), [ADR 0108](0108-console-buttons-on-the-in-game-controls-page.md), patch 0157, `SLOT_PIN`

## Context

Upstream tagged v1.10.0 on 2026-10-28, v1.11.0 on 10-29, v1.12.0 on 10-30, v1.13.0 on 11-01 and v1.14.0 on
11-04 (commit e66715d, tarball sha256 1e727299...980c3). Together they are 109 commits and 455 files past our
v1.9.0 pin (20703ed): 61,000 new lines, 5,400 of them in `app.rs`. `MGBA_COMMIT` and `GPSP_COMMIT` did not move.
`GAMBATTE_COMMIT` (77f2567) is new. The dry run stops at patch 0001 (3 files), so this is a heavy rebase:
the 156 patches were re-applied one by one (39 of them conflict, 122 files changed on both sides), then one
adaptation patch (0157) was added, as 0155 did for 1.9.0.

| Upstream | What it touches in ours |
|---|---|
| 1.10 `Scale`, `Stretch`, Frame Blending | `video_mode::source_rect` became `picture_for(platform, picture, canvas, mode, scale, stretch)`; our canvas, Crop, 4:3, Actual scale and arcade upright rects are folded into it. `source_rect` stays as a thin wrapper for the retro shelves |
| 1.10 Game Boy Advance Video shelf (`Platform::Gbav`) | a 27th shelf, second in the classic order, sharing the GBA Screen page, Scale row and shader; release date 2004-05 |
| 1.10 screenshots, 1.12 Reset Game, Sunlight, 1.11 FF Toggle and 1.5x | new `Shortcut` and `QuickRow` rows; none starts on one of our chords |
| 1.11 audio device stays open with headphones, CPU back to fixed speed | our Hold (patch 0018) and CPU row stay; no overlap found in the loop |
| 1.13 Wi-Fi, Network menu, Gamebit, Cart Studio, updater | new modules; Studio, the unwrap scene and the house label are Game Boy shaped and take a GBA sized fallback on our shelves |
| 1.14 Gambatte core, Game Boy audio, ROM header index, label cache | `Core::Gambatte` is third in `Core::index`, `Core::EVERY` follows it, `Core::pair(platform)` replaces our default core fn, `Core::partners` is ours |
| 1.14 Remove Recent on X | a shelf binding, no clash with ours |

## Decision

1. **Hide the slot update row, keep the BaseOS one.** The updater reads `slot-cfw.fyi/versions.json` and installs
   upstream's zip from `BrandonKowalski/slot`, which would replace this build with plain slot and drop the
   26 added shelves. (Open: the patch for it is not written yet, see below.)
2. **Scale, Stretch and Frame Blending are Game Boy family rows for now.** `Platform::classic()` is true for GBA,
   GBAV, GB and GBC; the retro shelves keep the picture modes they had (Actual, Stretch, Crop, 4:3) and hide the
   three new rows. Extending the rows to the 23 added shelves is a follow-up, on purpose not part of the rebase.
3. **`Core::partners(self)` stays ours** (the pair a seated core belongs to) and `Core::pair(platform)` is
   upstream's (the pair a platform offers). `PairFaces` hands the picker whole socket and chip lists indexed by
   `Core::index`, as upstream draws them.
4. **`step_emulator` now returns "late"** (upstream changed it); our tests assert `!step_emulator(..)`.

## Known upstream failures on a macOS host

`boot_drops_index_entries_for_games_no_longer_on_the_card`, `keeping_every_entry_leaves_the_index_saved`,
`house_label::tests::a_game_boy_label_is_the_shape_of_its_own_well` and `the_link_screen_uses_the_whole_4_by_3_panel`
fail on pristine v1.14.0 here too (two of them depend on test order in a shared index). They are not ours.

## Open work (checked off as it lands)

- [x] `task check` through the test, format, guard, lint, touch point and harness steps (2026-11-06): the
      upstream failures on a macOS host (two header index tests, the link screen frame, a house label shape)
      run in both trees, the Gamebit tests run one at a time, the harness had to learn that `step_emulator`
      returns late and that the Game Boy Advance shader list is one short on a 3:2 panel.
- [x] Patch 0158 hides the slot update row (`update_slot_hidden.rs` tests it, upstream's update tests use a
      fake runner and are untouched).
- [x] Gambatte host dylib fetched through upstream's task and pinned (`gambatte_host_sha256_arm64`).
- [x] Gambatte and Gamebit's web page in the dist: device `.so` from upstream's `core:gambatte`,
      `gambatte_tarball_sha256` pin, `cores.sha256`, `zip-check.sh`, LICENSING, SUPPLY-CHAIN, Bun in CI.
- [x] Device gate on the RG34XXSP (2026-11-06): boots in 3.9 s on the second boot (4.1 s on 1.9.0); the
      controls check answers every button on all 23 added shelves and on Game Boy and Game Boy Color with
      Gambatte and mGBA (`docs/device-controls/2026-11-06/`).
- [ ] CI on PR 186, merge, tag `v1.14.0-ns.1` (Felipe pushes it).
- [ ] Not tested on the device: Network, Check for Updates showing only BaseOS (needs Wi-Fi, a unit test
      covers it), Gamebit and Cart Studio with the added shelves.
- [x] The two Gamebit sound tests (`server_ui` buzz and tear, 2026-11-07): a frame step costs the same in both
      trees (600 steps of `advance_at` and `render` on `server_ui`'s rig: 7 and 9 microseconds, render about 50
      in both), so our patches add no work per frame. The patched tree boots a little slower (27 shelves), and
      the tests tie the scene clock to wall clock, so they only flake under the parallel run. They stay in the
      serial list of `scripts/run-tests.sh`; closed as contention.

## Accepted limit

The first start after updating from 1.9.0 logged `label cache: 11010 new labels`: slot 1.14 converts the old
`.rgba` cache files to its `.lz4` format at boot (the card then held 1,689 `.lz4` and 72 orphaned `.rgba` files
for the GBA shelf, the orphans being games renamed or removed since). That is upstream's conversion, not ours:
it is file work on an SD card and took about 10 minutes for 12,800 files, and the games tested during it did
not start. A second boot was fast. An earlier version of this ADR said our caches were not converted; that was
wrong. It is in the release notes under Known limits. Slot could convert in the background without holding
games back, which would be an upstream issue.

## Follow-up: Scale, Stretch and Frame Blending on the added shelves

Not built yet, proposed (a separate pull request):

- **Scale** on every added shelf's Screen page and in-game Screen page: SP Screen (today's picture, the
  default), Integer and Fit. `video_mode::picture_for` already takes a `Scale`; the shelves pin it to the
  default today. Needs one state field per shelf, like `scale_gba`.
- **Stretch** is not added: the Picture row (Stretch, Actual, Crop, 4:3) already covers it, and a second row
  for the same thing would confuse.
- **Frame Blending** is not added: it is a core option on mGBA, gpSP and Gambatte, and none of our cores has one.

## Consequences

Patch history for 0002 to 0156 carries a few glued or wrong lines that the adaptation patch (0157) repairs
(`Platform::GbavPs1`, `Shortcut::GuidePictureNext`, `Action::ForgetRecentVideoModeToggle` and similar, from the word
level merge helper used during the rebase). They never build on their own; only the series as a whole does,
like 0155 before it. The next rebase should fold them back with `--fixup`.
