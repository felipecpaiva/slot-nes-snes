# Decisions

One row per binding decision. Newest last.

| Date | Decision | Why |
|---|---|---|
| 2026-10-11 | Patch set over pinned slot releases, not a fork and not a shim core | slot's owner declined more systems (slot#30). A shim would squeeze NES/SNES into the 240x160 GBA frame and the GBA shelf |
| 2026-10-11 | Cores: fceumm (NES default), nestopia (alt), snes9x (SNES default), snes9x2005_plus (alt) | Defaults on muOS, Knulli, ROCKNIX and NextUI for H700-class devices |
| 2026-10-11 | Reference device: Anbernic RG35XXSP | The maintainer of this repo owns one |
| 2026-10-11 | Video: fixed per-platform 2x canvas (360x240 logical) | Smallest patch, GBA untouched. SNES hi-res blended 2:1 |
| 2026-10-11 | NES and SNES keep the GBA SP bezel on the RG35XXSP (640x427 window) | Same nostalgia look as GBA |
| 2026-10-11 | Real NES, Famicom, SNES and Super Famicom cart art with variants in v1 | Same depth slot gives GB, GBC and GBA carts |
| 2026-10-11 | SNES picture mode toggles with SELECT+X | L and R belong to the game on SNES; X is free in SELECT chords |
| 2026-10-11 | No new quick menu rows; NES/SNES shaders via SELECT+B/A | Keeps every upstream quick menu test unmodified |
| 2026-10-11 | Host struct field list untouched; new state in a side struct | Upstream in-source test `host_with()` lists every Host field |
| 2026-10-11 | macOS is the primary test job; Linux arm builds device artefacts | slot's host core tasks and headless render tests are macOS-only |
| 2026-10-12 | Two upstream test files get one token each (`| Platform::Nes` in chrome.rs, `| CartPlatform::Nes` in render_shelves.rs; Snes later) | Their helper matches over Platform are exhaustive, so a new variant cannot compile otherwise; check-upstream-tests.sh allows exactly these tokens |
| 2026-10-12 | `durability.rs` example value `cart_platform=nes` becomes `cart_platform=pce` | Upstream used `nes` as an unknown platform; NES is now real and must resume from `cart_platform=nes`; check-upstream-tests.sh allows only that value |
| 2026-10-12 | Upstream test edits happen only at five named sites, each checked exactly by `check-upstream-tests.sh`: `libretro.rs` one `#[cfg(test)] mod env_tests;`; `chrome.rs` `label_band` and `render_shelves.rs` `label_top` (`\| Platform::Nes` then optional `\| Platform::Snes` on the Game Boy arm, same with `CartPlatform`); `durability.rs` the one value `cart_platform=nes` to `cart_platform=pce`; `gpsp.rs` colour-correction match (`\| Core::Fceumm`, then optional `\| Core::Nestopia`, `\| Core::Snes9x`, `\| Core::Snes9x2005Plus` on the `Core::Mgba` arm). A future site may be added without asking only if it appends a variant token to an existing arm of an existing exhaustive match and is named in the guard; any other upstream test change stops and asks | Adding `Core::Fceumm` makes `gpsp.rs`'s match over `Core` non-exhaustive, so it cannot compile unchanged |
| 2026-10-12 | Carts show the real cartridge label art, never a screenshot; NES and SNES get a Cart Studio equivalent | Nostalgia: the shelf mirrors the physical carts. Asked the owner on slot #64 whether this lands as a PR to slot-cart-studio or a credited fork; a user-side fetch script (issue 41) is the fallback, and no Nintendo art is ever committed |
