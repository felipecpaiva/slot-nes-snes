# 0013. Allow upstream test edits only at named sites checked by the guard

- Status: Accepted. Amends [0011](0011-one-token-in-two-test-files.md) and [0012](0012-durability-value-pce.md). Amended by [0044](0044-test-site-c-gone.md)
- Date: 2026-10-12
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 03](../../.github/issues/03-task-check-and-upstream-guard.md), [issue 14](../../.github/issues/14-libretro-env-and-hires.md), [patch 0003](../../patches/0003-core-fceumm.patch), [patch 0006](../../patches/0006-libretro-env.patch), `scripts/check-upstream-tests.sh`, CONTRIBUTING.md section 1

## Context

Adding `Core::Fceumm` makes the colour-correction match in `gpsp.rs` non-exhaustive, so it cannot
compile unchanged. More such sites would follow with each new variant.

## Decision

Upstream test edits happen only at named sites, each checked exactly by `check-upstream-tests.sh`:
`libretro.rs` one `#[cfg(test)] mod env_tests;`; `label_band` in `chrome.rs` and `label_top` in
`render_shelves.rs` (the `Nes` then optional `Snes` token on the Game Boy arm); the `durability.rs`
value `cart_platform=pce`; the `gpsp.rs` colour-correction match (`Core::Fceumm`, then optional
`Nestopia`, `Snes9x`, `Snes9x2005Plus` on the `Core::Mgba` arm). A new site may be added without
asking only if it appends a variant token to an existing arm of an existing exhaustive match and
is named in the guard. Any other upstream test change stops and asks.

## Consequences

- Every edit to upstream test code is listed and byte-checked by `task check`.
- CONTRIBUTING.md section 1 now lists a sixth site, (f): `shader_nes` and `shader_snes` in the full
  `SlotState` literal in `durability.rs`, approved by the maintainer on 2026-10-13 (issue 21).
- On each rebase: `check-upstream-tests.sh` must pass against the new upstream test files.
