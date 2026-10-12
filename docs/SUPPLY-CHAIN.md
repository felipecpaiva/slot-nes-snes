# Supply chain: every network fetch in the build and dist path

| Fetch | Where | Verification |
|---|---|---|
| slot release tarball | `scripts/fetch-slot.sh` | sha256 `tarball_sha256` in `SLOT_PIN`, cached copy removed on mismatch |
| fceumm source tarball | `cores/fceumm/build.sh fetch` (shared code in `cores/lib.sh`) | sha256 `fceumm_tarball_sha256` in `SLOT_PIN` |
| snes9x source tarball | `cores/snes9x/build.sh fetch` | sha256 `snes9x_tarball_sha256` in `SLOT_PIN` |
| mGBA source | upstream `cores/mgba/build.sh`, `git fetch` of one commit | git commit id `MGBA_COMMIT` (SHA-1 content addressed) |
| Task linux arm64 tarball | `scripts/fetch-task.sh` | sha256 `task_linux_arm64_sha256` in `SLOT_PIN`, checked before extraction |
| gpSP device source tarball | upstream `core:gpsp` (curl, no checksum) | sha256 `gpsp_tarball_sha256` in `SLOT_PIN`, checked by `scripts/dist-device.sh` on the vendor copy and the dist copy right after upstream's run; failure removes the dist tree and the gpSP cache. Upstream deletes its cached copy before downloading and its skip check cannot be met from outside, so the check runs after the download, before anything is packaged |
| gpSP host dylib (buildbot nightly) | upstream `core:gpsp:host` | sha256 `gpsp_host_sha256_<arch>` via `scripts/core-host.sh`. Host only, never shipped |
| Rust crates | Cargo, from `Cargo.lock` | the checksums in `Cargo.lock`, same as upstream |
| `rust:1-bullseye` image | `scripts/device-sh.sh`, upstream's device builds | none: a floating tag. Known, accepted gap, also upstream's |
| `cmake` by `apt-get` in the container | upstream `cores/mgba/build.sh` | none: Debian's signed apt index only. Known, accepted gap, also upstream's |

`zip-check.sh` then checks the zip itself: each core is the core its name says (library name in
`strings`, sha256 in `System/licenses/cores.sha256`), the licences folder holds exactly the
expected names, and the source tarball holds the full `work/slot` HEAD file list.
