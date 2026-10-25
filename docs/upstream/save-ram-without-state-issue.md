# Draft issue for BrandonKowalski/slot (not posted)

Status: draft for the maintainer to decide on. Nothing here has been posted. GitHub refuses pull
requests from our account on this repository, so this is an issue text.

---

**Title:** A core that gives no state loses its save at eject and at the five minute tick

**Body:**

In v1.9.0 `App::autosave` writes the game's own save every minute (`trusted_sav`) and the resume state
every five minutes. Two paths still return without writing the save when the core cannot give a state
(`Snapshot::state()` is `None`: the core has no savestates, or it did not answer within the new 2 s limit):

1. `flush_eject` logs "the core gave up no state" and passes `(None, None)` to `persist::eject`, so the
   `.sav` is not written on an eject even though `save_ram()` has it.
2. The resume branch of `autosave()` logs the same line and returns, so on a five minute tick the save
   of that core is skipped as well (the minute ticks write it, so this loses at most a minute).

`flush_resume` (doze, power tap) has the same early return and drops the save when the power then goes off.

A core with battery or flash saves and no states is a real case (PICO-8 cartdata, cores that refuse
`serialize`), and a core that is slow for 2 s on `state()` is another. The save is the thing that must
not be lost.

**Proposal.** When `state()` is `None`, still ask `save_ram()` and write it, with the log line saying so:

```rust
None => (None, trusted_sav(snapshot.as_ref(), "eject")),
```

in `flush_eject`, the same in the resume branch of `autosave()` and in `flush_resume`. A test that gives
`Snapshot` a `None` state and a `Some` save, then ejects, ticks 5 minutes and dozes, and reads the `.sav`.

We carry this as a patch on our fork (`flush-sav-without-state`) and would drop it on the release that
ships it.
