# Draft issue for BrandonKowalski/slot (not posted)

Status: draft for the maintainer to decide on. Nothing here has been posted.

---

**Title:** Say why the shelf came up after a start that took slot down, and keep that cart selected

**Body:**

v1.9.0 starts on the shelf when a cart took slot down while it was loading (`start_after_a_crash`). The
player sees the shelf with no explanation and, because `state.cart` is cleared, with whatever cart the
shelf happens to select first. On a card with hundreds of games the cart that crashed is hard to find
again, and the player cannot tell a crash from a fresh boot.

**Proposal.** In `start_after_a_crash`, select the cart that crashed on its shelf (`seat_of(stem, platform)`,
the same lookup a normal start uses) and show a banner, "Last start failed", through the existing toast
list. The resume state is already moved aside, so tapping A starts it clean.

Our fork carries this as about fifteen lines (`App::show_start_failed`, one `Toast` variant) hooked in
`start_after_a_crash`, and would drop it on the release that ships it.
