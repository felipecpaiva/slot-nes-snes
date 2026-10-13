# Performance evaluation, automated play on the device

    date 2026-10-13-fix
    device Linux 4.9.170 aarch64
    governor performance
    power Full 
    input nodes: A /dev/input/event1, B /dev/input/event1, START /dev/input/event1, MENU /dev/input/event1, hat /dev/input/event1
    play 3 minutes per run, 1 runs per pair

Each cell is median / worst over runs. Every run plays the same script on every core: START x3, then right held with A every 700 ms and B every 2.3 s, then eject. Latency is input to screen swap. Slot logs no per-frame wall time: the pace lines (work per frame, missed latches) are the nearest frame-time figure, and only exist with the latency trace on. Starved and dropped count samples, not events. A run without a session summary line did not end cleanly.

## GBA mGBA baseline, heavy and light side by side

| Metric | gba-mgba-heavy | gba-mgba-light |
|---|---|---|
| Boot to first frame (ms) | n/a | n/a |
| Insert or resume to first game frame (ms) | n/a | n/a |
| Audio starved samples, session total | n/a | n/a |
| Audio dropped samples, session total | n/a | n/a |
| Audio starved, trace maximum (per 300 frames, cumulative) | n/a | n/a |
| Audio dropped, trace maximum | n/a | n/a |
| Input latency median (ms) | n/a | n/a |
| Input latency p99 (ms) | n/a | n/a |
| Input latency max (ms) | n/a | n/a |
| Presents that missed a latch (total over the session) | n/a | n/a |
| Presents drawn early (total) | n/a | n/a |
| Work per frame, median over 600 frame windows (ms) | n/a | n/a |
| Work per frame, worst 600 frame window (ms) | n/a | n/a |
| Present period, median (ms) | n/a | n/a |
| Present interval p50, median over windows (ms) | n/a | n/a |
| Present interval p99, worst window (ms) | n/a | n/a |
| Present interval, longest (ms) | n/a | n/a |
| Crash lines | n/a | n/a |

## Boot to first frame (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 751.800 | 751.800 | n/a |
| nes-nestopia-light | 1 | 955.000 | 955.000 | n/a |
| snes-snes9x-heavy | 1 | 740.100 | 740.100 | n/a |

## Insert or resume to first game frame (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 292.500 | 292.500 | n/a |
| nes-nestopia-light | 1 | 641.600 | 641.600 | n/a |
| snes-snes9x-heavy | 1 | 467.800 | 467.800 | n/a |

## Audio starved samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 3072.000 | 3072.000 | n/a |
| nes-nestopia-light | 1 | 5120.000 | 5120.000 | n/a |
| snes-snes9x-heavy | 1 | 5120.000 | 5120.000 | n/a |

## Audio dropped samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 33756.000 | 33756.000 | n/a |
| nes-nestopia-light | 1 | 32776.000 | 32776.000 | n/a |
| snes-snes9x-heavy | 1 | 22506.000 | 22506.000 | n/a |

## Audio starved, trace maximum (per 300 frames, cumulative)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 3072.000 | 3072.000 | n/a |
| nes-nestopia-light | 1 | 5120.000 | 5120.000 | n/a |
| snes-snes9x-heavy | 1 | 5120.000 | 5120.000 | n/a |

## Audio dropped, trace maximum

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 33756.000 | 33756.000 | n/a |
| nes-nestopia-light | 1 | 32776.000 | 32776.000 | n/a |
| snes-snes9x-heavy | 1 | 22506.000 | 22506.000 | n/a |

## Input latency median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 16.400 | 16.400 | n/a |
| nes-nestopia-light | 1 | 16.800 | 16.800 | n/a |
| snes-snes9x-heavy | 1 | 22.800 | 22.800 | n/a |

## Input latency p99 (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 25.700 | 25.700 | n/a |
| nes-nestopia-light | 1 | 25.300 | 25.300 | n/a |
| snes-snes9x-heavy | 1 | 31.800 | 31.800 | n/a |

## Input latency max (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 29.600 | 29.600 | n/a |
| nes-nestopia-light | 1 | 29.800 | 29.800 | n/a |
| snes-snes9x-heavy | 1 | 39.800 | 39.800 | n/a |

## Presents that missed a latch (total over the session)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 0.000 | 0.000 | n/a |
| nes-nestopia-light | 1 | 0.000 | 0.000 | n/a |
| snes-snes9x-heavy | 1 | 0.000 | 0.000 | n/a |

## Presents drawn early (total)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 116.000 | 116.000 | n/a |
| nes-nestopia-light | 1 | 106.000 | 106.000 | n/a |
| snes-snes9x-heavy | 1 | 100.000 | 100.000 | n/a |

## Work per frame, median over 600 frame windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 6.300 | 6.300 | n/a |
| nes-nestopia-light | 1 | 7.300 | 7.300 | n/a |
| snes-snes9x-heavy | 1 | 12.600 | 12.600 | n/a |

## Work per frame, worst 600 frame window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 7.900 | 7.900 | n/a |
| nes-nestopia-light | 1 | 8.700 | 8.700 | n/a |
| snes-snes9x-heavy | 1 | 15.400 | 15.400 | n/a |

## Present period, median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 16.790 | 16.790 | n/a |
| nes-nestopia-light | 1 | 16.790 | 16.790 | n/a |
| snes-snes9x-heavy | 1 | 16.780 | 16.780 | n/a |

## Present interval p50, median over windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 16.780 | 16.780 | n/a |
| nes-nestopia-light | 1 | 16.780 | 16.780 | n/a |
| snes-snes9x-heavy | 1 | 16.790 | 16.790 | n/a |

## Present interval p99, worst window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 17.330 | 17.330 | n/a |
| nes-nestopia-light | 1 | 17.350 | 17.350 | n/a |
| snes-snes9x-heavy | 1 | 17.910 | 17.910 | n/a |

## Present interval, longest (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 22.490 | 22.490 | n/a |
| nes-nestopia-light | 1 | 21.320 | 21.320 | n/a |
| snes-snes9x-heavy | 1 | 19.410 | 19.410 | n/a |

## Crash lines

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| nes-fceumm-light | 1 | 0.000 | 0.000 | n/a |
| nes-nestopia-light | 1 | 0.000 | 0.000 | n/a |
| snes-snes9x-heavy | 1 | 0.000 | 0.000 | n/a |

## Sessions that ended cleanly (summary line present)

| Pair | Runs | Clean |
|---|---|---|
| nes-fceumm-light | 1 | 1 |
| nes-nestopia-light | 1 | 1 |
| snes-snes9x-heavy | 1 | 1 |
