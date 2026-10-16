# 0064. Answer pcsx_rearmed's declared option defaults, and leave every other core's answers alone

- Status: Accepted
- Date: 2026-10-17
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0047](0047-upstream-first-fixes.md), [ADR 0063](0063-ps1-in-scope-on-pcsx-rearmed.md), [PS1 spike](../research/ps1-spike.md) Results, [issue 59](../../.github/issues/59-ps1-options.md)

## Context

slot answers GET_VARIABLE only for keys it sets, and returns false for every other key. pcsx
leaves `thread_rendering` at 0 unless `pcsx_rearmed_gpu_thread_rendering` is answered, so under
slot today it renders on the emu thread even though its declared default is `auto`. Found by
tray, confirmed in the source at the pin (`frontend/libretro.c:2824-2836`). On the device
(Spyro, mean ms a frame): 3.45 with nothing answered, 2.38 with threads `auto`, 2.17 with every
declared default answered (omega-zero's approach, which also turns on `drc_thread=auto`).
`off-thread` was 0 in every run, so slot drops no frame.

## Decision

- For pcsx_rearmed, slot answers every key the core declares. The order is:
  1. a value slot sets explicitly wins, for example `memcard2=none` or
     `neon_enhancement_enable=disabled` (issue 59);
  2. a key slot does not set gets the core's declared default;
  3. a key the core never declared is still answered false.
- `pcsx_rearmed_gpu_thread_rendering=auto` and `pcsx_rearmed_drc_thread=auto` are also set
  explicitly, so a change of declared default at a future pin cannot turn threading off silently.
- Scope: pcsx_rearmed only, the narrowest of the allowed scopes. mGBA and gpSP keep upstream's
  behaviour exactly, because GBA, GB and GBC must stay byte-identical. Our NES, SNES and Sega
  cores may join later, one issue each, once the harness proves their frames do not change.
- Whether every core should get its defaults answered is a generic question for upstream (ADR
  0047). It is asked there, with the Spyro numbers and omega-zero's Supafaust crash as evidence,
  not carried here for GBA.

## Consequences

- PS1 gains about 1 ms a frame of headroom on the emu thread with no new mechanism for GBA.
- A second GPU thread uses the other A53 cores. Battery and SoC temperature go into the device
  gate (issue 56).
- If upstream adopts answering defaults for every core, our pcsx-only branch is dropped on the
  next rebase.
- On a rebase, check that the declared keys and their defaults at the pin still match the test's
  list.
