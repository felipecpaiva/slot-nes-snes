# Issue index

One file per issue. Tracking issues list their children and hold the phase gate and device check.

| NN | title | phase | area | type | size | depends_on |
|---|---|---|---|---|---|---|
| [01](01-phase-1-nes-boots.md) | Phase 1: NES boots on the RG34XXSP from a release-shaped zip | 1 | device | tracking | L | none |
| [02](02-patch-pipeline.md) | Pin slot v1.6.0 and build both trees from the patch set | 1 | infra | chore | M | none |
| [03](03-task-check-and-upstream-guard.md) | Add task check with shared host cores and the upstream-test-unmodified guard | 1 | tests | test | M | 02-patch-pipeline |
| [04](04-fceumm-core-build.md) | Build fceumm for host and device from a pinned commit and record its licence | 1 | cores | feature | M | 02-patch-pipeline |
| [05](05-gba-harness-and-bench.md) | Build the deterministic GBA/GB/GBC frame-hash harness and the core_bench compare | 1 | tests | test | L | 03-task-check-and-upstream-guard |
| [06](06-step0-exhaustive-matches.md) | Patch 0001: Replace silent GBA/GB fallthroughs with exhaustive Platform policy | 1 | platform | feature | S | 03-task-check-and-upstream-guard, 05-gba-harness-and-bench |
| [07](07-platform-nes.md) | Patch 0002: Add Platform::Nes with its own shelf, folders and placeholder cart | 1 | platform | feature | M | 06-step0-exhaustive-matches |
| [08](08-core-fceumm.md) | Patch 0003: Add Core::Fceumm, Core::EVERY and per-core option prefixes | 1 | cores | feature | M | 07-platform-nes, 04-fceumm-core-build |
| [09](09-canvas.md) | Patch 0004: Add a fixed 360x240 canvas per core via HostExtra and Compositor::set_game_canvas | 1 | video | feature | L | 08-core-fceumm |
| [10](10-dist-zip-deploy.md) | Package the h700 release zip, GPL source tarball and device deploy tasks | 1 | release | feature | M | 09-canvas, 04-fceumm-core-build |
| [11](11-phase-2-snes.md) | Phase 2: SNES | 2 | device | tracking | L | 01-phase-1-nes-boots |
| [12](12-platform-snes.md) | Patch 0005: Add Platform::Snes, Core::Snes9x and SNES header titles | 2 | platform | feature | M | 09-canvas |
| [13](13-snes9x-core-build.md) | Build snes9x from a pinned commit and record its non-commercial licence stance | 2 | cores | feature | M | 04-fceumm-core-build |
| [14](14-libretro-env-and-hires.md) | Patch 0006: Answer SET_GEOMETRY, SET_SYSTEM_AV_INFO and GET_AUDIO_VIDEO_ENABLE, and enable the hi-res blend | 2 | cores | feature | M | 12-platform-snes, 13-snes9x-core-build |
| [15](15-snes-input.md) | Patch 0007: Pass SNES X/Y/L/R to the game, add SELECT+X picture mode and guard SELECT+Y | 2 | input | feature | M | 14-libretro-env-and-hires |
| [16](16-frontend-cost-eval.md) | Add eval-frontend-cost.sh and hold NES/SNES frontend cost inside the GBA budget | 2 | tests | test | S | 14-libretro-env-and-hires |
| [17](17-device-gate-log.md) | Create docs/DEVICE-GATE.md and the RG34XXSP measurement routine | 2 | device | chore | S | 10-dist-zip-deploy, 15-snes-input |
| [18](18-phase-3-parity.md) | Phase 3: full NES/SNES parity | 3 | device | tracking | L | 11-phase-2-snes |
| [19](19-alt-cores-build.md) | Build nestopia and snes9x2005_plus for host and device and record their licences | 3 | cores | feature | M | 04-fceumm-core-build |
| [20](20-core-picker-pairs.md) | Patch 0008: Make the core picker pair-relative and add Core::Nestopia and Core::Snes9x2005Plus | 3 | cores | feature | M | 15-snes-input, 19-alt-cores-build |
| [21](21-shaders.md) | Patch 0009: Give NES and SNES their own shaders stored as shader_nes and shader_snes | 3 | video | feature | S | 20-core-picker-pairs |
| [22](22-ff-and-rewind.md) | Verify fast-forward and rewind on every new core, with per-core option keys | 3 | cores | test | M | 20-core-picker-pairs |
| [23](23-states-quickmenu-resume.md) | Prove save states, polaroids, quick menu, resume on boot and eject saves on NES and SNES | 3 | platform | test | M | 21-shaders |
| [24](24-phase-4-cart-art.md) | Phase 4: real NES and SNES cart art with variants | 4 | ui-art | tracking | L | 18-phase-3-parity |
| [25](25-cart-variant-research.md) | Research and cite NES, Famicom, SNES and Super Famicom cart variants and colours | 4 | docs | chore | M | none |
| [26](26-cart-art.md) | Patch 0010: Add NES, Famicom, SNES and SFC cart shapes, assets, colour tables and evals | 4 | ui-art | feature | L | 25-cart-variant-research, 21-shaders |
| [27](27-cart-shell-grammar-region.md) | Patch 0011: Add cart_shell.txt outline words and region auto-pick for NES and SNES | 4 | ui-art | feature | M | 26-cart-art |
| [28](28-phase-5-release.md) | Phase 5: release, CI, rebase automation and the final device gate | 5 | release | tracking | L | 24-phase-4-cart-art |
| [29](29-ci-test-workflow.md) | Add test.yml: required macOS host job and Linux arm device job | 5 | infra | chore | M | 03-task-check-and-upstream-guard, 10-dist-zip-deploy |
| [30](30-release-workflow.md) | Add release.yml with ship checks, the GPL source tarball and release notes | 5 | release | chore | M | 29-ci-test-workflow |
| [31](31-rebase-and-diffsurface.md) | Add rebase.sh, docs/REBASE.md and task diffsurface | 5 | infra | chore | M | 02-patch-pipeline, 03-task-check-and-upstream-guard |
| [32](32-phase-6-deferred.md) | Phase 6: deferred work (non-blocking) | 6 | docs | tracking | S | 28-phase-5-release |
| [33](33-deferred-fds.md) | DEFERRED: Support the Famicom Disk System as a variant and core | 6 | cores | chore | L | 32-phase-6-deferred |
| [34](34-deferred-pal-pacing.md) | DEFERRED: Pace PAL titles at 50 Hz | 6 | video | chore | M | 32-phase-6-deferred |
| [35](35-deferred-stem-key-collision.md) | DEFERRED: Fix the stem-key collision in selected_core.txt, video_mode.txt and cart_shell.txt | 6 | platform | chore | M | 32-phase-6-deferred |
| [36](36-deferred-option-b-video.md) | DEFERRED: Move to Option B variable frame size for true SNES hi-res | 6 | video | chore | L | 32-phase-6-deferred |
| [38](38-dev-tools-mise.md) | Pin the developer toolchain with mise | 1 | infra | chore | S | none |
| [39](39-cross-platform-performance.md) | Evaluate performance across every platform and core so each one feels like GBA | 5 | device | test | L | 17-device-gate-log, 22-ff-and-rewind, 26-cart-art, 30-release-workflow |
| [40](40-cart-studio-nes-snes.md) | Bring NES and SNES label art to Cart Studio, as a PR or a credited fork | 4 | ui-art | feature | L | 26-cart-art, 27-cart-shell-grammar-region |
| [41](41-label-fetcher-cli.md) | Fetch real NES and SNES cart labels onto the SD card with a small script | 4 | ui-art | feature | M | 26-cart-art, 27-cart-shell-grammar-region |
| [42](42-harness-retry-noise.md) | Stop scheduler noise from failing the harness retry rule | 1 | tests | chore | S | 05-gba-harness-and-bench |
| [43](43-nes-snes-default-stretch.md) | Make Stretch the default picture mode for NES and SNES carts | 2 | video | feature | S | 09-canvas, 12-platform-snes |
| [44](44-quick-menu-retro-shaders.md) | Offer the NES and SNES shaders in the quick menu | 3 | video | feature | S | 21-shaders |
| [45](45-shelf-memory.md) | Remember the last shelf and each shelf's cart across restarts | 3 | platform | feature | S | 12-platform-snes |
| [46](46-retro-shaders.md) | Add Sharp, Scanlines, crt-pi and crt-1tap shaders for NES and SNES | 3 | video | feature | M | 21-shaders, 44-quick-menu-retro-shaders |
| [47](47-audio-reopen.md) | Stop losing audio when slot reopens the ALSA device | 5 | device | fix | S | 39-cross-platform-performance |
