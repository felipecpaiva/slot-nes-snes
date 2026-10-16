# PS1 spike: pcsx_rearmed on the RG34XXSP (step 2 of docs/research/ps1-plan.md)

A throwaway device measurement. Nothing here enters `patches/`: the core build, the core_bench
changes and the scripts live outside the patch set until the numbers say go.

## What was built

| Artifact | Detail | sha256 |
|---|---|---|
| Source | `https://github.com/libretro/pcsx_rearmed/archive/c8816799b50388e61cfe237fe2cdbb7d8175f20a.tar.gz` (the pin bently and omega-zero use) | `edeb21fdeef8815521cb9d4488d2cd35746607c968ca9b26cce4e42c09f2dc99` |
| `pcsx_rearmed_libretro.so` | `cores/lib.sh` in rust:1-bullseye, `make -f Makefile.libretro platform=unix DYNAREC=ari64 BUILTIN_GPU=neon HAVE_PHYSICAL_CDROM=0 HAVE_CHD=1`, CFLAGS `-mcpu=cortex-a53` (omega-zero's flags) | `2b438b1ef1fafa118cb5f7ce4021e7b6882560529ebc974335d2ebfcef0f35b8` |
| `core_bench` | slot's `bench:device` task, with the spike diff below | `96d0947e8702d06edd020830f203108be029b0df66bfaa4085c863aa91ae8e67` |
| `stickread` | 83 lines of C, static, same container | `1a1156332f669bb8e6952a6b110f80fac309a62f9bf9787844660f81aa910f2e` |

- The build log shows `new_dynarec` (ari64), `gpu_neon`, `libchdr` and `gpu_async` objects.
- NEEDED is libpthread, libdl, libm and libc only, at GLIBC_2.17 or older.
- The device binaries ran a CHD game in an aarch64 bullseye container: path load, frames and audio all worked. That is a smoke test only, not a timing.
- Files are in `/tmp/claude-501/ps1spike/`:
  - `run.sh`, `README.md`, the three binaries;
  - `core_bench-spike.diff`, `pcsx_rearmed-build.sh`, `pcsx_rearmed_libretro.so.meta`.

### core_bench spike changes (`core_bench-spike.diff`, not in patches/)

- `video_refresh` counts every frame by (width, height, pixel format). It also counts:
  - NULL dupes;
  - frames delivered off the bound thread;
  - the time spent in slot's copy and convert.

  `spike_take_frame_stats()` returns them.
- New core_bench flags, all passed after `load` by path (patch 0030):
  - `--canvas WxH`. The spike uses 640x480. At the default 240x160, pcsx frames take the legacy crop path and no size is recorded.
  - `--defaults` answers every declared option with its first value, which is what omega-zero 1.2.0 does.
  - `--per-frame` times every `retro_run`, in one pass with no save states.
  - `--tap-start N` presses START for 4 frames every N frames.
- In per-frame mode it prints:
  - the mean of each 600-frame bucket;
  - the median, p95 and max;
  - x realtime at 59.94 Hz and at the core's fps;
  - the size histogram;
  - slot's convert ms per shown frame, and emulation time with that subtracted;
  - a synthetic `copy_centred` cost for each seen size into 640x480 and 320x240;
  - a 640x480x4 memcpy.

## Method (run.sh)

1. Pushes the core, core_bench and stickread to `/mnt/sdcard/ps1spike-tmp`.
2. Lists `/mnt/sdcard/BIOS`. It pushes `scph*.bin` from the maintainer's BIOS folder only when the card has no scph file there.
3. Stick dump, done first so the maintainer can leave during the benches:
   - prints `/proc/bus/input/devices`;
   - stickread finds every node with ABS axes and prints the EVIOCGABS ranges;
   - while both sticks move for 10 s, it prints, per code, the min, max and number of distinct values, plus diagonal samples per stick pair.
4. Picks three games by name, preferring `.chd` and never Disc 2 or later:
   - light 2D: Symphony of the Night;
   - 3D: Crash Bandicoot, else Spyro;
   - heavy: Gran Turismo 2, else Tekken 3.

   It copies them into the temp dir as `g1` to `g3`, after a free-space check.
5. Ten runs. Each is 3000 frames after 600 warmup, with idle input, canvas 640x480, `memcard2=none` and `neon_enhancement_enable=disabled`:
   - g1 and g3: threads `disabled` vs `auto`;
   - g2: `disabled`, `auto`, `enabled`, HLE BIOS, no options answered (slot today), every default answered (omega-zero).
6. Removes the temp dir; `KEEP=1` keeps it. BIOS files it pushed stay in `BIOS/`, where slot will look for them.

## Facts from the source at the pin

- `pcsx_rearmed_gpu_thread_rendering` takes `auto|disabled|enabled`. **There is no `sync`**: libretro.c maps any unknown value to auto (-1). The spike runs `enabled` in its place.
- When the key is not answered, `thread_rendering` stays 0, so it is **disabled**: the libretro `pl_rearmed_cbs` initializer leaves it unset. Slot today answers no defaults, so it runs single-threaded. omega-zero answers the declared default `auto`, which turns threading on when there are 2 or more cores.
- `pcsx_rearmed_bios=auto` tries, in order, scph5500, 5501, 5502, psxonpsp660, scph101, 7001, 1001, then any BIOS in the system dir, then HLE. **core_bench cannot see which one was used**, because slot's log callback is a no-op. The real BIOS vs HLE pair is only meaningful if the card's BIOS listing shows a file from that list.

## How to read the results

- **`run` is the frontend-visible cost.** It is `retro_run` including slot's copy into the canvas. One 59.94 Hz frame is 16.68 ms. x realtime of 1.00 is just full speed; core_bench runs unthrottled.
- **Threaded runs** move GPU work to a second thread, so `run` drops while the total CPU use does not.
  - Compare threads `auto` against `disabled` for the headroom that slot would gain by answering the option.
  - `off-thread` above 0 means pcsx called `video_refresh` from its GPU thread. slot drops those frames, because the host is bound per thread. That would be a real blocker for threading, not a bench artefact.
- **`dupes`** are NULL frames, where pcsx reports no change. A high count on a title screen is normal.
- **Frame sizes:**
  - 256, 320, 368/364, 512 and 640 wide, with 240 or 480 high, are the PS1 modes.
  - 480-high frames are interlaced hi-res, for example menus in some games.
  - Width above 640 or height above 480 is halved by `copy_centred`.
- **Convert:**
  - The in-run `slot copy/convert` figure is the real path at canvas 640x480.
  - The synthetic `convert` lines show what a 320x240 canvas would cost instead. Any frame wider than 320 then takes the box-filter path, which is slower than the plain copy.
  - **Upload is not measured.** core_bench is headless, with no GL. The memcpy line is only a floor for staging 1.2 MB.
- **Sticks:**
  - More than 8 distinct values on ABS_X/Y or ABS_RX/RY (or Z/RZ) means analog.
  - Diagonal samples above zero mean the sticks do not snap to cardinals.
  - Only the hat codes 0x10/0x11 moving, or no ABS node at all, means the sticks are digital or not exposed. That answers the N64 spike's question too.

### Caveats

- **Idle input over 600 + 3000 frames (about 60 s) is mostly logos, intros, attract mode and title screens, not gameplay.**
  - A "3D at full speed" verdict from these runs is weak.
  - If g2 and g3 show only 320x240 or 512x240 and many dupes, rerun with `TAP=180 WARMUP=1800` to get into menus or demos.
  - A state saved in-game would be better still: core_bench takes `--state`.
- Real BIOS and HLE show different content (HLE skips the boot logo), so their pair compares cost, not identical frames.
- If slot is running on the shelf during the bench, it takes CPU. The header prints its pid.
- No audio is output, so underruns are not measured here. Plan item 4, audio underruns and lid-close save time, needs slot itself on a throwaway branch.

## Go / no-go bar

**Go** (continue to step 3, the ADRs) only if all of these hold:

1. **Light (g1) and 3D (g2) run at full speed with headroom.** With threads `disabled` (slot today), or with `auto` if `off-thread` is 0:
   - median ms/frame is at most 12.5 (x realtime at least 1.33);
   - p95 is under 16.68.
2. **Conversion is under 2 ms a frame:** the in-run `slot copy/convert` at canvas 640x480, for every frame size seen.
3. **The sticks are analog:** at least one stick pair moves through more than 8 values, with diagonal samples.

**Partial:**

- If 1 and 2 pass but 3 fails, PS1 v1 still goes, since it is digital pad only. Analog (v2) and the N64 stick plan are parked.
- If g3 (heavy) misses full speed, record it as a known title gap. It is not a no-go.

**No-go:** g1 or g2 below full speed with every thread setting, or conversion at 2 ms or more. Then either:

- try the 320x240 canvas (the synthetic lines show its cost), or
- park PS1 per the plan.
