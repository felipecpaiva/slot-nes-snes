# PR title

Run the render tests on Linux through surfaceless Mesa EGL

# PR body

## Problem

`HeadlessSurface` is macOS only (CGL, desktop GL 4.1 core). Every render test is gated
`#![cfg(target_os = "macos")]` (`slot-gfx/tests/layout.rs`, `slot-ui/tests/render_row_edges.rs`,
`slot/tests/render*.rs`), and `slot-gfx/tests/pipeline.rs` has no cfg at all, so it does not build
on Linux. The device draws with GLES2, so a shader that desktop GL accepts but GLES2 rejects is only
found on the device, and a Linux box (or a Linux CI runner) cannot run any of these tests.

## Change

- New `crates/slot-gfx/src/headless_egl.rs`: `HeadlessSurface` on Linux. It opens libEGL and
  libGLESv2 at run time, the same way `fbdev.rs` does (no new dependency), gets the display with
  `eglGetPlatformDisplay(EGL_PLATFORM_SURFACELESS_MESA)`, and makes a GLES2 context current on a
  720x480 pbuffer. `proc_address` looks in libGLESv2 first, then `eglGetProcAddress`. `swap` is a
  `glFlush`, as on macOS. The two libraries are never unloaded: Mesa 20.3 crashes at process exit
  when libEGL is closed before its exit handlers run.
- `crates/slot-gfx/src/lib.rs`: `mod headless_egl` and `pub use headless_egl::HeadlessSurface`
  under `#[cfg(target_os = "linux")]`, so the tests use the same name on both systems.
- The render test files widen `#![cfg(target_os = "macos")]` to
  `#![cfg(any(target_os = "macos", target_os = "linux"))]`, and `pipeline.rs` gains that line.
- `crates/slot-gfx/tests/headless_egl.rs` (Linux only): the surface opens and `GL_VERSION` starts
  with `OpenGL ES`. The render tests return early when no surface opens, so without this a machine
  with no Mesa driver would pass them all without drawing.

Mesa on Debian bullseye (20.3, llvmpipe) needs `libegl1 libegl-mesa0 libgles2 libgl1-mesa-dri`
and no `/dev/dri`; `EGL_PLATFORM` does not need to be set.

## What changes for the tests

- llvmpipe is software, so a Linux run draws the same frame every time.
- `layout.rs` compares frames against FNV hashes taken on macOS. GLES2 on llvmpipe can round
  differently, so those tests need their own expected value on Linux (a `cfg` on the constant) or
  stay macOS only. I would keep `layout.rs` on macOS in this PR and add Linux hashes separately once
  they are stable across two runs.
- Tests that need a libretro core (`render.rs`, `render_picture_modes.rs`) still need the core
  built for Linux; they skip as today when it is missing.

## How it was tested

On v1.7.0 with the slot-nes-snes patch set applied, on Debian bullseye arm64 in Docker (Mesa
20.3.5, llvmpipe, no display), with the cfg widened; to be rerun on main before sending:

- `slot-gfx/tests/pipeline.rs`: 21 passed.
- `slot-ui/tests/render_row_edges.rs`: 3 passed.
- `slot-gfx/tests/layout.rs`: 8 passed, 2 failed, the two FNV hash tests
  (`a_framed_frame_on_a_4_by_3_panel_is_todays_frame` and
  `a_framed_frame_after_a_native_one_is_todays_frame_again`). Linux draws that frame as
  `0xd6f695d1d775525d`. These are the tests that need a per-OS expected value (above).
- The guard test passed, and so did our patch set's own core-free render tests, twice in a row.

`cargo clippy -p slot-gfx --all-targets` is clean on Linux. Nothing changes on macOS: the new file
is not compiled there.

## Credit

After cloudwithax/unslot 42ef0f8 and suprsomething/slot.advance e761baa (both GPL-3.0), which do
the same on their forks.
