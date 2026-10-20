# Draft issue for pvaibhav/BaseOS (not posted)

Status: draft for the maintainer to decide on. Nothing here has been posted.

---

**Title:** Setting to choose the frontend card: `frontend_card=auto|tf1|tf2` in baseos.conf

**Body:**

On a two-slot device (RG34XXSP here, BaseOS 1.3.0), `/etc/init.d/rcS` mounts the frontend card at
`/mnt/sdcard` by trying `/dev/mmcblk1p1` (TF2 p1) first, with vfat, then exfat, then one
`fsck.fat -a` and vfat or `-t auto`, and only then `/dev/mmcblk0p7` (TF1 p7).
`/sbin/frontend-session` retries in the same order. There is no setting for this, so any TF2 whose
first partition mounts becomes the frontend card.

That default suits "OS on TF1, everything else on TF2". It rules out the opposite layout: frontend,
saves and settings on TF1, and TF2 as a plain storage card that the frontend mounts itself (for
example a large card holding only CD-based games). Today the only way to keep TF1 as the frontend card
with a card in TF2 is to make TF2 p1 something no filesystem driver accepts. We do that now with a
16 MiB partition of zeros before an exFAT data partition, which works but is a trick a user can undo by
formatting the card on a computer.

**Proposal.** One new key in TF1's `baseos.conf`:

```
# Which card holds the frontend: auto (TF2 first, then TF1, as today), tf1 or tf2.
# frontend_card=auto
```

- `auto` (the default, also for a missing or unknown value) keeps today's order, so nothing changes
  for existing users.
- `tf1` tries only `/dev/mmcblk0p7`. TF2 is left unmounted for the frontend to use.
- `tf2` tries only `/dev/mmcblk1p1`, and shows the existing "INSERT SD CARD" message when it is
  missing instead of falling back.

Two details we noticed while reading 1.3.0:

1. rcS reads `baseos.conf` after the card loop (it reuses TF1 at `/mnt/sdcard` or mounts it read-only
   at `/mnt/system`). The key would need to be read before the loop, for example by mounting TF1 p7
   read-only at `/mnt/system` first, reading the one key with the same data-not-code parser as
   `baseos-config`, and unmounting it. TF1 is always present, so this costs one mount on a normal boot.
2. `frontend-session` has its own copy of the device order in its retry loop. It would need the same
   value, for example from `/run/baseos.conf`, which `baseos-config` already writes.

USB storage mode could stay as it is (TF2 whole disk when present), or follow the same key so `tf1`
exports TF1 p7. We have no strong view on that part.

Happy to send a PR if the key name and the values look right to you.

---

Context for us (not part of the issue): ADR 0098, `System/expansion.sh`, `tools/expansion-card.py`.
If BaseOS ships this, the Expansion Card no longer needs a zeroed p1, but the bind mounts stay.
