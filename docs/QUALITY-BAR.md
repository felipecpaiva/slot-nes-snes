# Definition of done

Two halves. Both must pass.

## 1. GBA, GB and GBC do not change

Patched slot is compared against unpatched slot at the same release, both playing the same GBA
and GB carts.

- Every upstream test passes, unmodified.
- Rendered frames are identical, pixel for pixel.
- Frontend cost per frame on GBA is the same as upstream (`core_bench`).

## 2. NES and SNES reach parity

Every feature row in [RESEARCH.md](RESEARCH.md) works on both new shelves: carousel, letter jump,
cart art and labels, core picker, insert and eject, resume on boot, saves and autosave, save
states and polaroids, rewind, fast-forward, turbo, shaders, video mode, quick menu, settings,
volume, sleep.

Hard numbers:

- Frontend cost per frame (pixel conversion, publish, upload) stays within the GBA budget. Measured
  on the host.
- **Device gate (manual, on a real H700):** full speed and zero audio underruns on Star Fox,
  Yoshi's Island, Kirby Super Star, Super Mario RPG and Seiken Densetsu 3, via `task bench:device`
  and `SLOT_TRACE`.

## Known gaps, not hidden

These will not match GBA in the first version:

- SNES uses L and R as game buttons, so it loses slot's L/R picture-mode toggle.
- SNES hi-res frames (512 wide, a few titles) are blended down 2:1 and lose detail.
- Colour correction does nothing on NES and SNES.
- Carts are NES and SNES shaped (issue 26). Famicom and Super Famicom variants, and the choice of region, wait for issue 27, so every NES cart wears the NES shell and every SNES cart the SNES shell. The embossed lettering masks are blank, so no moulded text appears on any cart face.
- PAL (50 Hz) games run at 50 fps with one frame in about six repeated on the 59.6 Hz panel (ADR 0071); PAL Speed "Panel" brings back 60 Hz.
- Settings keyed only by file name collide if the same name exists on two systems.
