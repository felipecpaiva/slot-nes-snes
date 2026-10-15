# Performance evaluation, automated play on the device

    date 2026-10-15-v170
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
| v170-btoads | 1 | 1193.500 | 1193.500 | n/a |
| v170-gsun | 1 | 1513.400 | 1513.400 | n/a |
| v170-smrpg | 1 | 1228.100 | 1228.100 | n/a |

## Insert or resume to first game frame (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 729.700 | 729.700 | n/a |
| v170-gsun | 1 | 1121.400 | 1121.400 | n/a |
| v170-smrpg | 1 | 817.200 | 817.200 | n/a |

## Audio starved samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 0.000 | 0.000 | n/a |
| v170-gsun | 1 | 0.000 | 0.000 | n/a |
| v170-smrpg | 1 | 2560.000 | 2560.000 | n/a |

## Audio dropped samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 0.000 | 0.000 | n/a |
| v170-gsun | 1 | 0.000 | 0.000 | n/a |
| v170-smrpg | 1 | 0.000 | 0.000 | n/a |

## Audio starved, trace maximum (per 300 frames, cumulative)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 0.000 | 0.000 | n/a |
| v170-gsun | 1 | 0.000 | 0.000 | n/a |
| v170-smrpg | 1 | 2560.000 | 2560.000 | n/a |

## Audio dropped, trace maximum

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 0.000 | 0.000 | n/a |
| v170-gsun | 1 | 0.000 | 0.000 | n/a |
| v170-smrpg | 1 | 0.000 | 0.000 | n/a |

## Input latency median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 17.000 | 17.000 | n/a |
| v170-gsun | 1 | 18.500 | 18.500 | n/a |
| v170-smrpg | 1 | 28.000 | 28.000 | n/a |

## Input latency p99 (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 24.700 | 24.700 | n/a |
| v170-gsun | 1 | 27.400 | 27.400 | n/a |
| v170-smrpg | 1 | 48.400 | 48.400 | n/a |

## Input latency max (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 25.300 | 25.300 | n/a |
| v170-gsun | 1 | 28.300 | 28.300 | n/a |
| v170-smrpg | 1 | 50.100 | 50.100 | n/a |

## Presents that missed a latch (total over the session)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 1.000 | 1.000 | n/a |
| v170-gsun | 1 | 2.000 | 2.000 | n/a |
| v170-smrpg | 1 | 1.000 | 1.000 | n/a |

## Presents drawn early (total)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 26.000 | 26.000 | n/a |
| v170-gsun | 1 | 62.000 | 62.000 | n/a |
| v170-smrpg | 1 | 0.000 | 0.000 | n/a |

## Work per frame, median over 600 frame windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 6.400 | 6.400 | n/a |
| v170-gsun | 1 | 7.700 | 7.700 | n/a |
| v170-smrpg | 1 | 16.900 | 16.900 | n/a |

## Work per frame, worst 600 frame window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 9.100 | 9.100 | n/a |
| v170-gsun | 1 | 10.300 | 10.300 | n/a |
| v170-smrpg | 1 | 18.100 | 18.100 | n/a |

## Present period, median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 16.780 | 16.780 | n/a |
| v170-gsun | 1 | 16.780 | 16.780 | n/a |
| v170-smrpg | 1 | 16.770 | 16.770 | n/a |

## Present interval p50, median over windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 16.780 | 16.780 | n/a |
| v170-gsun | 1 | 16.790 | 16.790 | n/a |
| v170-smrpg | 1 | 16.780 | 16.780 | n/a |

## Present interval p99, worst window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 17.360 | 17.360 | n/a |
| v170-gsun | 1 | 18.230 | 18.230 | n/a |
| v170-smrpg | 1 | 17.720 | 17.720 | n/a |

## Present interval, longest (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 35.940 | 35.940 | n/a |
| v170-gsun | 1 | 116.200 | 116.200 | n/a |
| v170-smrpg | 1 | 42.530 | 42.530 | n/a |

## Crash lines

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| v170-btoads | 1 | 0.000 | 0.000 | n/a |
| v170-gsun | 1 | 0.000 | 0.000 | n/a |
| v170-smrpg | 1 | 0.000 | 0.000 | n/a |

## Sessions that ended cleanly (summary line present)

| Pair | Runs | Clean |
|---|---|---|
| v170-btoads | 1 | 1 |
| v170-gsun | 1 | 1 |
| v170-smrpg | 1 | 1 |
