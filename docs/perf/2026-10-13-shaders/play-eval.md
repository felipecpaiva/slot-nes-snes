# Performance evaluation, automated play on the device

    date 2026-10-13-shaders
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
| shader-btoads-crt-pi | 1 | 647.100 | 647.100 | n/a |
| shader-btoads-off | 1 | 825.900 | 825.900 | n/a |
| shader-smrpg-crt-1tap | 1 | 658.200 | 658.200 | n/a |
| shader-smrpg-crt-pi | 1 | 652.800 | 652.800 | n/a |
| shader-smrpg-off | 1 | 824.300 | 824.300 | n/a |
| shader-smrpg-scanlines | 1 | 641.500 | 641.500 | n/a |
| shader-smrpg-sharp | 1 | 649.400 | 649.400 | n/a |

## Insert or resume to first game frame (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 165.600 | 165.600 | n/a |
| shader-btoads-off | 1 | 298.400 | 298.400 | n/a |
| shader-smrpg-crt-1tap | 1 | 261.500 | 261.500 | n/a |
| shader-smrpg-crt-pi | 1 | 244.600 | 244.600 | n/a |
| shader-smrpg-off | 1 | 611.800 | 611.800 | n/a |
| shader-smrpg-scanlines | 1 | 256.400 | 256.400 | n/a |
| shader-smrpg-sharp | 1 | 232.600 | 232.600 | n/a |

## Audio starved samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-btoads-off | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-1tap | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-off | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-scanlines | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-sharp | 1 | 0.000 | 0.000 | n/a |

## Audio dropped samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-btoads-off | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-1tap | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-off | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-scanlines | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-sharp | 1 | 0.000 | 0.000 | n/a |

## Audio starved, trace maximum (per 300 frames, cumulative)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-btoads-off | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-1tap | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-off | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-scanlines | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-sharp | 1 | 0.000 | 0.000 | n/a |

## Audio dropped, trace maximum

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-btoads-off | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-1tap | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-off | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-scanlines | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-sharp | 1 | 0.000 | 0.000 | n/a |

## Input latency median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 16.600 | 16.600 | n/a |
| shader-btoads-off | 1 | 16.600 | 16.600 | n/a |
| shader-smrpg-crt-1tap | 1 | 38.500 | 38.500 | n/a |
| shader-smrpg-crt-pi | 1 | 28.800 | 28.800 | n/a |
| shader-smrpg-off | 1 | 38.600 | 38.600 | n/a |
| shader-smrpg-scanlines | 1 | 28.800 | 28.800 | n/a |
| shader-smrpg-sharp | 1 | 26.900 | 26.900 | n/a |

## Input latency p99 (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 23.900 | 23.900 | n/a |
| shader-btoads-off | 1 | 24.100 | 24.100 | n/a |
| shader-smrpg-crt-1tap | 1 | 50.300 | 50.300 | n/a |
| shader-smrpg-crt-pi | 1 | 49.300 | 49.300 | n/a |
| shader-smrpg-off | 1 | 50.300 | 50.300 | n/a |
| shader-smrpg-scanlines | 1 | 49.700 | 49.700 | n/a |
| shader-smrpg-sharp | 1 | 49.400 | 49.400 | n/a |

## Input latency max (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 24.900 | 24.900 | n/a |
| shader-btoads-off | 1 | 24.300 | 24.300 | n/a |
| shader-smrpg-crt-1tap | 1 | 51.000 | 51.000 | n/a |
| shader-smrpg-crt-pi | 1 | 50.200 | 50.200 | n/a |
| shader-smrpg-off | 1 | 51.500 | 51.500 | n/a |
| shader-smrpg-scanlines | 1 | 50.400 | 50.400 | n/a |
| shader-smrpg-sharp | 1 | 50.400 | 50.400 | n/a |

## Presents that missed a latch (total over the session)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 1.000 | 1.000 | n/a |
| shader-btoads-off | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-1tap | 1 | 1.000 | 1.000 | n/a |
| shader-smrpg-crt-pi | 1 | 2.000 | 2.000 | n/a |
| shader-smrpg-off | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-scanlines | 1 | 1.000 | 1.000 | n/a |
| shader-smrpg-sharp | 1 | 1.000 | 1.000 | n/a |

## Presents drawn early (total)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 27.000 | 27.000 | n/a |
| shader-btoads-off | 1 | 63.000 | 63.000 | n/a |
| shader-smrpg-crt-1tap | 1 | 5.000 | 5.000 | n/a |
| shader-smrpg-crt-pi | 1 | 5.000 | 5.000 | n/a |
| shader-smrpg-off | 1 | 17.000 | 17.000 | n/a |
| shader-smrpg-scanlines | 1 | 5.000 | 5.000 | n/a |
| shader-smrpg-sharp | 1 | 3.000 | 3.000 | n/a |

## Work per frame, median over 600 frame windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 6.300 | 6.300 | n/a |
| shader-btoads-off | 1 | 6.100 | 6.100 | n/a |
| shader-smrpg-crt-1tap | 1 | 15.700 | 15.700 | n/a |
| shader-smrpg-crt-pi | 1 | 15.400 | 15.400 | n/a |
| shader-smrpg-off | 1 | 16.100 | 16.100 | n/a |
| shader-smrpg-scanlines | 1 | 16.600 | 16.600 | n/a |
| shader-smrpg-sharp | 1 | 16.500 | 16.500 | n/a |

## Work per frame, worst 600 frame window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 7.500 | 7.500 | n/a |
| shader-btoads-off | 1 | 7.400 | 7.400 | n/a |
| shader-smrpg-crt-1tap | 1 | 18.500 | 18.500 | n/a |
| shader-smrpg-crt-pi | 1 | 17.200 | 17.200 | n/a |
| shader-smrpg-off | 1 | 17.800 | 17.800 | n/a |
| shader-smrpg-scanlines | 1 | 19.100 | 19.100 | n/a |
| shader-smrpg-sharp | 1 | 18.500 | 18.500 | n/a |

## Present period, median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 16.780 | 16.780 | n/a |
| shader-btoads-off | 1 | 16.780 | 16.780 | n/a |
| shader-smrpg-crt-1tap | 1 | 16.790 | 16.790 | n/a |
| shader-smrpg-crt-pi | 1 | 16.780 | 16.780 | n/a |
| shader-smrpg-off | 1 | 16.780 | 16.780 | n/a |
| shader-smrpg-scanlines | 1 | 16.790 | 16.790 | n/a |
| shader-smrpg-sharp | 1 | 16.770 | 16.770 | n/a |

## Present interval p50, median over windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 16.780 | 16.780 | n/a |
| shader-btoads-off | 1 | 16.790 | 16.790 | n/a |
| shader-smrpg-crt-1tap | 1 | 16.780 | 16.780 | n/a |
| shader-smrpg-crt-pi | 1 | 16.790 | 16.790 | n/a |
| shader-smrpg-off | 1 | 16.780 | 16.780 | n/a |
| shader-smrpg-scanlines | 1 | 16.790 | 16.790 | n/a |
| shader-smrpg-sharp | 1 | 16.790 | 16.790 | n/a |

## Present interval p99, worst window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 17.360 | 17.360 | n/a |
| shader-btoads-off | 1 | 17.350 | 17.350 | n/a |
| shader-smrpg-crt-1tap | 1 | 18.620 | 18.620 | n/a |
| shader-smrpg-crt-pi | 1 | 18.380 | 18.380 | n/a |
| shader-smrpg-off | 1 | 18.860 | 18.860 | n/a |
| shader-smrpg-scanlines | 1 | 18.820 | 18.820 | n/a |
| shader-smrpg-sharp | 1 | 18.380 | 18.380 | n/a |

## Present interval, longest (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 66.660 | 66.660 | n/a |
| shader-btoads-off | 1 | 22.500 | 22.500 | n/a |
| shader-smrpg-crt-1tap | 1 | 32.470 | 32.470 | n/a |
| shader-smrpg-crt-pi | 1 | 30.970 | 30.970 | n/a |
| shader-smrpg-off | 1 | 19.620 | 19.620 | n/a |
| shader-smrpg-scanlines | 1 | 32.140 | 32.140 | n/a |
| shader-smrpg-sharp | 1 | 33.950 | 33.950 | n/a |

## Crash lines

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| shader-btoads-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-btoads-off | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-1tap | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-crt-pi | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-off | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-scanlines | 1 | 0.000 | 0.000 | n/a |
| shader-smrpg-sharp | 1 | 0.000 | 0.000 | n/a |

## Sessions that ended cleanly (summary line present)

| Pair | Runs | Clean |
|---|---|---|
| shader-btoads-crt-pi | 1 | 1 |
| shader-btoads-off | 1 | 1 |
| shader-smrpg-crt-1tap | 1 | 1 |
| shader-smrpg-crt-pi | 1 | 1 |
| shader-smrpg-off | 1 | 1 |
| shader-smrpg-scanlines | 1 | 1 |
| shader-smrpg-sharp | 1 | 1 |
