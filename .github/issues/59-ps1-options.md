---
title: "Set the PS1 core options and answer pcsx's declared defaults"
phase: 8
area: cores
type: feature
size: S
depends_on: [58-platform-ps1]
---

## Why
Step 6. pcsx renders on the emu thread unless its threaded-rendering key is answered (ADR 0064). States are too big for rewind (ADR 0066).

## Scope
- [ ] Explicit values in `core_options_policy.rs`: `pcsx_rearmed_bios=auto`, `memcard1=libretro` (128 KB SAVE_RAM to `Saves/PS1/<stem>.srm`, one card shared by every disc), `memcard2=none`, `frameskip_type=disabled`, `neon_enhancement_enable=disabled`, `gpu_thread_rendering=auto`, `drc_thread=auto`.
- [ ] For pcsx_rearmed only: an unset key the core declared is answered with its declared default; explicit values win; undeclared keys still return false. mGBA, gpSP and our other cores unchanged.
- [ ] Rewind and run-ahead off for PS1 (ADR 0066).

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot/tests/ps1_options.rs` | each explicit key answered; a declared but unset key returns its default; an undeclared key returns false; mGBA gets no default answers |
| (new) | same | no rewind capture on PS1 |

## Edge cases
| Case | Expected handling |
|---|---|
| A future pin renames a key | The option test fails on the rebase |

## Acceptance
- [ ] Tests green; GBA harness compare at 0 diffs.

## Device check (RG34XXSP)
Spyro mean ms a frame near the spike's 2.17, with threads on.

## References
- ADR 0064, 0066; docs/research/ps1-spike.md Results
