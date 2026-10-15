# 0044. Retire named test site (c): upstream deleted label_top

- Status: Accepted. Amends [0013](0013-five-named-test-sites.md)
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0038](0038-rebase-to-slot-v1-7-0.md), CONTRIBUTING.md section 1, `scripts/check-upstream-tests.sh`

## Context

Site (c) let `label_top` in `crates/slot/tests/render_shelves.rs` gain `| CartPlatform::Nes` and
`| CartPlatform::Snes`. slot v1.7.0 removed that helper and has no exhaustive match over
`CartPlatform` left in the file, so the patch set no longer touches it.

## Decision

Remove site (c) from CONTRIBUTING.md and its case from `check-upstream-tests.sh`. The file must
now be byte-identical to upstream like every other test file. Sites (a), (b), (d), (e) and (f)
are unchanged; site (f) still places the two shader lines directly after
`shader_gb: Shader::Simpletex,` (v1.7.0 puts `shader_gbc` after them).

## Consequences

- Five named sites remain. No site was added.
