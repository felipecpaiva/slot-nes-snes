# 0041. Drop audio-release-pace: upstream paces the released device

- Status: Accepted
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0038](0038-rebase-to-slot-v1-7-0.md), [ADR 0030](0030-keep-alsa-open-while-fed.md), slot #70

## Context

Our patch 0016 made the audio thread sleep to absolute deadlines while the ALSA device is
released, so a released consumer drains at real time. slot v1.7.0 adds `audio/pacer.rs`: the same
absolute-deadline sleep, resynced after 4 late spans and reset while the device is open.

## Decision

Drop patch 0016 and `released_pace.rs`. Patch audio-reopen (now 0018) builds on upstream's
`Pacer` instead and still replaces `Silence` with `Hold`, because v1.7.0 still releases the
device after 3 s of silence even while a game feeds it.

## Consequences

- Upstream resyncs after 4 spans late where ours resynced at once; one burst of up to 4 periods
  after a stall is possible. Check the audio starve lines on the device (`task readout:device`).
