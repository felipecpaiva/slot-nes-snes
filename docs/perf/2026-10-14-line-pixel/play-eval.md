# Performance evaluation, automated play on the device

    date 2026-10-14-line-pixel
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
| shader-btoads-line | 1 | 931.400 | 931.400 | n/a |
| shader-btoads-pixel | 1 | 695.600 | 695.600 | n/a |
| shader-smrpg-line | 1 | 922.200 | 922.200 | n/a |
| shader-smrpg-pixel | 1 | 739.800 | 739.800 | n/a |
| shader-smrpg-scanlines | 1 | 737.100 | 737.100 | n/a |

## Insert or resume to first game frame (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 352.800 | 352.800 | n/a |
| shader-btoads-pixel | 1 | 137.200 | 137.200 | n/a |
| shader-smrpg-line | 1 | 27981.500 | 27981.500 | n/a |
| shader-smrpg-pixel | 1 | 278.000 | 278.000 | n/a |
| shader-smrpg-scanlines | 1 | 278.800 | 278.800 | n/a |

## Audio starved samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 0.000 | 0.000 | n/a |
| shader-btoads-pixel | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-line | 1 | 1024.000 | 1024.000 | n/a |
| shader-smrpg-pixel | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-scanlines | 1 | 0.000 | 0.000 | n/a |

## Audio dropped samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 0.000 | 0.000 | n/a |
| shader-btoads-pixel | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-line | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-pixel | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-scanlines | 1 | 0.000 | 0.000 | n/a |

## Audio starved, trace maximum (per 300 frames, cumulative)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 0.000 | 0.000 | n/a |
| shader-btoads-pixel | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-line | 1 | 1024.000 | 1024.000 | n/a |
| shader-smrpg-pixel | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-scanlines | 1 | 0.000 | 0.000 | n/a |

## Audio dropped, trace maximum

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 0.000 | 0.000 | n/a |
| shader-btoads-pixel | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-line | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-pixel | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-scanlines | 1 | 0.000 | 0.000 | n/a |

## Input latency median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 16.300 | 16.300 | n/a |
| shader-btoads-pixel | 1 | 16.300 | 16.300 | n/a |
| shader-smrpg-line | 1 | 27.600 | 27.600 | n/a |
| shader-smrpg-pixel | 1 | 27.700 | 27.700 | n/a |
| shader-smrpg-scanlines | 1 | 28.000 | 28.000 | n/a |

## Input latency p99 (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 24.700 | 24.700 | n/a |
| shader-btoads-pixel | 1 | 24.300 | 24.300 | n/a |
| shader-smrpg-line | 1 | 49.900 | 49.900 | n/a |
| shader-smrpg-pixel | 1 | 50.000 | 50.000 | n/a |
| shader-smrpg-scanlines | 1 | 48.500 | 48.500 | n/a |

## Input latency max (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 25.700 | 25.700 | n/a |
| shader-btoads-pixel | 1 | 25.000 | 25.000 | n/a |
| shader-smrpg-line | 1 | 50.300 | 50.300 | n/a |
| shader-smrpg-pixel | 1 | 50.400 | 50.400 | n/a |
| shader-smrpg-scanlines | 1 | 48.900 | 48.900 | n/a |

## Presents that missed a latch (total over the session)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 0.000 | 0.000 | n/a |
| shader-btoads-pixel | 1 | 1.000 | 1.000 | n/a |
| shader-smrpg-line | 1 | 5.000 | 5.000 | n/a |
| shader-smrpg-pixel | 1 | 1.000 | 1.000 | n/a |
| shader-smrpg-scanlines | 1 | 1.000 | 1.000 | n/a |

## Presents drawn early (total)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 26.000 | 26.000 | n/a |
| shader-btoads-pixel | 1 | 26.000 | 26.000 | n/a |
| shader-smrpg-line | 1 | 64.000 | 64.000 | n/a |
| shader-smrpg-pixel | 1 | 4.000 | 4.000 | n/a |
| shader-smrpg-scanlines | 1 | 4.000 | 4.000 | n/a |

## Work per frame, median over 600 frame windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 6.100 | 6.100 | n/a |
| shader-btoads-pixel | 1 | 6.900 | 6.900 | n/a |
| shader-smrpg-line | 1 | 15.100 | 15.100 | n/a |
| shader-smrpg-pixel | 1 | 15.900 | 15.900 | n/a |
| shader-smrpg-scanlines | 1 | 17.100 | 17.100 | n/a |

## Work per frame, worst 600 frame window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 8.300 | 8.300 | n/a |
| shader-btoads-pixel | 1 | 7.900 | 7.900 | n/a |
| shader-smrpg-line | 1 | 17.800 | 17.800 | n/a |
| shader-smrpg-pixel | 1 | 17.600 | 17.600 | n/a |
| shader-smrpg-scanlines | 1 | 18.900 | 18.900 | n/a |

## Present period, median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 16.800 | 16.800 | n/a |
| shader-btoads-pixel | 1 | 16.780 | 16.780 | n/a |
| shader-smrpg-line | 1 | 16.780 | 16.780 | n/a |
| shader-smrpg-pixel | 1 | 16.780 | 16.780 | n/a |
| shader-smrpg-scanlines | 1 | 16.770 | 16.770 | n/a |

## Present interval p50, median over windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 16.780 | 16.780 | n/a |
| shader-btoads-pixel | 1 | 16.780 | 16.780 | n/a |
| shader-smrpg-line | 1 | 16.790 | 16.790 | n/a |
| shader-smrpg-pixel | 1 | 16.790 | 16.790 | n/a |
| shader-smrpg-scanlines | 1 | 16.790 | 16.790 | n/a |

## Present interval p99, worst window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 17.330 | 17.330 | n/a |
| shader-btoads-pixel | 1 | 17.350 | 17.350 | n/a |
| shader-smrpg-line | 1 | 24.300 | 24.300 | n/a |
| shader-smrpg-pixel | 1 | 18.110 | 18.110 | n/a |
| shader-smrpg-scanlines | 1 | 18.580 | 18.580 | n/a |

## Present interval, longest (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 19.330 | 19.330 | n/a |
| shader-btoads-pixel | 1 | 92.000 | 92.000 | n/a |
| shader-smrpg-line | 1 | 70.680 | 70.680 | n/a |
| shader-smrpg-pixel | 1 | 30.880 | 30.880 | n/a |
| shader-smrpg-scanlines | 1 | 47.340 | 47.340 | n/a |

## Crash lines

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-line | 1 | 0.000 | 0.000 | n/a |
| shader-btoads-pixel | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-line | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-pixel | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-scanlines | 1 | 0.000 | 0.000 | n/a |

## Sessions that ended cleanly (summary line present)

| Pair | Runs | Clean |
|---|---|---|
| shader-btoads-line | 1 | 1 |
| shader-btoads-pixel | 1 | 1 |
| shader-smrpg-line | 1 | 1 |
| shader-smrpg-pixel | 1 | 1 |
| shader-smrpg-scanlines | 1 | 1 |
