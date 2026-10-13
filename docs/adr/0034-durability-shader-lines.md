# 0034. Allow the two shader lines in durability.rs's SlotState literal (named test site f)

- Status: Accepted
- Date: 2026-10-13
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0013](0013-five-named-test-sites.md), [CONTRIBUTING.md](../../CONTRIBUTING.md), issue 21 (NES and SNES shaders)

## Context

`a_card_from_before_the_settings_keeps_all_its_values` in upstream's
`crates/slot-store/tests/durability.rs` builds a full `SlotState` literal with no
`..Default::default()`. Giving NES and SNES their own stored shaders adds the required fields
`shader_nes` and `shader_snes`, so that literal no longer compiles unless it names them.

## Decision

Add a sixth named site, (f), to the upstream test guard: that literal gains exactly
`shader_nes: Shader::Off,` and `shader_snes: Shader::Off,`, in that order, directly after
`shader_gb: Shader::Simpletex,`. Any other change to that file still fails the guard.

## Consequences

- Every other `SlotState` addition must avoid this literal. Shelf memory (ADR 0025) went to its
  own file, `Config/shelf.state`, for this reason.
- `scripts/check-upstream-tests.sh` checks the exact lines on every `task check`.
