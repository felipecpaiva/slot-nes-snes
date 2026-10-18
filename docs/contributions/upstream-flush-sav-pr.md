# PR title

Write the battery save on a flush, an eject or an autosave even when the core gives no state

# PR body

## Problem

`App::flush_resume` returns as soon as `snapshot.state()` is `None`:

```rust
let Some(state) = snapshot.state() else {
    eprintln!("slot: flush: the core gave up no state");
    return;
};
```

So when `serialize` fails at a lid close or a POWER tap, neither `resume.state` nor the `.sav` is
written. The doze then powers off after its timeout and the game held in RAM is lost, including
progress the game had already saved to its battery RAM. `flush_eject` and `autosave` return the
same way, so an eject also loses the `.sav` and leaves the cart recorded in `slot.state`.

## Change

When the core gives no state, `flush_resume`, `flush_eject` and `autosave` still write the save
RAM (filtered by `save_ram_trusted`, as `trusted_write` does) with no state, and log
`slot: <verb>: the core gave up no state, writing the save ram alone`. The eject then finishes as
usual. The missing state is not counted as a card write failure.

A blank save RAM cannot reach the card this way: the emu worker only answers `Cmd::Sav` after the
ROM and the `.sav` are loaded, and a failed load ends the thread, so `save_ram()` is `None`.

## Tests

New `crates/slot/tests/flush_without_state.rs`, with a snapshot whose `state()` is `None` and whose
`save_ram()` is `Some`, one test each for a POWER tap, an eject and the 60 s autosave: the `.sav`
holds the bytes. All three fail on the current code (`left: None`) and pass now. `cargo test --workspace` passes.

## Credit

The idea comes from suprsomething/slot.advance dbbadae (GPL-3.0), which also reports the failed
flush to its sleep timer.
