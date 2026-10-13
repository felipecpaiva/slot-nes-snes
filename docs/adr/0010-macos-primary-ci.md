# 0010. Run tests on macOS; Linux arm only builds device artefacts

- Status: Accepted
- Date: 2026-10-11
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 03](../../.github/issues/03-task-check-and-upstream-guard.md), [issue 29](../../.github/issues/29-ci-test-workflow.md), [issue 30](../../.github/issues/30-release-workflow.md)

## Context

slot's host core tasks assert `Mach-O` (`taskfile.yml:83-127`), slot-retro tests hardcode
`vendor/*.dylib`, and `HeadlessSurface` is macOS-only. Upstream has no test workflow.

## Decision

A macOS job runs every test, the harness and the benches. A Linux arm job only builds the device
artefacts, the zip and the ship checks. `release.yml` needs both.

## Consequences

- Upstream tests run where they were written to run.
- Render tests are gated with `#![cfg(target_os = "macos")]`, like upstream.
- Linux runs no tests. The device container uses the floating `rust:1-bullseye` tag, an accepted
  gap ([SUPPLY-CHAIN.md](../SUPPLY-CHAIN.md)).
