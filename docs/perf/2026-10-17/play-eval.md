# Performance evaluation, automated play on the device

    date 2026-10-17
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
| ps1-pcsx_rearmed-heavy | 1 | 1574.500 | 1574.500 | n/a |
| ps1-pcsx_rearmed-light | 1 | 1628.400 | 1628.400 | n/a |

## Insert or resume to first game frame (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 974.600 | 974.600 | n/a |
| ps1-pcsx_rearmed-light | 1 | 1078.500 | 1078.500 | n/a |

## Audio starved samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 0.000 | 0.000 | n/a |
| ps1-pcsx_rearmed-light | 1 | 0.000 | 0.000 | n/a |

## Audio dropped samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 0.000 | 0.000 | n/a |
| ps1-pcsx_rearmed-light | 1 | 0.000 | 0.000 | n/a |

## Audio starved, trace maximum (per 300 frames, cumulative)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 0.000 | 0.000 | n/a |
| ps1-pcsx_rearmed-light | 1 | 0.000 | 0.000 | n/a |

## Audio dropped, trace maximum

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 0.000 | 0.000 | n/a |
| ps1-pcsx_rearmed-light | 1 | 0.000 | 0.000 | n/a |

## Input latency median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 24.100 | 24.100 | n/a |
| ps1-pcsx_rearmed-light | 1 | 19.600 | 19.600 | n/a |

## Input latency p99 (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 46.400 | 46.400 | n/a |
| ps1-pcsx_rearmed-light | 1 | 30.600 | 30.600 | n/a |

## Input latency max (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 50.200 | 50.200 | n/a |
| ps1-pcsx_rearmed-light | 1 | 43.600 | 43.600 | n/a |

## Presents that missed a latch (total over the session)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 2.000 | 2.000 | n/a |
| ps1-pcsx_rearmed-light | 1 | 2.000 | 2.000 | n/a |

## Presents drawn early (total)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 2995.000 | 2995.000 | n/a |
| ps1-pcsx_rearmed-light | 1 | 844.000 | 844.000 | n/a |

## Work per frame, median over 600 frame windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 14.900 | 14.900 | n/a |
| ps1-pcsx_rearmed-light | 1 | 10.600 | 10.600 | n/a |

## Work per frame, worst 600 frame window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 17.700 | 17.700 | n/a |
| ps1-pcsx_rearmed-light | 1 | 19.800 | 19.800 | n/a |

## Present period, median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 16.780 | 16.780 | n/a |
| ps1-pcsx_rearmed-light | 1 | 16.780 | 16.780 | n/a |

## Present interval p50, median over windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 16.790 | 16.790 | n/a |
| ps1-pcsx_rearmed-light | 1 | 16.790 | 16.790 | n/a |

## Present interval p99, worst window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 17.690 | 17.690 | n/a |
| ps1-pcsx_rearmed-light | 1 | 19.070 | 19.070 | n/a |

## Present interval, longest (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 61.440 | 61.440 | n/a |
| ps1-pcsx_rearmed-light | 1 | 152.780 | 152.780 | n/a |

## Crash lines

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 0.000 | 0.000 | n/a |
| ps1-pcsx_rearmed-light | 1 | 0.000 | 0.000 | n/a |

## Sessions that ended cleanly (summary line present)

| Pair | Runs | Clean |
|---|---|---|
| ps1-pcsx_rearmed-heavy | 1 | 1 |
| ps1-pcsx_rearmed-light | 1 | 1 |
