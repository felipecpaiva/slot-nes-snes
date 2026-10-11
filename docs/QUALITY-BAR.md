Build NES and SNES as first-class platforms in slot (github.com/BrandonKowalski/slot, pinned at v1.6.0), shipped as a small patch set on top of that release: own Games/NES and Games/SNES shelves, own core choice and settings, fceumm and snes9x cores. Research and file:line map are in docs/RESEARCH.md. Clone is a local clone of slot.

The bar is unpatched slot v1.6.0 playing a GBA cart in its host app. Build it first and compare against it directly: insert, boot to first frame, save, save state, rewind, fast-forward, quick menu, eject, resume on boot, and the frame times from core_bench. GBA and GB output must stay byte-identical, and every upstream test must pass unchanged.

Break this into the smallest pieces that can be judged on their own. For each piece, fan out a builder and a separate critic with fresh context. The critic runs the real build, puts our NES/SNES recording and numbers next to the GBA bar blind with labels stripped, says which feels better, and names the single biggest remaining gap. Then it goes back to the builder.

The critic should be a harsh critic. Praise is not useful. If ours does not match, it keeps going.

/loop on each piece until the critic cannot tell ours from the bar. Do not stop before that.

Keep a live progress page updating as the work evolves so I can watch it.

Fan out subagents and ultracode.
