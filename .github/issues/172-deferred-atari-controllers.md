---
title: "DEFERRED: Atari paddles, keypads and the other special controllers"
phase: 6
area: input
type: chore
size: L
depends_on: [159-a2600-input-switches]
---

## Why
Matched against Stella's database, 35 of his 559 recognised 2600 dumps need paddles (Kaboom!, Breakout, Super Breakout, Warlords, Circus Atari, Night Driver, Street Racer, Video Olympics, Canyon Bomber, Demons to Diamonds, Casino, Party Mix, Steeplechase, ...), 15 a keypad or kids controller (Star Raiders, BASIC Programming, Codebreaker, Brain Games, Hunt & Score, Alpha Beam with Ernie, Big Bird's Egg Catch, Cookie Monster Munch, Oscar's Trash Race, ...), Indy 500 the driving controller, 3 the Mindlink and Smurfs Save the Day the Kid Vid. Out of scope for the first release.

## Scope
- [x] Paddles: done in patch 0099. slot answers Stella's analog queries with the left stick (the port stays a RetroPad) and A or B press the paddle button; Stella picks paddles per game from its `Controller.Left` property. Device check in issue 162.
- [ ] Keypad: an on-screen 12-key overlay, only if asked for.
- [ ] 7800 High Score Cartridge: only if a core gains it (issue 164).

## Tests
| ID | File | Asserts |
|---|---|---|
| (later) | n/a | n/a |

## Edge cases
| Case | Expected handling |
|---|---|
| n/a | n/a |

## Acceptance
- [ ] Decided when the maintainer asks.

## Device check (RG34XXSP)
Later.

## References
- ADR 0095; docs/research/atari-plan.md
