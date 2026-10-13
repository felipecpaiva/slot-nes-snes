# 0033. Keep upstream's lid behaviour: doze, then power off after 3 minutes

- Status: Accepted
- Date: 2026-10-13
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0025](0025-shelf-memory.md)

## Context

Closing the RG34XXSP lid makes slot doze: it saves the state, turns the backlight off and pauses
the core, which stays loaded (`doze()` in app.rs). Opening the lid within 3 minutes returns to the
game at once. After 3 minutes closed (`DOZE_TIMEOUT` in frontend.rs) slot powers the device off.
A cart that was playing stays recorded in slot.state, so the next boot resumes it with no action.
A longer timeout was considered so that coming back stays instant for longer.

## Decision

Keep upstream's 3-minute doze timeout and power-off. No patch.

## Consequences

- Battery is saved while the lid is closed.
- Coming back after more than 3 minutes costs about 2 s of boot, then the game resumes by itself.
- With shelf memory (ADR 0025), a device closed on the shelf boots back to the same shelf and cart.
