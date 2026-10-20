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
| [34](34-deferred-pal-pacing.md) | DEFERRED: Pace PAL titles at 50 Hz (superseded by 66) | 6 | video | chore | M | 32-phase-6-deferred |
| [35](35-deferred-stem-key-collision.md) | DEFERRED: Fix the stem-key collision in selected_core.txt, video_mode.txt and cart_shell.txt | 6 | platform | chore | M | 32-phase-6-deferred |
| [80](80-deferred-cheats.md) | DEFERRED: Per-game cheats from the libretro cheat database | 6 | platform | chore | L | 32-phase-6-deferred |
| [36](36-deferred-option-b-video.md) | DEFERRED: Move to Option B variable frame size for true SNES hi-res | 6 | video | chore | L | 32-phase-6-deferred |
| [38](38-dev-tools-mise.md) | Pin the developer toolchain with mise | 1 | infra | chore | S | none |
| [39](39-cross-platform-performance.md) | Evaluate performance across every platform and core so each one feels like GBA | 5 | device | test | L | 17-device-gate-log, 22-ff-and-rewind, 26-cart-art, 30-release-workflow |
| [40](40-cart-studio-nes-snes.md) | Bring NES and SNES label art to Cart Studio, as a PR or a credited fork | 4 | ui-art | feature | L | 26-cart-art, 27-cart-shell-grammar-region |
| [41](41-label-fetcher-cli.md) | Fetch real NES and SNES cart labels onto the SD card with a small script | 4 | ui-art | feature | M | 26-cart-art, 27-cart-shell-grammar-region |
| [42](42-harness-retry-noise.md) | Stop scheduler noise from failing the harness retry rule | 1 | tests | chore | S | 05-gba-harness-and-bench |
| [43](43-nes-snes-default-stretch.md) | Make Stretch the default picture mode for NES and SNES carts | 2 | video | feature | S | 09-canvas, 12-platform-snes |
| [44](44-quick-menu-retro-shaders.md) | Offer the NES and SNES shaders in the quick menu | 3 | video | feature | S | 21-shaders |
| [45](45-shelf-memory.md) | Remember the last shelf and each shelf's cart across restarts (superseded by slot v1.7.0 #53, ADR 0039) | 3 | platform | feature | S | 12-platform-snes |
| [46](46-retro-shaders.md) | Add Sharp, Scanlines, crt-pi and crt-1tap shaders for NES and SNES | 3 | video | feature | M | 21-shaders, 44-quick-menu-retro-shaders |
| [47](47-audio-reopen.md) | Stop losing audio when slot reopens the ALSA device | 5 | device | fix | S | 39-cross-platform-performance |
| [48](48-deferred-n64.md) | DEFERRED: Add N64 as a platform, after a device spike proves it | 6 | cores | chore | L | 32-phase-6-deferred |
| [49](49-retro-line-pixel.md) | Add Line and Pixel shaders for NES and SNES and make Scanlines sharp | 3 | video | feature | S | 46-retro-shaders |
| [50](50-sega-tracking.md) | Sega: Game Gear, Master System and Mega Drive on Genesis Plus GX | 7 | device | tracking | L | 39-cross-platform-performance |
| [51](51-platform-gg.md) | Add Platform::Gg, Game Gear on Genesis Plus GX at 3x | 7 | platform | feature | M | 50-sega-tracking |
| [52](52-platform-sms.md) | Add Platform::Sms, Master System on Genesis Plus GX at 2x | 7 | platform | feature | M | 51-platform-gg |
| [53](53-platform-md.md) | Add Platform::Md, Mega Drive on Genesis Plus GX with 6-button input and live-width Stretch | 7 | platform | feature | L | 52-platform-sms |
| [54](54-system-picture.md) | Choose each retro system's default picture mode from its Screen section | 7 | video | feature | S | 43-nes-snes-default-stretch, 53-platform-md |
| [55](55-crop-overscan.md) | Crop the NES and SNES overscan edges in a new default picture mode | 7 | video | feature | S | 54-system-picture |
| [56](56-ps1-tracking.md) | PlayStation: PS1 on pcsx_rearmed, built the NES and SNES way | 8 | device | tracking | L | 50-sega-tracking |
| [57](57-ps1-core-build.md) | Build pcsx_rearmed from a pinned commit for host and device and record its licence | 8 | cores | feature | M | 56-ps1-tracking |
| [58](58-platform-ps1.md) | Add Platform::Ps1 with its own shelf, disc scan and explicit policy | 8 | platform | feature | M | 57-ps1-core-build |
| [59](59-ps1-options.md) | Set the PS1 core options and answer pcsx's declared defaults | 8 | cores | feature | S | 58-platform-ps1 |
| [60](60-ps1-canvas-screen.md) | Give PS1 a 640x480 canvas and its own Screen section with Shader and Picture rows | 8 | video | feature | M | 59-ps1-options |
| [61](61-ps1-disk-control.md) | Swap PS1 discs, remember the disc per game and record it in states | 8 | platform | feature | M | 60-ps1-canvas-screen |
| [62](62-ps1-input.md) | Hand L1, R1, L2 and R2 to PS1 games and map the PlayStation face buttons | 8 | input | feature | S | 58-platform-ps1 |
| [63](63-ps1-tests.md) | Test PS1 with generated PS-X EXE and ISO discs on HLE BIOS | 8 | tests | test | M | 57-ps1-core-build |
| [64](64-ps1-cases.md) | Draw PS1 games as jewel cases with cover art, region styles and the disc on insert | 8 | ui-art | feature | L | 58-platform-ps1 |
| [65](65-ps1-analog.md) | Read the RG34XXSP analog sticks and offer the DualShock on PS1 (v2) | 8 | input | feature | L | 62-ps1-input |
| [66](66-pal-pacing.md) | Pace PAL titles at 50 Hz on NES, Master System, Mega Drive and PS1 | 8 | video | feature | M | 56-ps1-tracking |
| [67](67-crash-guard.md) | Do not auto-resume a game whose start crashed | 8 | platform | fix | M | 56-ps1-tracking |
| [68](68-deferred-ps1-disc-shelf.md) | DEFERRED: Offer a 3D disc or disc stack as an alternative PS1 shelf style | 6 | ui-art | chore | L | 32-phase-6-deferred, 64-ps1-cases |
| [69](69-sms-region.md) | Master System region override: a Region row in the Master System Screen section | 8 | video | feature | M | 66-pal-pacing |
| [81](81-tg16-tracking.md) | TurboGrafx-16: PC Engine and TurboGrafx HuCards on Beetle PCE Fast, built the NES and SNES way | 10 | device | tracking | L | 56-ps1-tracking |
| [82](82-tg16-core-build.md) | Build Beetle PCE Fast from a pinned commit for host and device and record its licence | 10 | cores | feature | S | 81-tg16-tracking |
| [83](83-platform-tg16.md) | Add Platform::Tg16 with its own shelf, scan and explicit policy | 10 | platform | feature | M | 82-tg16-core-build |
| [84](84-tg16-options.md) | Set the TG16 core options, the scanline window first | 10 | cores | feature | S | 83-platform-tg16 |
| [85](85-tg16-canvas-screen.md) | Give TG16 the 360x240 canvas and its own Screen section with Shader and Picture rows | 10 | video | feature | S | 84-tg16-options |
| [86](86-tg16-saves.md) | Keep TG16 backup RAM in .sav like every core; TurboCD out of scope | 10 | platform | feature | S | 83-platform-tg16 |
| [87](87-tg16-input.md) | Map the TG16 pad: II, I, Select, Run and turbo | 10 | input | feature | S | 83-platform-tg16 |
| [88](88-tg16-tests.md) | Test TG16 with a generated HuCard | 10 | tests | test | S | 82-tg16-core-build |
| [89](89-tg16-carts.md) | Draw HuCards and fetch their labels | 10 | ui-art | feature | M | 83-platform-tg16 |
| [90](90-tg16-device-gate.md) | TG16 device gate on the RG34XXSP | 10 | device | chore | S | 85-tg16-canvas-screen, 86-tg16-saves, 87-tg16-input |
| [91](91-wswan-tracking.md) | WonderSwan: WonderSwan and WonderSwan Color on Beetle Cygne, built the NES and SNES way | 11 | device | tracking | L | 56-ps1-tracking |
| [92](92-wswan-core-build.md) | Build Beetle Cygne from a pinned commit for host and device and record its licence | 11 | cores | feature | S | 91-wswan-tracking |
| [93](93-platform-wswan.md) | Add Platform::Ws with its own shelf, scan, footer reader, saves and explicit policy | 11 | platform | feature | M | 92-wswan-core-build |
| [94](94-wswan-options.md) | Set the WonderSwan core options: 60 Hz mode, rotation and keymap on every load | 11 | cores | feature | S | 93-platform-wswan |
| [95](95-wswan-canvas-screen.md) | Give WonderSwan its canvases and its own Screen section with Shader, Picture and Refresh rows | 11 | video | feature | M | 94-wswan-options |
| [96](96-wswan-input.md) | Map the WonderSwan X and Y pads for horizontal and vertical games | 11 | input | feature | M | 93-platform-wswan |
| [97](97-wswan-tests.md) | Test WonderSwan with a generated cart that paints, turns and saves | 11 | tests | test | S | 92-wswan-core-build |
| [98](98-wswan-carts.md) | Draw WonderSwan carts (black and clear shells) and fetch their labels | 11 | ui-art | feature | M | 93-platform-wswan |
| [99](99-wswan-device-gate.md) | WonderSwan device gate on the RG34XXSP | 11 | device | chore | S | 93-platform-wswan, 95-wswan-canvas-screen, 96-wswan-input |
| [101](101-lynx-tracking.md) | Atari Lynx: Lynx on Beetle Lynx, with a BIOS check, our own rotation and real-rate pacing | 12 | device | tracking | L | 56-ps1-tracking |
| [102](102-lynx-core-build.md) | Build Beetle Lynx from a pinned commit for host and device and record its licence | 12 | cores | feature | S | 101-lynx-tracking |
| [103](103-platform-lynx.md) | Add Platform::Lynx with its own shelf, scan, LNX header reader and explicit policy | 12 | platform | feature | M | 102-lynx-core-build |
| [104](104-lynx-bios-check.md) | Check lynxboot.img before a Lynx launch and toast instead of a silent black screen | 12 | platform | feature | S | 103-platform-lynx |
| [105](105-lynx-options.md) | Set the Lynx core options: lynx_rot_screen always set, lynx_force_60hz off, RGB565 | 12 | cores | feature | S | 103-platform-lynx |
| [106](106-lynx-canvas-screen.md) | Give Lynx a 240x160 canvas at 4x and its own Screen section | 12 | video | feature | S | 105-lynx-options |
| [107](107-lynx-pacing.md) | Pace Lynx games at the rate their frames carry, with a Lynx Speed row (Native default) | 12 | video | feature | M | 106-lynx-canvas-screen, 66-pal-pacing |
| [108](108-lynx-saves.md) | Lynx saves: states only on Beetle Lynx, and say so | 12 | platform | chore | S | 103-platform-lynx |
| [109](109-lynx-input-rotation.md) | Map the Lynx buttons and turn carts made to be held sideways | 12 | input | feature | M | 105-lynx-options |
| [110](110-lynx-tests.md) | Test Lynx with a homebrew image, synthetic carts and the real BIOS when present | 12 | tests | test | S | 102-lynx-core-build |
| [111](111-lynx-carts.md) | Draw Lynx cards and fetch their labels | 12 | ui-art | feature | M | 103-platform-lynx |
| [112](112-lynx-device-gate.md) | Lynx device gate on the RG34XXSP | 12 | device | chore | S | 104-lynx-bios-check, 107-lynx-pacing, 109-lynx-input-rotation |
| [70](70-ngp-tracking.md) | NeoGeo Pocket: NGP and Pocket Color on Beetle NeoPop, built the NES and SNES way | 9 | device | tracking | L | 56-ps1-tracking |
| [71](71-ngp-core-build.md) | Build Beetle NeoPop from a pinned commit for host and device and record its licence | 9 | cores | feature | S | 70-ngp-tracking |
| [72](72-platform-ngp.md) | Add Platform::Ngp with its own shelf, scan and explicit policy | 9 | platform | feature | M | 71-ngp-core-build |
| [73](73-ngp-options.md) | Set the NGP core options and answer NeoPop's declared defaults | 9 | cores | feature | S | 72-platform-ngp |
| [74](74-ngp-canvas-screen.md) | Give NGP a 240x160 canvas and its own Screen section with Shader and Picture rows | 9 | video | feature | S | 73-ngp-options |
| [75](75-ngp-flash-saves.md) | Keep NGP cart flash safe: core save dir, atomic publish, flush by reload | 9 | platform | feature | M | 72-platform-ngp |
| [76](76-ngp-input.md) | Map the NGP A, B and Option buttons | 9 | input | feature | S | 72-platform-ngp |
| [77](77-ngp-tests.md) | Test NGP with a generated cart that paints and writes flash | 9 | tests | test | S | 71-ngp-core-build |
| [78](78-ngp-carts.md) | Draw NGP carts (mono and Color shells) and fetch their labels | 9 | ui-art | feature | M | 72-platform-ngp |
| [79](79-ngp-device-gate.md) | NGP device gate on the RG34XXSP | 9 | device | chore | S | 74-ngp-canvas-screen, 75-ngp-flash-saves, 76-ngp-input |
| [143](143-s32x-tracking.md) | Sega 32X: 32X on PicoDrive, a shelf of its own beside an unchanged Mega Drive | 15 | device | tracking | L | 70-ngp-tracking |
| [144](144-s32x-core-build.md) | Build PicoDrive and its three submodules from pinned commits for host and device and record its licence | 15 | cores | feature | M | 143-s32x-tracking |
| [145](145-platform-s32x.md) | Add Platform::S32x with its own shelf, a 32X header check and explicit policy | 15 | platform | feature | M | 144-s32x-core-build |
| [146](146-s32x-options.md) | Set the PicoDrive options: six-button pad, region Auto, dynarec on | 15 | cores | feature | S | 145-platform-s32x |
| [147](147-s32x-screen.md) | Give the 32X its own Screen section with Shader, Picture, PAL Speed, Renderer and Sound Rate | 15 | video | feature | M | 146-s32x-options |
| [148](148-s32x-saves.md) | 32X saves: the ordinary .sav, written only for games that save | 15 | platform | chore | S | 145-platform-s32x |
| [149](149-s32x-input.md) | Map the 32X pad as the Mega Drive six-button pad | 15 | input | feature | S | 145-platform-s32x |
| [150](150-s32x-tests.md) | Test the 32X with a generated cart whose SH-2s must answer, and Mega Drive after 32X | 15 | tests | test | S | 144-s32x-core-build |
| [151](151-s32x-carts.md) | Draw the 32X cart and fetch its labels | 15 | ui-art | feature | M | 145-platform-s32x |
| [152](152-s32x-device-gate.md) | 32X device gate on the RG34XXSP | 15 | device | chore | S | 147-s32x-screen, 149-s32x-input |
| [153](153-atari-tracking.md) | Atari 2600 and Atari 7800 on Stella 2014 and ProSystem, built the NES and SNES way | 14 | device | tracking | L | 56-ps1-tracking |
| [154](154-a2600-core-build.md) | Build Stella 2014 from a pinned commit for host and device and record its licence | 14 | cores | feature | S | 153-atari-tracking |
| [155](155-a7800-core-build.md) | Build ProSystem from a pinned commit for host and device and record its licence | 14 | cores | feature | S | 153-atari-tracking |
| [156](156-platform-a2600.md) | Add Platform::A2600 with its own shelf, scan and explicit policy | 14 | platform | feature | M | 154-a2600-core-build |
| [157](157-a2600-options.md) | Set the Stella 2014 core options slot relies on | 14 | cores | feature | S | 156-platform-a2600 |
| [158](158-a2600-canvas-screen.md) | Give the 2600 the 360x240 canvas with doubled columns, a crop rule for tall frames, and its own Screen section | 14 | video | feature | M | 157-a2600-options |
| [159](159-a2600-input-switches.md) | Map the 2600 joystick and console switches | 14 | input | feature | M | 156-platform-a2600 |
| [160](160-a2600-pal-pacing.md) | Pace PAL 2600 games at 49.92 Hz with a PAL Speed row | 14 | video | feature | S | 158-a2600-canvas-screen, 66-pal-pacing |
| [161](161-a2600-carts.md) | Draw 2600 carts and fetch their labels | 14 | ui-art | feature | M | 156-platform-a2600 |
| [162](162-a2600-device-gate.md) | Atari 2600 device gate on the RG34XXSP | 14 | device | chore | S | 158-a2600-canvas-screen, 159-a2600-input-switches, 160-a2600-pal-pacing |
| [163](163-platform-a7800.md) | Add Platform::A7800 with its own shelf, scan, header handling and explicit policy | 14 | platform | feature | M | 155-a7800-core-build |
| [164](164-a7800-options.md) | Set the ProSystem core options and say there is no high score cart | 14 | cores | feature | S | 163-platform-a7800 |
| [165](165-a7800-bios.md) | 7800 BIOS row: Off by default, On with a checked file | 14 | platform | feature | S | 163-platform-a7800 |
| [166](166-a7800-canvas-screen.md) | Give the 7800 the 360x240 canvas with a crop rule for PAL and its own Screen section | 14 | video | feature | S | 164-a7800-options |
| [167](167-a7800-input-switches.md) | Map the 7800 joystick, buttons and console switches | 14 | input | feature | M | 163-platform-a7800 |
| [168](168-a7800-pal-pacing.md) | Pace PAL 7800 games at 50 Hz with a PAL Speed row | 14 | video | feature | S | 166-a7800-canvas-screen, 66-pal-pacing |
| [169](169-a7800-carts.md) | Draw 7800 carts and fetch their labels | 14 | ui-art | feature | M | 163-platform-a7800 |
| [170](170-a7800-device-gate.md) | Atari 7800 device gate on the RG34XXSP | 14 | device | chore | S | 165-a7800-bios, 166-a7800-canvas-screen, 167-a7800-input-switches, 168-a7800-pal-pacing |
| [171](171-atari-tests.md) | Test both Atari cores with generated carts | 14 | tests | test | S | 154-a2600-core-build, 155-a7800-core-build |
| [172](172-deferred-atari-controllers.md) | DEFERRED: Atari paddles, keypads and the other special controllers | 6 | input | chore | L | 159-a2600-input-switches |
| [173](173-vb-tracking.md) | Virtual Boy: Beetle VB, one eye on the flat panel, a shelf of its own | 16 | device | tracking | L | 143-s32x-tracking |
| [174](174-vb-core-build.md) | Build Beetle VB from a pinned commit for host and device with the VR view off and record its licence | 16 | cores | feature | S | 173-vb-tracking |
| [175](175-platform-vb.md) | Add Platform::Vb with its own shelf and explicit policy | 16 | platform | feature | M | 174-vb-core-build |
| [176](176-vb-options.md) | Set the Beetle VB options: anaglyph with the preset off, the right stick as the right D-pad | 16 | cores | feature | S | 175-platform-vb |
| [177](177-vb-screen.md) | Give the Virtual Boy its own Screen section with Shader, Picture, VB Speed, Palette and Right Pad | 16 | video | feature | M | 176-vb-options |
| [178](178-vb-saves.md) | Virtual Boy saves: the ordinary .sav for the 64 KB cart RAM | 16 | platform | chore | S | 175-platform-vb |
| [179](179-vb-input.md) | Map the Virtual Boy pad: the right stick as the right D-pad, an ABXY fallback | 16 | input | feature | M | 175-platform-vb |
| [180](180-vb-tests.md) | Test the Virtual Boy with a generated two-eye cart, and GBA after the Virtual Boy | 16 | tests | test | S | 174-vb-core-build |
| [181](181-vb-carts.md) | Draw the Virtual Boy cart and fetch its labels | 16 | ui-art | feature | M | 175-platform-vb |
| [182](182-vb-device-gate.md) | Virtual Boy device gate on the RG34XXSP | 16 | device | chore | S | 177-vb-screen, 179-vb-input |
