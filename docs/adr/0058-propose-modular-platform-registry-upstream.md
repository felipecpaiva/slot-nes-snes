# 0058. Propose a modular platform registry upstream, asked first on discussion #64

- Status: Proposed
- Date: 2026-10-16
- Deciders: maintainer (Felipe Paiva)
- Related: [docs/design/modular-platforms.md](../design/modular-platforms.md),
  [docs/design/modular-discussion-draft.md](../design/modular-discussion-draft.md),
  [docs/UPSTREAM-TOUCHPOINTS.md](../UPSTREAM-TOUCHPOINTS.md), ADR 0001, 0009, 0013, 0024, 0027, 0047

## Context

The maintainer asked for PRs to BrandonKowalski/slot that add no systems and instead make slot
modular, so the community can build system modules the way we do. Brandon declined more systems
(slot#30). He takes generic improvements but lands them himself (our lazy-shelf fix came back
rewritten as 3339c6f). Our account cannot open PRs on his repo (`CreatePullRequest` refused).

Of our 262 upstream hunks, 217 (867 lines, 37 files) exist only because upstream has no
per-platform seam: exhaustive matches on `Platform` and `Core`, triple per-platform fields and
rows, a fixed 240x160 canvas. Upstream tests pin some of the literals, which is why we keep five
named test sites. nelynes/slotPlus pays the same cost for WonderSwan and Lynx.

## Decision

- Propose upstream a compile-time registry: a `PlatformSpec` const per platform (identity, cores,
  capabilities, play policy), a `CoreSpec` per core, a `CartLook` per platform in slot-ui, and
  the Screen page and per-system settings generated from the table. No runtime plugin loading,
  no new dependency.
- Deliver it as eight small PRs, each with zero behaviour change for GBA, GB and GBC and useful
  alone, starting with naming the `!= Platform::Gba` gates and ending with optional uninhabited
  extension stubs (`Platform::Ext(ExtPlatform)`) that make a fork's module edit no upstream logic.
- `Platform::ALL`, `Core::ALL`, `QuickRow::ALL`, `QuickRow::SCREEN` and the `SlotState` fields
  keep their upstream values, so upstream's tests stay unedited. Platforms outside the three keep
  their settings in `Config/platform_settings.txt` (ADR 0051 made generic).
- First step is a short post on discussion #64 asking whether he wants this and how. Nothing is
  posted, pushed or opened until the maintainer approves the post.

## Consequences

- If accepted in full, our upstream touch points fall from 217 platform hunks to three stub
  files, plus one arm per new upstream match on `Platform` at rebase (Rust 1.96 lets upstream
  omit `Ext` arms). Named test sites (f), (g) and (h) go away; (b) and (e) only if upstream takes
  the optional test rewordings.
- If declined, nothing changes: our policy files already follow this shape, and the design keeps
  guiding how we add systems.
- Each PR is proven in our tree first: upstream suite unedited, frame-hash tests (ADR 0045),
  `bench:compare` GBA within 2%, `harness/downgrade.rs`.
- Cost: our NES and SNES shader keys move out of `slot.state` once PR 7 lands (a one-time read of
  the old keys). On each rebase, recheck the counts in the design against the touch-point map.
