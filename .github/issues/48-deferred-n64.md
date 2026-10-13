---
title: "DEFERRED: Add N64 as a platform, after a device spike proves it"
phase: 6
area: cores
type: chore
size: L
depends_on: [32-phase-6-deferred]
---

## Why
**Deferred, not in v1.** The maintainer asked whether the RG34XXSP can run N64 like NES and SNES. The research (docs/research/n64-feasibility.md, 2026-10-13) says "go with limits", but only after a spike; the maintainer chose to park it (2026-10-13). docs/PLAN.md lists more systems as out of scope, so starting this needs an ADR.

## Findings (from the research)
- The RG34XXSP has two analog sticks plus L2/R2/L3/R3. Unknown: whether BaseOS exposes them as evdev axes. slot reads only the d-pad today.
- slot has no libretro hardware rendering (`SET_HW_RENDER`); N64 cores need it. Smallest design: an offscreen EGL context with an FBO on the `slot-emu` thread and a `glReadPixels` readback into the existing frame buffer.
- Only usable core without Vulkan: mupen64plus-next with GLideN64 (GLES2/3), built for `arm64_cortex_a53_gles2` (needs an exception to ADR 0002's build rule). Licences: GLideN64 GPL-2.0-only, covered by the separate-program stance used for snes9x.
- Saves fit slot's SAVE_RAM path. Rewind does not (a state is about 16.8 MB against a 20 MB ring). Fast-forward is not promised.
- H700 reports: Super Mario 64, Mario Kart 64, Star Fox 64 full speed; GoldenEye, Perfect Dark, Conker, Majora's Mask below.
- About 10 to 14 patches. Needs its own frontend-cost budget (readback) and a gate limited to named light titles.

## Scope (when picked up)
- [ ] Spike outside slot, 1 to 2 days: cross-build mupen64plus-next GLES2, a tiny frontend with an offscreen EGL context on a non-main thread and per-frame `glReadPixels`, timing logs. Run Super Mario 64, Mario Kart 64, Ocarina of Time, GoldenEye for 3 minutes each. Record the GL version and extensions, check for Vulkan, dump evdev while moving both sticks.
- [ ] Go only if Super Mario 64 and Mario Kart 64 run at full speed, readback is under 3 ms, and both sticks show as axes. Otherwise close as won't-do with the numbers.
- [ ] On go: an ADR that brings N64 into scope, then re-plan into a new phase with its own tickets.

## Acceptance
- [ ] Spike numbers recorded in docs/research/n64-feasibility.md and a go or no-go recorded as an ADR.
