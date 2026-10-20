# Supply chain: every network fetch in the build and dist path

| Fetch | Where | Verification |
|---|---|---|
| slot release tarball | `scripts/fetch-slot.sh` | sha256 `tarball_sha256` in `SLOT_PIN`, cached copy removed on mismatch |
| fceumm source tarball | `cores/fceumm/build.sh fetch` (shared code in `cores/lib.sh`) | sha256 `fceumm_tarball_sha256` in `SLOT_PIN` |
| snes9x source tarball | `cores/snes9x/build.sh fetch` | sha256 `snes9x_tarball_sha256` in `SLOT_PIN` |
| nestopia source tarball | `cores/nestopia/build.sh fetch` | sha256 `nestopia_tarball_sha256` in `SLOT_PIN` (commit `nestopia_commit`) |
| snes9x2005_plus source tarball (libretro/snes9x2005) | `cores/snes9x2005_plus/build.sh fetch` | sha256 `snes9x2005_plus_tarball_sha256` in `SLOT_PIN` (commit `snes9x2005_plus_commit`) |
| Genesis Plus GX source tarball (libretro/Genesis-Plus-GX) | `cores/genesis_plus_gx/build.sh fetch` | sha256 `genesis_plus_gx_tarball_sha256` in `SLOT_PIN` (commit `genesis_plus_gx_commit`); built, not in a release yet |
| pcsx_rearmed source tarball (libretro/pcsx_rearmed) | `cores/pcsx_rearmed/build.sh fetch` | sha256 `pcsx_rearmed_tarball_sha256` in `SLOT_PIN` (commit `pcsx_rearmed_commit`); shipped with the PS1 platform |
| Beetle PCE Fast source tarball (libretro/beetle-pce-fast-libretro) | `cores/mednafen_pce_fast/build.sh fetch` | sha256 `mednafen_pce_fast_tarball_sha256` in `SLOT_PIN` (commit `mednafen_pce_fast_commit`); built and tested, ships with the TG16 platform (issue 83) |
| Beetle Cygne source tarball (libretro/beetle-wswan-libretro) | `cores/mednafen_wswan/build.sh fetch` | sha256 `mednafen_wswan_tarball_sha256` in `SLOT_PIN` (commit `mednafen_wswan_commit`); built and tested, ships with the WonderSwan platform (issue 93) |
| Beetle Lynx source tarball (libretro/beetle-lynx-libretro) | `cores/mednafen_lynx/build.sh fetch` | sha256 `mednafen_lynx_tarball_sha256` in `SLOT_PIN` (commit `mednafen_lynx_commit`); ships with the Lynx platform (patches 0058 on; `dist-device.sh`, `zip-check.sh`). No Lynx BIOS is fetched or shipped |
| Beetle NeoPop source tarball (libretro/beetle-ngp-libretro) | `cores/mednafen_ngp/build.sh fetch` | sha256 `mednafen_ngp_tarball_sha256` in `SLOT_PIN` (commit `mednafen_ngp_commit`); built and tested, ships with the NGP platform (issue 72) |
| PicoDrive source tarball (libretro/picodrive) and its emu2413, dr_libs and libpicofe submodule tarballs (GitHub archives of digital-sound-antiques/emu2413, mackron/dr_libs, irixxxx/libpicofe) | `cores/picodrive/build.sh fetch` (`cores/lib.sh` `modules`) | sha256 `picodrive_tarball_sha256` and `picodrive_<name>_tarball_sha256` in `SLOT_PIN` (commits `picodrive_commit`, `picodrive_<name>_commit`), each checked before it is unpacked; ships with the 32X platform (issue 145, ADR 0096) |
| Stella 2014 source tarball (libretro/stella2014-libretro) | `cores/stella2014/build.sh fetch` | sha256 `stella2014_tarball_sha256` in `SLOT_PIN` (commit `stella2014_commit`); ships with the 2600 platform (patch 0100, issue 156; `dist-device.sh`, `zip-check.sh`) |
| ProSystem source tarball (libretro/prosystem-libretro) | `cores/prosystem/build.sh fetch` | sha256 `prosystem_tarball_sha256` in `SLOT_PIN` (commit `prosystem_commit`); ships with the 7800 platform (patch 0100, issue 163; `dist-device.sh`, `zip-check.sh`). No 7800 BIOS is fetched or shipped |
| Beetle VB source tarball (libretro/beetle-vb-libretro) | `cores/mednafen_vb/build.sh fetch` | sha256 `mednafen_vb_tarball_sha256` in `SLOT_PIN` (commit `mednafen_vb_commit`) |
| FinalBurn Neo source tarball (libretro/FBNeo) | `cores/fbneo/build.sh fetch` | sha256 `fbneo_tarball_sha256` in `SLOT_PIN` (commit `fbneo_commit`), checked before it is unpacked; ships with the arcade platforms (issue 184, ADR 0099). No romset or BIOS is fetched or shipped |
| Beetle SuperGrafx source tarball (libretro/beetle-supergrafx-libretro) | `cores/mednafen_supergrafx/build.sh fetch` | sha256 `mednafen_supergrafx_tarball_sha256` in `SLOT_PIN` (commit `mednafen_supergrafx_commit`); ships with the SuperGrafx platform (ADR 0101) |
| mGBA source | upstream `cores/mgba/build.sh`, `git fetch` of one commit | git commit id `MGBA_COMMIT` (SHA-1 content addressed) |
| Task linux arm64 tarball | `scripts/fetch-task.sh` | sha256 `task_linux_arm64_sha256` in `SLOT_PIN`, checked before extraction |
| gpSP device source tarball | upstream `core:gpsp` (curl, no checksum) | sha256 `gpsp_tarball_sha256` in `SLOT_PIN`, checked by `scripts/dist-device.sh` on the vendor copy and the dist copy right after upstream's run; failure removes the dist tree and the gpSP cache. Upstream deletes its cached copy before downloading and its skip check cannot be met from outside, so the check runs after the download, before anything is packaged |
| exfatprogs release tarball (for `System/fsck.exfat`, shipped with its source) | upstream `fsck:exfat` (curl), built static in the device box | sha256 `EXFATPROGS_SHA256` in upstream's taskfile, checked by upstream with `shasum -c` before the build, and again by `scripts/zip-check.sh` on the shipped copy |
| gpSP host dylib (buildbot nightly) | upstream `core:gpsp:host` | sha256 `gpsp_host_sha256_<arch>` via `scripts/core-host.sh`. Host only, never shipped |
| Rust crates | Cargo, from `Cargo.lock` | the checksums in `Cargo.lock`, same as upstream |
| `rust:1-bullseye` image | `scripts/device-sh.sh`, upstream's device builds | none: a floating tag. Known, accepted gap, also upstream's |
| `cmake` by `apt-get` in the container | upstream `cores/mgba/build.sh` | none: Debian's signed apt index only. Known, accepted gap, also upstream's |
| `task` linux arm64 binary in the CI `device` job | `scripts/fetch-task.sh` (no mise in the container) | same sha256 as above |
| GitHub Actions in `.github/workflows/test.yml` and `release.yml` | `uses:` lines | full commit SHA, tag in a comment: `actions/checkout` v7.0.1 `3d3c42e5aac5ba805825da76410c181273ba90b1`, `jdx/mise-action` v5.1.2 `08ae2a091c038e1e05ec6f5115dc5c69d5a2a6b8`, `actions/cache` v6.1.0 `55cc8345863c7cc4c66a329aec7e433d2d1c52a9`, `actions/upload-artifact` v7.0.2 `cf430e030ddbb5b0abf93d22962f4752f3646cd9`, `actions/download-artifact` (release.yml only) v8.0.2 `9000827ccba6bdab643e8b6fd33ac0654aef8333`. Bump by `git ls-remote --tags` and edit both SHA and comment |
| `rust:1-bullseye` as the CI `device` container | `container:` in `test.yml` | none: the same floating tag as local, accepted gap |
| Rust, Task, cmake on the CI `host` job | `jdx/mise-action` from `mise.toml` | versions pinned in `mise.toml` (rust, task, cmake), the same as a developer. adb is not installed in CI |
| `zip`, `unzip`, `file`, `binutils` by `apt-get` in the CI `device` container | `test.yml` | none: Debian's signed apt index only, same gap as cmake |

`zip-check.sh` then checks the zip itself: each core is the core its name says (library name in
`strings`, sha256 in `System/licenses/cores.sha256`), the licences folder holds exactly the
expected names, and the source tarball holds the full `work/slot` HEAD file list.
