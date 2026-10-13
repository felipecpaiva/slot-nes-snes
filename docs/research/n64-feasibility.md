# N64 on slot-nes-snes: feasibility research (2026-10-13)

Read-only research. Code refs are to `work/slot` (patched slot
v1.6.0 + patches 0001-0021) unless noted. Web evidence on per-game H700 performance is mostly from
secondary review/guide sites and is marked as such; the device spike in section 6 is the primary
evidence we do not have yet.

## TL;DR

- **Correction to the premise:** the RG34XXSP *has* dual analog sticks (Hall), plus L2/R2/L3/R3. The
  stickless clamshell is the newer **RG SP**, not the RG34XXSP. RAM is 2 GB on early units, 1 GB on
  units after Jan 2026.
- **slot has no libretro hardware rendering at all.** Software framebuffers only, a GLES2 compositor
  context on the main thread, cores on a separate `slot-emu` thread. Every usable N64 path on the
  H700 without Vulkan needs GL (GLideN64 on GLES2/3). This is the single big item.
- The H700 can run the light end of the N64 library at full speed (SM64, MK64, OoT, Star Fox 64,
  Pokemon Stadium per guides), GoldenEye/Perfect Dark/Majora's Mask need frameskip and still dip.
  It will not meet the NES/SNES bar ("every gate title full speed, zero underruns").
- **Recommendation: go-with-limits, gated by a spike** that proves (a) GLideN64 GLES2 builds and runs
  at speed on BaseOS's Mali fbdev blob through an offscreen EGL context, and (b) the sticks are
  readable as evdev axes on BaseOS. Kill if either fails.

## 1. slot's video path and other N64 needs

### What slot supports today

- Environment callback `environment()` handles only: GET_CAN_DUPE, SET_PIXEL_FORMAT (XRGB8888,
  RGB565), GET_SYSTEM/SAVE_DIRECTORY, GET_VARIABLE(_UPDATE), SET_VARIABLES, GET_RUMBLE_INTERFACE,
  GET_LOG_INTERFACE, SET_AUDIO_BUFFER_STATUS_CALLBACK, SET_NETPACKET_INTERFACE, plus (patch 0006)
  SET_GEOMETRY, SET_SYSTEM_AV_INFO, GET_AUDIO_VIDEO_ENABLE. Everything else returns false.
  `crates/slot-retro/src/libretro.rs:77-218`, constants `crates/slot-retro/src/ffi.rs:9-19`,
  `crates/slot-retro/src/canvas.rs:9-11`.
- **No SET_HW_RENDER (14), no GET_CURRENT_FRAMEBUFFER / GET_PROC_ADDRESS callbacks, no
  SET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE, no SET_CORE_OPTIONS(_V2)** (mupen falls back to
  SET_VARIABLES, so options still work).
- `video_refresh` copies pixel data into a CPU buffer `Host.video` (GBA 240x160x4, or the
  360x240 canvas via `canvas::copy_centred`). `libretro.rs:315-366`. It only null-checks `data`:
  a HW-rendered core passes `RETRO_HW_FRAME_BUFFER_VALID` = `(void*)-1`, which this code would
  dereference and crash. Any HW patch must special-case that sentinel first.
- The core runs on its own thread: `std::thread::Builder::new().name("slot-emu")`
  `crates/slot/src/emu.rs:188-190`. Frames are handed over as bytes (`Frames::new(canvas_w*canvas_h*4)`,
  `emu.rs:150-151`).
- Device GL: `FbdevSurface` dlopens libEGL, Mali fbdev window surface, **ES2 context, no share
  context** (`crates/slot-gfx/src/fbdev.rs:218-231`), current on the main thread. Host (macOS)
  uses glutin with desktop GL 3.3 core (`crates/slot-gfx/src/host.rs:~60-72`), shaders compiled
  with `#version 330 core` or the ES variant (`crates/slot-gfx/src/shaders.rs:3-12`).
- Input: `input_state` answers only `RETRO_DEVICE_JOYPAD` (`libretro.rs:384-399`); anything else,
  including RETRO_DEVICE_ANALOG, returns 0. `ButtonMask` is a u16 of 12 GBA/SNES buttons
  (`crates/slot-retro/src/core.rs:10-25`). Device evdev reads keys and only ABS_HAT0X/HAT0Y (the
  d-pad) (`crates/slot/src/input/evdev.rs:12-26`, `input/device.rs:118-122`). No stick axes at all.
- Saves: `save_ram()` reads `RETRO_MEMORY_SAVE_RAM` (+RTC) (`libretro.rs:680-700`). Works as-is for
  mupen64plus-next, which exposes one `saved_memory` blob = SRAM + EEPROM + FlashRAM + 4 controller
  paks (mupen `libretro/libretro.c:2108-2129`, `format_saved_memory` at :1781-1800). Rough size a
  few hundred KB. Controller-pak saves come for free.
- Save states / rewind: mupen64plus-next `retro_serialize_size()` = 16,788,288 + 5,124 bytes
  (~16.8 MB) (mupen `libretro.c:2133-2136`), and serialize co-switches into the game thread and
  binds the GL state. slot's rewind ring is 20 MB total (`crates/slot/src/rewind.rs:3`) and the
  perf routine serializes every frame. **Rewind is not viable for N64** (one uncompressed state is
  84% of the ring; per-frame 16.8 MB serialize + lz4 on an A53 alone eats most of a frame).
  Manual save states are fine (16.8 MB write, plus a thumbnail). Polaroid thumbnails need the
  frame in CPU memory.
- Fast-forward: N64 on H700 is at or below 1x already for many titles; FF is effectively
  "uncapped", expect 1.0-1.5x on light titles. Not a parity row we could promise.

### Option for adding HW render, smallest first

**A. Offscreen context on the emu thread + readback (recommended).**
On `slot-emu`, create a *separate* EGL context (pbuffer surface, GLES2 or GLES3) when a core asks
for SET_HW_RENDER. Give the core an FBO via `get_current_framebuffer`, `eglGetProcAddress` via
`get_proc_address`, call `context_reset` after load. On `video_refresh(HW_FRAME_BUFFER_VALID, w, h)`
do one `glReadPixels` (320x240 RGBA = 300 KB) into `Host.video`. Everything downstream (Frames,
canvas, shaders, thumbnails, polaroids, harness frame dumps) stays a CPU-pixel pipeline, untouched.
- Touches: `slot-retro/src/libretro.rs` (env cases, video_refresh sentinel, context lifetime on
  load/unload/serialize), `ffi.rs` (HwRenderCallback struct), a new file for the EGL pbuffer
  context (new file, not an upstream touch point), a GL entry on host via CGL/glutin headless.
  `slot-gfx/src/fbdev.rs` probably needs only an exported EGL loader, or none if the new file
  dlopens libEGL itself.
- Cost: glReadPixels is a GPU->CPU sync stall on Mali every frame (estimate 1-3 ms, unmeasured).
  That is new frontend cost that GBA does not pay and NES/SNES do not pay, so it does not break
  their budgets, but N64 needs its own budget line.
- Risk: whether BaseOS's Mali fbdev blob allows a second context on another thread with a pbuffer
  surface (EGL_PBUFFER_BIT config). Most Mali blobs do; must be proved in the spike.

**B. Shared context, zero-copy texture to the compositor.** `eglCreateContext(..., share_context=
compositor_ctx)` on the emu thread, core renders into an FBO texture, compositor samples it.
Needs fences (EGL_KHR_fence_sync) across threads, changes to `fbdev.rs:221` (share context),
to the pipeline (texture input instead of upload), and breaks thumbnails/polaroids/frame dumps
which all assume CPU pixels (would need a readback anyway). Bigger upstream touch, saves maybe
1-3 ms. Only if A's readback cost is proven too high.

**C. Run the core on the main thread.** Rewrite of `emu.rs` (1,318 lines) threading model. No.

Hard requirements for Option A (from mupen `libretro.c`):
- **context_reset is mandatory, not optional.** Under GLideN64, load_game sets
  `first_context_reset = true` and defers `emu_step_initialize` until the frontend calls
  `hw_render.context_reset` (`libretro.c:~1987-1991`). No reset = game never starts.
- **FBO must honour `hw_render.depth`/`stencil`** (GLideN64 needs a depth attachment).
- **Readback must flip rows when `bottom_left_origin` is true** (GL convention), or every
  polaroid, thumbnail and frame dump is upside down.
- **Every core call on the context-owning thread.** `retro_serialize` does
  `glsm_ctl(GLSM_CTL_STATE_BIND)`; run, serialize, unserialize, unload must all happen on
  `slot-emu`. slot's Worker already funnels core calls through that thread (Cmd channel,
  `emu.rs:180-190`), so this holds if nothing calls the core from main.

Note: mupen64plus-next's GLideN64 path optionally runs a threaded renderer on libco coroutines
(`libretro.c:1951-1956`); keep `mupen64plus-ThreadedRenderer = False` for a simpler first cut.

### Frame size and pixel format

With GLideN64 at native 320x240 (mupen option `mupen64plus-43screensize = 320x240`), the readback
frame is 320x240, which fits the existing **360x240 fixed canvas (ADR 0004 Option A)**: a 2x into
the 720x480 logical space = 640x480 centred on the RG34XXSP panel. **Issue 36 Option B is not
needed.** Pixel format: readback is RGBA8888; convert to the XRGB8888 buffer (BGRA swizzle) or
read `GL_BGRA_EXT` if the blob supports it. mupen sets the pixel format itself (`libretro.c:721`).

## 2. Input

- **RG34XXSP has dual analog sticks** (Hall), L1/R1/L2/R2/L3/R3:
  https://heldgames.com/comparisons/anbernic-rg-sp-vs-rg34xx-sp ("RG34XX SP: Analog Sticks 2
  (dual)"; "RG SP: None (D-pad only)"), https://retrohandhelds.gg/anbernic-rg34xxsp-first-impressions/,
  https://retrocatalog.com/retro-handhelds/rg-34xxsp. RAM "1 GB (2 GB before Jan 2026)" per heldgames.
- Natural mapping: left stick = N64 stick (RETRO_DEVICE_ANALOG index 0), right stick = C-buttons
  (mupen's default maps C to the right analog), A/B, Z = L2, L/R = L1/R1, Start.
- **Unknown, must test:** how BaseOS exposes the sticks. Reports say stock firmware on H700 stick
  models has cardinal snapping ("acts more like a D-pad") that muOS/Knulli fix
  (https://retrohandhelds.gg/?p=8500 RG40XXV coverage). The spike must run an evdev dump on
  BaseOS and look for ABS_X/ABS_Y/ABS_RX/ABS_RY and their ranges (slot already has
  `crates/slot/src/input/trace.rs` for traces).
- Stickless fallback (other H700 devices, RG SP): d-pad as analog (full deflection), C-buttons on a
  modifier (e.g. hold R2 + face buttons), the common firmware approach. Playable without a stick:
  turn-based/menu or d-pad-friendly titles (Pokemon Stadium/Puzzle League, Paper Mario, Dr. Mario
  64, Bomberman 64, Mario Party menus); everything 3D-camera heavy is poor. Since the reference
  device has sticks, the fallback is a nice-to-have, not v1.
- slot work: new `RETRO_DEVICE_ANALOG` answer in `input_state`; axis plumbing from evdev ->
  input thread -> emu `Shared` (currently a single `AtomicU16` input, `emu.rs:153`) -> Host. That is
  a widening of the input channel (4 x i16 axes) which touches upstream input and emu code.

## 3. Cores

| Core | Renderers | Without Vulkan on H700 | Licence |
|---|---|---|---|
| mupen64plus-next (`libretro/mupen64plus-libretro-nx`, active, pushed 2026-10-01) | GLideN64 (GL/GLES2/GLES3, HLE), angrylion (software, only when built with `HAVE_THR_AL`), ParaLLEl-RDP (Vulkan) | **GLideN64 GLES2/3 only.** The `arm64_cortex_a53_gles2` / `_gles3` targets (Makefile:347-366) do not set HAVE_THR_AL, and angrylion is far too slow on an A53 anyway. ParaLLEl needs Vulkan (`libretro.c:1849-1876`). If GL negotiation fails, load_game returns false (`libretro.c:1970-1975`). | Repo SPDX GPL-2.0; mupen64plus-core headers "version 2 ... or (at your option) any later version". **GLideN64 LICENSE says "GNU General Public License version 2"** with no "or later" (gonetz/GLideN64 LICENSE). |
| parallel-n64 (`libretro/parallel-n64`, active) | gln64, glide64, rice (GL), angrylion (sw), ParaLLEl-RDP (Vulkan) | GLES2 gln64/glide64/rice. Older plugins, less compatible; libretro docs direct improvements to mupen64plus-next (https://docs.libretro.com/library/mupen64plus/). | GPL-2 family (no SPDX on repo) |
| Mupen64Plus standalone (what ROCKNIX ships as Mupen64Plus-SA) | GLideN64/rice | Not a libretro core, cannot load in slot | GPL-2+ |

- **Vulkan:** stock BaseOS is Linux 4.9.170 + Mali fbdev blob (docs/PERFORMANCE.md device record);
  a Vulkan ICD was not found in any source and is expected absent (not verified on device; the
  spike checks). ROCKNIX's mainline Panfrost reports GL 3.1/GLES 3.1 for the H700
  (https://rocknix.org/devices/anbernic/rg34xx/), also no Vulkan listed; PanVK on Bifrost G31 is not a
  usable path. ParaLLEl is out.
- **Build:** use mupen64plus-next with `platform=arm64_cortex_a53_gles2` (or gles3 if the blob reports
  ES3). This contradicts ADR 0002's "make platform=unix, never platform=arm64" rule; needs its own
  ADR exception (or `platform=unix FORCE_GLES=1 WITH_DYNAREC=aarch64`). Links `-lGLESv2` against the
  device's Mali libGLESv2. Host build: macOS arm64 with desktop GL core (libretro buildbot ships an
  osx arm64 build, so it compiles; GLideN64 needs a GL 3.3 core context there).
- **Licence vs slot (GPL-3.0-or-later):** GLideN64 being GPL-2.0-only is incompatible with GPL-3 *if
  combined into one program*. The project already ships snes9x (non-commercial, not GPL-compatible)
  on the stance "separate program across the libretro C ABI" (ADR 0002, LICENSING.md); mupen64plus-next
  fits the same stance and is strictly less restrictive than snes9x. Needs a LICENSING.md section and
  a source tarball like the others. Not a blocker under the existing stance.

## 4. Real performance on H700 devices

Treat as secondary-source evidence: the table rests mostly on one aggregator (heldgames.com), which
contradicts itself on OoT, plus DROIX. Retro Game Corps' H700 family guide only marks N64 with "cannot
play every game at full speed" and notes the POWER-tap d-pad/stick swap on stickless models
(https://retrogamecorps.com/2024/06/07/anbernic-rg35xx-family-starter-guide/). Reddit is not
reachable from this tool. The spike is the real measurement. No first-hand H700 benchmark tables from muOS/Knulli/ROCKNIX docs
were found (their docs list cores and mappings, not speeds).

| Game | Result on H700 | Core/settings | Source |
|---|---|---|---|
| Super Mario 64 | full speed | mupen64plus-next, GLideN64, dynarec, 320x240 | heldgames N64 guide; droix RG35XX review ("runs well") |
| Mario Kart 64 | full speed / "acceptable" | same | heldgames N64 guide; heldgames best-N64 guide |
| Ocarina of Time | full speed per one guide, "drops frames" per another | same | heldgames N64 guide vs heldgames best-handhelds guide (conflict) |
| Star Fox 64 | full speed | same | heldgames N64 guide |
| Pokemon Stadium 1 & 2 | full speed | same | heldgames N64 guide |
| Super Smash Bros | full speed 1v1 only | same | heldgames N64 guide |
| Majora's Mask | frameskip 1, slowdowns in Clock Town | same | heldgames N64 guide; droix ("struggles") |
| Conker's Bad Fur Day | struggles | - | droix RG35XX review |
| GoldenEye 007 | 70-90% depending on level | frameskip | heldgames N64 guide |
| Perfect Dark | 60-75% with frameskip | frameskip | heldgames N64 guide |
| RG40XXV generally | "varies by game, frameskip needed for demanding games" | - | droix RG40XXV review |

Settings consensus: dynarec on (interpreter 3-5x slower), native 320x240 (upscaling "tanks"
performance), GLideN64 default, frameskip 1 for 80-90% titles. ParaLLEl "too demanding for the
H700". Standalone Mupen64Plus sometimes faster than the libretro core (lower overhead) - slot can only
use the libretro core, so slot will be at or below the RetroArch numbers, plus the readback cost.

Sources: https://heldgames.com/guides/n64-emulation-handheld ,
https://heldgames.com/guides/best-handhelds-n64-emulation ,
https://droix.net/blogs/anbernic-rg35xx-plus-review/ , https://droix.net/blogs/en-au/rg35xx-review/ ,
https://rocknix.org/devices/anbernic/rg34xx/ , https://docs.libretro.com/library/mupen64plus/

Also: 1 GB RAM units. Core + 16.8 MB states + GLideN64 texture cache + slot. Fine for play,
another reason to drop rewind.

## 5. Effort estimate (vs NES/SNES = 21 patches)

| # | Work item | Size | Upstream touch | Notes |
|---|---|---|---|---|
| 0 | Spike (section 6) | S | none | Decides everything below |
| 1 | HW render in slot-retro: SET_HW_RENDER, get_current_framebuffer, get_proc_address, context_reset/destroy, HW_FRAME_BUFFER_VALID sentinel, per-thread EGL pbuffer context, readback | **L** | `libretro.rs` (env + video_refresh + load/unload/serialize), `ffi.rs`; new file for context | Biggest risk; also the host (macOS CGL) side for tests/harness |
| 2 | Core build: mupen64plus-next for device (gles2 target, ADR exception to 0002) and host (macOS); SLOT_PIN sha, SUPPLY-CHAIN, licence tarball | M | none (build scripts) | GLideN64 + dynarec cross build |
| 2b | Core picker: `Core::pair()` returns a strict `(Core, Core)` (`crates/slot-store/src/core_policy.rs:24-30`; picker holds `pair: (Core, Core)`, Left/Right pick `.0`/`.1`, `crates/slot/src/core_picker.rs:48,62,121-122`). A one-core platform does not fit. Either ship parallel-n64 (GLES2 gln64/rice) as the second core, or gate the picker off for N64 | S (gate) / M (second core build) | `core_policy.rs`, `core_picker.rs`, `slot-store/src/core.rs` | Decide in the ADR |
| 3 | `Platform::N64` (Games/N64, Saves, States, Labels, .z64/.n64/.v64 scan; byte-order handled by core) | M | same files as 0002/0005 (`slot-store` core.rs, platform.rs, scan.rs, slot_state.rs, `slot-ui` cart.rs) | Mechanical, follows NES/SNES pattern |
| 4 | Analog input: evdev ABS axes, deadzone/calibration, widen emu input channel, RETRO_DEVICE_ANALOG in input_state, C-buttons on right stick, Z on L2 | M-L | `input/evdev.rs`, `input/device.rs`, `emu.rs` Shared input, `libretro.rs:384` | New for slot; GBA unaffected if axes are 0 |
| 5 | Core options policy: force 320x240, frameskip, ThreadedRenderer off, aspect | S | `core_options_policy.rs` | |
| 6 | Saves: SAVE_RAM blob works; verify autosave/resume path with 16.8 MB states (time to write on SD, lid-close save time budget) | S-M | maybe `state_writer.rs` timeouts | Lid-close save of 16.8 MB may exceed current budget |
| 7 | Disable rewind (and likely FF promise) for N64 | S | `rewind.rs`/quick menu gating | Parity table gets explicit N/A rows |
| 8 | Cart art: N64 cart shape + label variants (grey/coloured, JP/US/PAL) | M | `slot-ui/cart.rs`, cart_shell | Follows ADR 0006/0014 |
| 9 | Shaders: retro shaders on 320x240 input; check cost with GPU already busy | S | none if canvas path reused | GPU now shared between core and compositor |
| 10 | Tests + harness: HW core needs a GL context in CI (macOS runner OK), frame hashes are GPU-specific (host goldens differ from device), deterministic test ROM (homebrew, e.g. a libdragon test ROM) | M-L | tests in own files (ADR 0020) | Byte-identical comparisons only on same GPU |
| 11 | Device gate titles + perf rows: SM64, MK64, OoT, Star Fox 64 (must pass), GoldenEye/Majora (reported, not gated) | S-M | none | |

Rough total: roughly 10-14 patches, with item 1 alone comparable to the canvas + libretro-env work
(0004 + 0006) combined, and item 4 a new subsystem. Calendar effort similar to or larger than SNES.

### Rule checks

- **GBA/GB/GBC byte-identical:** safe if HW render is entered only when a core calls SET_HW_RENDER
  (mGBA/gpSP never do), the HW_FRAME_BUFFER_VALID guard is a new early branch, and analog axes are 0
  for joypad-only cores. The input-channel widening in `emu.rs` must not change GBA input timing:
  keep the existing AtomicU16 and add a separate axes atomic.
- **Frontend cost rule** (PLAN.md:57, QUALITY-BAR.md:12/23, eval at PLAN.md:746 compares NES/SNES to
  max(GBA)+5%): the N64 readback is new per-frame cost that will very likely exceed the GBA budget.
  It does not change the GBA/NES/SNES numbers, but the rule as written would fail N64 if extended to
  it. Needs an explicit N64 budget (or excluding N64 from that eval with a reason).
- **Device gate "full speed, zero underruns":** cannot hold across the N64 library. Must be scoped to
  a named list of light titles; heavy titles reported, not gated (like SA-1/Super FX rows today).
- **Scope:** PLAN.md lists "people who want ... more systems" as not-for. N64 is a scope change
  needing an ADR.
- **Build rule (ADR 0002)** "never platform=arm64": N64 needs a GLES-enabled aarch64 dynarec target.

## 6. Recommendation

**Go-with-limits, but only after a kill/prove spike.** Do not touch slot until the spike passes.

Spike (about 1-2 days, nothing in the patch set):
1. Cross-build mupen64plus-next at a pinned commit with `platform=arm64_cortex_a53_gles2`
   (and gles3) against the device's Mali libs.
2. Write a tiny standalone C or Rust test frontend (outside slot) that: opens EGL on BaseOS with a
   pbuffer surface on a *non-main* thread, answers SET_HW_RENDER (GLES2) /
   get_current_framebuffer / get_proc_address, runs a homebrew test ROM and then the owner's SM64,
   MK64, OoT, GoldenEye dumps for 3 minutes each, glReadPixels every frame, and logs ms/frame for
   retro_run and for the readback separately. Optionally also draw to fb0 via a second context to
   prove two-context coexistence with the compositor.
3. Record `GL_VERSION`/`GL_RENDERER`/`GL_EXTENSIONS` from the blob (ES3? `GL_EXT_read_format_bgra`?)
   and `ls /usr/share/vulkan /etc/vulkan` + any `libvulkan*` (GLES2 vs GLES3 picks the make target).
4. On BaseOS, dump evdev devices and events while moving both sticks: are there ABS_X/Y/RX/RY axes,
   what range, is there cardinal snapping.

Go if: SM64 and MK64 at full speed (<= 16.6 ms run + readback, p99 under the present budget) with
native 320x240, readback < 3 ms, and both sticks visible as evdev axes. Kill (or park as "deferred")
if GLideN64 cannot get a second EGL context on the fbdev blob, if SM64 is not full speed, or if the
sticks are not readable on BaseOS.

If go, ship scope v1 as: mupen64plus-next as the default, plus either parallel-n64 as the picker's
second core or a picker gate for one-core platforms (the picker is a strict pair today), 320x240 locked, no rewind, FF not promised, saves + manual states + autosave, gated
titles SM64/MK64/OoT/Star Fox 64, heavy titles documented as reported-only.
