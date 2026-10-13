# Performance evaluation, automated play on the device

    date 2026-10-13-shaders-warm
    device Linux 4.9.170 aarch64
    governor performance
    power Full 
    input nodes: A /dev/input/event1, B /dev/input/event1, START /dev/input/event1, MENU /dev/input/event1, hat /dev/input/event1
    play 2 minutes per run, 1 runs per pair

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
| shader-btoads-crt-pi | 1 | 861.200 | 861.200 | n/a |
| shader-smrpg-crt-pi | 1 | 665.500 | 665.500 | n/a |
| shader-smrpg-sharp | 1 | 843.300 | 843.300 | n/a |

## Insert or resume to first game frame (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 354.800 | 354.800 | n/a |
| shader-smrpg-crt-pi | 1 | 269.800 | 269.800 | n/a |
| shader-smrpg-sharp | 1 | 648.900 | 648.900 | n/a |

## Audio starved samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-sharp | 1 | 0.000 | 0.000 | n/a |

## Audio dropped samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-sharp | 1 | 0.000 | 0.000 | n/a |

## Audio starved, trace maximum (per 300 frames, cumulative)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-sharp | 1 | 0.000 | 0.000 | n/a |

## Audio dropped, trace maximum

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-sharp | 1 | 0.000 | 0.000 | n/a |

## Input latency median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 16.500 | 16.500 | n/a |
| shader-smrpg-crt-pi | 1 | 28.000 | 28.000 | n/a |
| shader-smrpg-sharp | 1 | 27.700 | 27.700 | n/a |

## Input latency p99 (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 24.700 | 24.700 | n/a |
| shader-smrpg-crt-pi | 1 | 50.100 | 50.100 | n/a |
| shader-smrpg-sharp | 1 | 50.000 | 50.000 | n/a |

## Input latency max (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 25.200 | 25.200 | n/a |
| shader-smrpg-crt-pi | 1 | 50.400 | 50.400 | n/a |
| shader-smrpg-sharp | 1 | 50.200 | 50.200 | n/a |

## Presents that missed a latch (total over the session)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-pi | 1 | 1.000 | 1.000 | n/a |
| shader-smrpg-sharp | 1 | 0.000 | 0.000 | n/a |

## Presents drawn early (total)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 26.000 | 26.000 | n/a |
| shader-smrpg-crt-pi | 1 | 7.000 | 7.000 | n/a |
| shader-smrpg-sharp | 1 | 18.000 | 18.000 | n/a |

## Work per frame, median over 600 frame windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 6.300 | 6.300 | n/a |
| shader-smrpg-crt-pi | 1 | 16.300 | 16.300 | n/a |
| shader-smrpg-sharp | 1 | 15.500 | 15.500 | n/a |

## Work per frame, worst 600 frame window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 8.300 | 8.300 | n/a |
| shader-smrpg-crt-pi | 1 | 17.900 | 17.900 | n/a |
| shader-smrpg-sharp | 1 | 17.400 | 17.400 | n/a |

## Present period, median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 16.780 | 16.780 | n/a |
| shader-smrpg-crt-pi | 1 | 16.790 | 16.790 | n/a |
| shader-smrpg-sharp | 1 | 16.790 | 16.790 | n/a |

## Present interval p50, median over windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 16.790 | 16.790 | n/a |
| shader-smrpg-crt-pi | 1 | 16.780 | 16.780 | n/a |
| shader-smrpg-sharp | 1 | 16.790 | 16.790 | n/a |

## Present interval p99, worst window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 17.350 | 17.350 | n/a |
| shader-smrpg-crt-pi | 1 | 19.150 | 19.150 | n/a |
| shader-smrpg-sharp | 1 | 18.550 | 18.550 | n/a |

## Present interval, longest (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 23.590 | 23.590 | n/a |
| shader-smrpg-crt-pi | 1 | 29.900 | 29.900 | n/a |
| shader-smrpg-sharp | 1 | 19.680 | 19.680 | n/a |

## Crash lines

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-sharp | 1 | 0.000 | 0.000 | n/a |

## Sessions that ended cleanly (summary line present)

| Pair | Runs | Clean |
|---|---|---|
| shader-btoads-crt-pi | 1 | 1 |
| shader-smrpg-crt-pi | 1 | 1 |
| shader-smrpg-sharp | 1 | 1 |
