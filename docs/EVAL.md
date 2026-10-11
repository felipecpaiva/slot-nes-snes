# slot: adding NES + SNES: evaluation

Date: 2026-10-11. Repo: `BrandonKowalski/slot` at `9d7c795` (v1.6.0).

## Verdict

- **No upstream PR.** The owner closed issue #30 on 2026-10-09 with: *"slot will not be adding
  support for more systems."* Also #19: *"This is complexity I am not looking to add."*
- **The only code path is our own copy of slot** (a fork, or a patch set on its releases).
- **Durability cost = rebasing on a very active upstream.** 1.6.0 shipped 2026-10-10. `app.rs` is
  3,475 lines and most of our changes touch it, so expect conflicts on most upstream releases.
- **Zero-code NES today:** PocketNES runs NES ROMs as `.gba` files inside slot (pointed out on #30).
  No SNES equivalent exists.

## Architecture fit (good)

One `Platform` enum (`slot-store/src/platform.rs`) holds name, folder, extensions, picture size.
One `Core` enum (`slot-store/src/core.rs`). Cores load as libretro `.so` by name
(`slot/src/core.rs` `dylib_name`). Scanner loops `Platform::ALL` over `Games/<DIR>/`. So adding
`Nes`/`Snes` + `fceumm`/`snes9x2005` is the right shape. Frontend cost per platform is about one
extra directory scan.

## Step 0: silent-fallthrough sites (fix before adding variants)

These compile fine with new variants and quietly treat NES/SNES as Game Boy:

| Site | Problem |
|---|---|
| `slot-store/src/scan.rs:21-32` `read_header` | `_ =>` runs the GB title parser on NES/SNES ROMs |
| `slot/src/core.rs:128` `palette_for` | `!= Gba && dmg_only(rom)` reads byte 0x143 of a NES/SNES ROM, can push mGBA palette options |
| `slot/src/app.rs:855, 2643, 2701` | `!= Platform::Gba` means "is Game Boy" today |
| `slot-store/src/core.rs:46` `Core::runs` | `Mgba => true` claims mGBA runs every platform |

Turn each into an exhaustive `match` so the compiler forces a decision.

## Hard blockers

| Area | Where | Why |
|---|---|---|
| Frame size | `slot-retro/src/libretro.rs:321-330` | `video_refresh` clamps to 240x160. NES/SNES are 256 wide; SNES hi-res is 512. Same constants size `emu.rs:151` `Frames::new`, `thumb.rs`, `mock.rs` |
| Geometry | `libretro.rs:76-213` `environment` | `SET_GEOMETRY` / `SET_SYSTEM_AV_INFO` return false; SNES cores switch resolution mid-game |
| Buttons | `slot-retro/src/core.rs:27-42` | X/Y are taken as turbo A/B. SNES needs real X/Y. Make turbo per-platform (off for SNES) |
| Core picker | `slot/src/core_picker.rs:115-116` | hardcoded Left = mGBA, Right = gpSP |
| Cart art | `slot-ui/src/cart.rs:83` `Shape`, `shell.rs:91` | only GBA/GB shapes. NES/SNES carts are a design job, and this is the "feeling" of the app |
| Shaders | `slot-store/src/slot_state.rs:53-54` + `shader_gba`/`shader_gb` | per-platform lists + per-platform state fields |
| Core build | `cores/*/build.sh`, `taskfile.yml`, `.github/workflows/release.yml` | new pinned build recipes for the H700 (arm64, cortex-a53) |

## Checked (by reading code, not by running)

- **Audio: OK.** `emu.rs:522-531` builds `Resampler::new(core_hz, device_hz)` from the core's own
  `av.sample_rate`. A 32,040 Hz SNES core is converted to the device rate. The fixed `GBA_HZ` is
  only the device open rate.
- **Rewind: OK.** `rewind.rs:3` is a fixed 20 MB byte budget. Bigger SNES states mean fewer seconds
  of rewind, not a failure.
- **Device performance: unverified.** Cannot measure from here. snes9x2005 and fceumm are the usual
  choices on Cortex-A53 handhelds; needs an on-device check.

## Rough size of the fork

Step 0 + frame size + geometry + per-platform turbo/shaders + two core recipes: a few days of code.
Cart art for NES/SNES: separate design effort. Plus the ongoing rebase cost above.

## Extension (shim) option: no fork, no upstream change

Same trick slot plays on BaseOS (it takes over `System/launch_frontend.sh`), one level down:
replace slot's `System/gpsp_libretro.so` with a small **dispatcher core**. It forwards real GBA
games to the real gpSP (renamed, e.g. `gpsp_real_libretro.so`) and NES / SNES games to
fceumm / snes9x2005. slot does not know. The libretro ABI is the only contract.

Why gpSP, not mGBA: mGBA is the default core and carries the link-cable patches. gpSP is only a
per-cart choice (`Config/selected_core.txt`, survives updates), so the installer pins each NES/SNES
stem to gpSP there. GBA games on mGBA are untouched.

### What was checked (code reading)

| Question | Answer | Evidence |
|---|---|---|
| Picture | **Hard limit.** slot caps every frame at 240x160; the shim must downscale. SNES 224 lines / NES 240 lines -> 160 (about 30% of lines lost). At 4:3 inside the GBA frame: 213x160, shown about 568x427 on a 640x480 panel. Small RPG text suffers | `libretro.rs:321-330`, `video_mode.rs:43` |
| X / Y buttons | slot strips X/Y before the core in both turbo modes. **But slot does not grab input exclusively** (no `EVIOCGRAB`), so the shim can read X/Y straight from evdev. Needs Turbo set to Off in slot | `slot-retro/src/core.rs:27-42`, grep `EVIOCGRAB` = none |
| RTC in .sav | Only appended if the core exposes `MEMORY_RTC`. Shim reports none -> SNES saves stay clean | `libretro.rs:646-661` |
| gpSP options | slot sets `gpsp_serial`, `gpsp_rtc_time_source`, `gpsp_boot_mode`, `gpsp_color_correction`, `gpsp_frameskip`. Shim forwards to real gpSP, ignores for NES/SNES | `slot/src/core.rs:186-206` |
| Link menu | Needs a GBA header code that carries link; NES/SNES fail it -> "No link" toast | `app.rs:2701-2715` |
| Audio, rewind, save states | Generic, follow the core's own rate and state size | see above |

### Costs / risks

- A slot update replaces `System/` -> the shim is wiped and must be reinstalled. Installer must tell
  shim from a new real gpSP by `retro_get_system_info().library_name`, not by file name.
- Games sit on the **GBA shelf as GBA carts**. ROMs need a fixed marker name (`name.sfc.gba`,
  `name.nes.gba`; NES also has the iNES magic). The GBA-header title may be garbage; label art
  still matches by file name.
- Core picker: if the user flips the cart to mGBA, the game does not boot.
- Etiquette: a separate GPL mod. Its README must send bugs to its own repo, not slot's tracker
  (owner already said no to more systems).

### Next step if chosen

One-ROM spike on the host: build the shim as a dylib, point `SLOT_CORE` at it in the host app,
run one NES ROM. Proves dispatch + downscale before more work.

## Own shelves per system (NES / SNES next to GBA / GB / GBC)

The shelf grouping is the `Platform` enum. Shelves are built from `Platform::ALL`
(`app.rs:365`), scanned from `Games/<dir_name>/` (`scan.rs:65`), and per-platform settings are
keyed by `dir_name()` (`slot_state.rs:235-243`). Core per system = `Core::runs` /
`Core::default_for`. 20 source files use `Platform`.

**It is compile-time only.** No config file or folder adds a shelf. So this cannot be done by an
add-on file; it needs a changed `System/slot` binary.

Lightest way to own that change: a **patch set over a pinned slot release**, the same way slot
itself ships mGBA (`cores/mgba/*.patch` over a pinned upstream commit, built in CI). Our repo holds
`patches/*.patch` + a build that outputs a replacement `System/slot` + the NES/SNES cores. Keep the
patches small to cut conflicts: NES/SNES data lives as `Platform` methods (picture, extensions,
shaders, cart shape, turbo on/off) in new code, `app.rs` only gets the exhaustive-match fixes.

This also removes the shim's two big costs: the 240x160 squeeze (fix the frame buffer) and games
sitting on the GBA shelf. Cost: patches must be re-checked on each slot release.
