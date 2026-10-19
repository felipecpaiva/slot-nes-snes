# 0088. Run our render tests on Linux under GLES2 through surfaceless Mesa EGL

- Status: Accepted. Amends [0035](0035-runner-sensitive-tests-info-on-ci.md)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0010](0010-macos-primary-ci.md), [ADR 0045](0045-layout-hash-tests-in-both-trees.md), [fork review 2026-10-18](../research/fork-review-2026-10-18.md) item 20, patches/0056-headless-egl.patch, [upstream PR text](../contributions/upstream-headless-egl-pr.md)

## Context

`HeadlessSurface` is macOS only (CGL, desktop GL 4.1 core), so every render test runs on the
macOS job, and ADR 0035 runs `retro_pipeline` there as information only because the runner's GPU
draws differently. The device runs GLES2, and our retro shaders are GLES programs that desktop GL
can let slip. cloudwithax/unslot (42ef0f8) and suprsomething/slot.advance (e761baa) both render on
Linux through Mesa's surfaceless EGL platform. llvmpipe is software and deterministic.

## Decision

- `slot-gfx/src/headless_egl.rs` (new): `HeadlessSurface` on Linux, a GLES2 context and a 720x480
  pbuffer on `EGL_PLATFORM_SURFACELESS_MESA`, with libEGL and libGLESv2 opened at run time like
  `fbdev.rs` (no new dependency). The libraries are never unloaded: Mesa crashes at process exit
  when they are. `lib.rs` gains two cfg lines.
- Our own render test files with no core (slot-gfx `gg_lcd`, `nes_pipeline`, `ps1_pipeline`,
  `retro_pipeline`, slot-ui `render_nes_region`, `render_nes_shelves`) widen their cfg to Linux.
  Upstream's render tests stay macOS only (CONTRIBUTING rule 2); widening them is the upstream PR.
- A guard test, `slot-gfx/tests/headless_egl.rs`, fails unless the context is real and reports
  OpenGL ES, because the other tests return early when no surface opens.
- The `device` CI job (Linux arm64, `rust:1-bullseye`) installs Mesa and runs the guard, then those
  six binaries, gating. slot crate render tests stay macOS only: they need ALSA headers and host
  cores the Linux job does not build.

## Consequences

- `retro_pipeline` gates CI again, on GLES2, the device's dialect. ADR 0035's informational run
  on macOS stays as it is.
- Our own tests carry no frame hashes, so no per-OS expected values are needed yet. Upstream's
  `layout.rs` hashes (ADR 0045) would need Linux values if upstream widens it.
- The Linux file is compiled into the device binary but never called there.
- Later, macOS CI minutes can drop by moving more render tests to the Linux job.
- Ported onto upstream main 1b20432 (ADR 0083) as is. The v1.7.0 build of this patch had committed
  two 55 MB process core dumps (`core` and `crates/slot-gfx/core`, likely from the Mesa exit crash
  above); the port leaves them out, so the patch is code only.
