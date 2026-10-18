# PR title

Ask before deleting a save state, and move through the switcher with Up and Down

# PR body

## Problem

In the save state switcher one Y press deletes the selected state, and undo covers saves and
loads, not deletes. A mis-press loses the state. The switcher also moves only with Left and Right,
while Up and Down do nothing.

## Change

- Y asks first: the top plate reads "Delete this state?" and the hints become B Keep / Y Delete.
  A second Y deletes. Any other press keeps the state and does nothing else, so an A meant for
  the question never loads the state.
- Up moves to the next newer state, Down to the next older one.
- The ring stays ten deep.

## Tests

- `crates/slot/tests/delete.rs`: the five tests that delete now press Y twice (this PR changes
  that behaviour on purpose).
- New: one Y only asks; B keeps the state and stays in the switcher; A while asking neither loads
  nor deletes; Down moves to the next older state; Up moves back to the next newer one.

## Credit

From suprsomething/slot.advance 2fe9876 (GPL-3.0), without its change of the ring to five states.
