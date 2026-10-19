---
title: "Set the WonderSwan core options: 60 Hz mode, rotation and keymap on every load"
phase: 11
area: cores
type: feature
size: S
depends_on: [93-platform-wswan]
---

## Why
Step 5. Two of Cygne's declared defaults are not what it does when slot leaves them unanswered (slot answers declared defaults for pcsx_rearmed only, ADR 0064): `wswan_60hz_mode` declares `enabled` but runs at 75.47 fps, and `wswan_rotate_display` falls to `manual`, where every SELECT press turns the picture. Both are pinned by `wswan_core.rs` (patch 0064).

## Scope
- [ ] Set before load, every load: `wswan_60hz_mode` (`enabled`, or `disabled` when the Refresh row says Native, issue 95), `wswan_rotate_display` (`portrait` when the footer's vertical bit is set, else `landscape`; the flip of issue 96 changes it in game), `wswan_rotate_keymap=disabled` (slot is the only mapper).
- [ ] Also pinned explicitly so a future pin cannot change them silently: `wswan_language=english`, `wswan_frameskip=disabled`, `wswan_sound_sample_rate=44100`, `wswan_gfx_colors=16bit`, `wswan_name_source` and the owner profile keys (`wswan_birth_*`, `wswan_sex`, `wswan_blood`) to fixed values so the internal EEPROM is the same on every boot.
- [ ] Record in the patch commit why ADR 0064's declared-defaults answer is not extended to Cygne: setting each key is explicit and testable, and the declared default of `wswan_rotate_display` is the trap itself.
- [ ] The declared-key check (`core_option_keys.rs`) covers `mednafen_wswan` with the `wswan` prefix.

## Tests
| ID | File | Asserts |
|---|---|---|
| (done) | `wswan_core.rs` `unanswered_60hz_mode_runs_at_the_native_75_47_fps_despite_its_declared_default` | the trap |
| (done) | `wswan_core.rs` `select_turns_the_picture_only_while_rotate_display_is_left_on_manual` | the trap |
| (new) | `core_option_keys.rs` | every key slot sets for mednafen_wswan is declared by the core |
| (new) | `wswan_options.rs` `a_horizontal_cart_opens_at_60_38_fps_in_landscape` | through slot's policy, not hand-set: av fps 60.38, frame 224 wide, SELECT does not turn it |
| (new) | `wswan_options.rs` `a_vertical_cart_opens_in_portrait` | footer bit 0 set: frame 144 wide |
| (new) | `wswan_options.rs` `native_refresh_opens_at_75_47_fps` | Refresh Native: av fps 75.47 |

## Edge cases
| Case | Expected handling |
|---|---|
| A future pin adds keys | The declared-key test still passes; new keys keep core startup values until answered |
| Refresh changed while a game runs | Applies from the next game (the core's `SET_SYSTEM_AV_INFO` is read only at spawn) |

## Acceptance
- [ ] `task check` green; each new test red with its option removed.

## Device check (RG34XXSP)
None.

## References
- ADR 0064, 0071, 0092; docs/research/wswan-plan.md sections 2 and 3
