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
