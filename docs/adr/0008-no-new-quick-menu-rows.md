# 0008. Add no quick menu rows; NES and SNES shaders change with SELECT+B/A

- Status: Superseded by [0023](0023-quick-menu-shader-rows.md)
- Date: 2026-10-11
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 21](../../.github/issues/21-shaders.md), [patch 0014](../../patches/0014-shaders.patch), [PLAN.md](../PLAN.md) Open questions (OQ2)

## Context

Upstream's `quick_menu.rs` tests pin `QuickRow::SCREEN` at exactly four rows. NES and SNES needed
their own shader choice. Resolved by the user as OQ2 during planning.

## Decision

No new quick menu rows. NES and SNES shaders change only with in-game SELECT+B/A, stored as
`shader_nes` and `shader_snes`.

## Consequences

- Every upstream quick menu test stays unmodified.
- Cost: NES and SNES shaders were not where users find them on GBA and GB. Reversed for shaders on
  2026-10-13 by [0023](0023-quick-menu-shader-rows.md).
