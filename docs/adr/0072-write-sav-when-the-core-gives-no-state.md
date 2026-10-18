# 0072. Write the battery save on a flush, an eject or an autosave even when the core gives no state

- Status: Accepted. Drop when the upstream PR lands (0047)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0047](0047-upstream-first-fixes.md), [ADR 0033](0033-keep-upstream-lid-timeout.md), patch `patches/0044-flush-sav-without-state.patch`, [fork review](../research/fork-review-2026-10-18.md), suprsomething/slot.advance [dbbadae](https://github.com/suprsomething/slot.advance/commit/dbbadae), upstream PR text in [docs/contributions/upstream-flush-sav-pr.md](../contributions/upstream-flush-sav-pr.md)

## Context

`App::flush_resume` (lid close, POWER tap, battery critical, the power menu) asks the core for a
state, and when `snapshot.state()` is `None` it logs "the core gave up no state" and returns
before writing `resume.state` or the `.sav`. The doze then powers off after its timeout (ADR 0033)
and the game held in RAM is gone, battery save included. `state()` is `None` when `serialize`
fails or the emu thread has gone. `flush_eject` and `autosave` return the same way, so an eject
with no state also skips the `.sav` and leaves the cart recorded in `slot.state`. The bug is in
v1.7.0 and in upstream main.

suprsomething/slot.advance (GPL-3.0) fixed it in dbbadae, together with a sleep timer that retries
the flush. We take only the generic half.

## Decision

When the core gives no state, `flush_resume`, `flush_eject` and `autosave` still write the save
RAM, filtered by `save_ram_trusted` as `trusted_write` does, with no state, and log
`slot: <flush|eject|autosave>: the core gave up no state, writing the save ram alone`. The shared
step is `save_ram_alone` in the new file `crates/slot/src/no_state.rs`. An eject with no state now
finishes the eject (the cart is cleared from `slot.state`) like one with a state. The missing state is not
reported to `card_writes`: that is the SD card signal, and the card did not fail. The fork's
`Snapshot::running()` is not needed: the emu worker answers `Cmd::Sav` only after the ROM and the
`.sav` are loaded, and a failed load ends the thread, so `save_ram()` is `None`, never a blank
buffer that could overwrite the player's `.sav`.

## Consequences

- A serialise failure at doze no longer loses battery-saved progress. Riskiest on PS1 (4.4 MB
  states).
- `crates/slot/tests/flush_without_state.rs`, a silent snapshot (state `None`, save RAM `Some`),
  one test each: a doze with a POWER tap, an eject, and the 60 s autosave all leave the `.sav`
  holding its bytes. Each was red without its part of the fix.
- **Drop the patch when the upstream PR lands.**
