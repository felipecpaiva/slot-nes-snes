# Performance evaluation, automated play on the device

    date 2026-10-13-audio
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
| gate-battletoads | 1 | 743.900 | 743.900 | n/a |
| gate-gba-ref | 1 | 667.200 | 667.200 | n/a |
| gate-kirbyadv | 1 | 580.500 | 580.500 | n/a |
| gate-smrpg | 1 | 726.100 | 726.100 | n/a |

## Insert or resume to first game frame (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 357.400 | 357.400 | n/a |
| gate-gba-ref | 1 | 349.600 | 349.600 | n/a |
| gate-kirbyadv | 1 | 166.100 | 166.100 | n/a |
| gate-smrpg | 1 | 625.800 | 625.800 | n/a |

## Audio starved samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 0.000 | 0.000 | n/a |
| gate-gba-ref | 1 | 0.000 | 0.000 | n/a |
| gate-kirbyadv | 1 | 0.000 | 0.000 | n/a |
| gate-smrpg | 1 | 0.000 | 0.000 | n/a |

## Audio dropped samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 0.000 | 0.000 | n/a |
| gate-gba-ref | 1 | 0.000 | 0.000 | n/a |
| gate-kirbyadv | 1 | 0.000 | 0.000 | n/a |
| gate-smrpg | 1 | 0.000 | 0.000 | n/a |

## Audio starved, trace maximum (per 300 frames, cumulative)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 0.000 | 0.000 | n/a |
| gate-gba-ref | 1 | 0.000 | 0.000 | n/a |
| gate-kirbyadv | 1 | 0.000 | 0.000 | n/a |
| gate-smrpg | 1 | 0.000 | 0.000 | n/a |

## Audio dropped, trace maximum

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 0.000 | 0.000 | n/a |
| gate-gba-ref | 1 | 0.000 | 0.000 | n/a |
| gate-kirbyadv | 1 | 0.000 | 0.000 | n/a |
| gate-smrpg | 1 | 0.000 | 0.000 | n/a |

## Input latency median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 16.100 | 16.100 | n/a |
| gate-gba-ref | 1 | 18.100 | 18.100 | n/a |
| gate-kirbyadv | 1 | 16.400 | 16.400 | n/a |
| gate-smrpg | 1 | 31.100 | 31.100 | n/a |

## Input latency p99 (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 24.900 | 24.900 | n/a |
| gate-gba-ref | 1 | 27.100 | 27.100 | n/a |
| gate-kirbyadv | 1 | 24.700 | 24.700 | n/a |
| gate-smrpg | 1 | 49.700 | 49.700 | n/a |

## Input latency max (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 25.200 | 25.200 | n/a |
| gate-gba-ref | 1 | 29.100 | 29.100 | n/a |
| gate-kirbyadv | 1 | 25.300 | 25.300 | n/a |
| gate-smrpg | 1 | 50.200 | 50.200 | n/a |

## Presents that missed a latch (total over the session)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 0.000 | 0.000 | n/a |
| gate-gba-ref | 1 | 0.000 | 0.000 | n/a |
| gate-kirbyadv | 1 | 1.000 | 1.000 | n/a |
| gate-smrpg | 1 | 0.000 | 0.000 | n/a |

## Presents drawn early (total)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 27.000 | 27.000 | n/a |
| gate-gba-ref | 1 | 46.000 | 46.000 | n/a |
| gate-kirbyadv | 1 | 21.000 | 21.000 | n/a |
| gate-smrpg | 1 | 17.000 | 17.000 | n/a |

## Work per frame, median over 600 frame windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 6.500 | 6.500 | n/a |
| gate-gba-ref | 1 | 8.200 | 8.200 | n/a |
| gate-kirbyadv | 1 | 7.500 | 7.500 | n/a |
| gate-smrpg | 1 | 15.600 | 15.600 | n/a |

## Work per frame, worst 600 frame window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 7.600 | 7.600 | n/a |
| gate-gba-ref | 1 | 10.200 | 10.200 | n/a |
| gate-kirbyadv | 1 | 8.100 | 8.100 | n/a |
| gate-smrpg | 1 | 16.900 | 16.900 | n/a |

## Present period, median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 16.780 | 16.780 | n/a |
| gate-gba-ref | 1 | 16.780 | 16.780 | n/a |
| gate-kirbyadv | 1 | 16.790 | 16.790 | n/a |
| gate-smrpg | 1 | 16.790 | 16.790 | n/a |

## Present interval p50, median over windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 16.780 | 16.780 | n/a |
| gate-gba-ref | 1 | 16.790 | 16.790 | n/a |
| gate-kirbyadv | 1 | 16.780 | 16.780 | n/a |
| gate-smrpg | 1 | 16.790 | 16.790 | n/a |

## Present interval p99, worst window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 17.400 | 17.400 | n/a |
| gate-gba-ref | 1 | 18.260 | 18.260 | n/a |
| gate-kirbyadv | 1 | 17.360 | 17.360 | n/a |
| gate-smrpg | 1 | 19.020 | 19.020 | n/a |

## Present interval, longest (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 18.310 | 18.310 | n/a |
| gate-gba-ref | 1 | 19.200 | 19.200 | n/a |
| gate-kirbyadv | 1 | 69.770 | 69.770 | n/a |
| gate-smrpg | 1 | 22.460 | 22.460 | n/a |

## Crash lines

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 0.000 | 0.000 | n/a |
| gate-gba-ref | 1 | 0.000 | 0.000 | n/a |
| gate-kirbyadv | 1 | 0.000 | 0.000 | n/a |
| gate-smrpg | 1 | 0.000 | 0.000 | n/a |

## Sessions that ended cleanly (summary line present)

| Pair | Runs | Clean |
|---|---|---|
| gate-battletoads | 1 | 1 |
| gate-gba-ref | 1 | 1 |
| gate-kirbyadv | 1 | 1 |
| gate-smrpg | 1 | 1 |
