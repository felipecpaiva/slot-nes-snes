# Draft: post on slot discussion #64

Not posted. Felipe posts it himself, after nelynes has seen the design
([modular-platforms.md](modular-platforms.md)). Keep it this short.

---

Hi Brandon, a question before I write any code for you.

You said on #30 that slot will not add more systems, and I respect that. This is not a request
for NES or SNES.

Keeping NES, SNES and three Sega systems on top of slot taught me where a new system has to touch
your code: 217 hunks in 37 of your files, most of them one more arm in a match on `Platform` or
`Core`. nelynes carries the same kind of patch for WonderSwan and Lynx.

What I would like to offer is a refactor with zero behaviour change for GBA, GB and GBC:

- one table per platform (folder, extensions, cores, which features it has) instead of matches
  spread over the app, with the Screen page and per-system settings built from it;
- the game canvas taken from the core instead of the fixed 240x160.

No new systems, no new dependencies, same `slot.state` bytes, your tests unedited. It would come
as about 8 small steps, the first one just naming the places where the code asks "is this a GBA?"
(link cable, core picker, shoulders, bezel, run-ahead).

The whole design, with every touch point counted, is here:
https://github.com/felipecpaiva/slot-nes-snes/blob/main/docs/design/modular-platforms.md

Two questions:

1. Do you want this at all? A no is a fine answer, we keep maintaining our patches.
2. If yes, how do you prefer to receive it? I cannot open PRs on the repo (GitHub refuses
   `CreatePullRequest` for my account), so a branch you read and rewrite, the way you did with the
   lazy shelf in 3339c6f, works for me. So does a written design first.

Thanks for slot, and for crediting everyone in the v1.7.0 notes.

Felipe
