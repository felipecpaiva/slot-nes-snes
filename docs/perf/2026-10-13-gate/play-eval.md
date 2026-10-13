# Performance evaluation, automated play on the device

    date 2026-10-13-gate
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
| gate-battletoads | 1 | 535.300 | 535.300 | n/a |
| gate-cv3 | 1 | 564.500 | 564.500 | n/a |
| gate-gba-ref | 1 | 750.800 | 750.800 | n/a |
| gate-kirbyadv | 1 | 587.400 | 587.400 | n/a |
| gate-kss | 1 | 552.500 | 552.500 | n/a |
| gate-rockman2 | 1 | 558.800 | 558.800 | n/a |
| gate-smb3 | 1 | 739.700 | 739.700 | n/a |
| gate-smrpg | 1 | 573.900 | 573.900 | n/a |
| gate-starfox | 1 | 751.100 | 751.100 | n/a |
| gate-yoshi | 1 | 563.500 | 563.500 | n/a |

## Insert or resume to first game frame (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 155.800 | 155.800 | n/a |
| gate-cv3 | 1 | 133.500 | 133.500 | n/a |
| gate-gba-ref | 1 | 690.200 | 690.200 | n/a |
| gate-kirbyadv | 1 | 167.800 | 167.800 | n/a |
| gate-kss | 1 | 497.900 | 497.900 | n/a |
| gate-rockman2 | 1 | 134.100 | 134.100 | n/a |
| gate-smb3 | 1 | 354.600 | 354.600 | n/a |
| gate-smrpg | 1 | 453.400 | 453.400 | n/a |
| gate-starfox | 1 | 386.900 | 386.900 | n/a |
| gate-yoshi | 1 | 298.100 | 298.100 | n/a |

## Audio starved samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 3072.000 | 3072.000 | n/a |
| gate-cv3 | 1 | 3072.000 | 3072.000 | n/a |
| gate-gba-ref | 1 | 4096.000 | 4096.000 | n/a |
| gate-kirbyadv | 1 | 2048.000 | 2048.000 | n/a |
| gate-kss | 1 | 4096.000 | 4096.000 | n/a |
| gate-rockman2 | 1 | 5120.000 | 5120.000 | n/a |
| gate-smb3 | 1 | 2048.000 | 2048.000 | n/a |
| gate-smrpg | 1 | 4096.000 | 4096.000 | n/a |
| gate-starfox | 1 | 4096.000 | 4096.000 | n/a |
| gate-yoshi | 1 | 5120.000 | 5120.000 | n/a |

## Audio dropped samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 46336.000 | 46336.000 | n/a |
| gate-cv3 | 1 | 22394.000 | 22394.000 | n/a |
| gate-gba-ref | 1 | 22818.000 | 22818.000 | n/a |
| gate-kirbyadv | 1 | 0.000 | 0.000 | n/a |
| gate-kss | 1 | 0.000 | 0.000 | n/a |
| gate-rockman2 | 1 | 23318.000 | 23318.000 | n/a |
| gate-smb3 | 1 | 20594.000 | 20594.000 | n/a |
| gate-smrpg | 1 | 48038.000 | 48038.000 | n/a |
| gate-starfox | 1 | 21422.000 | 21422.000 | n/a |
| gate-yoshi | 1 | 22272.000 | 22272.000 | n/a |

## Audio starved, trace maximum (per 300 frames, cumulative)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 3072.000 | 3072.000 | n/a |
| gate-cv3 | 1 | 3072.000 | 3072.000 | n/a |
| gate-gba-ref | 1 | 4096.000 | 4096.000 | n/a |
| gate-kirbyadv | 1 | 2048.000 | 2048.000 | n/a |
| gate-kss | 1 | 4096.000 | 4096.000 | n/a |
| gate-rockman2 | 1 | 5120.000 | 5120.000 | n/a |
| gate-smb3 | 1 | 2048.000 | 2048.000 | n/a |
| gate-smrpg | 1 | 4096.000 | 4096.000 | n/a |
| gate-starfox | 1 | 4096.000 | 4096.000 | n/a |
| gate-yoshi | 1 | 5120.000 | 5120.000 | n/a |

## Audio dropped, trace maximum

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 46336.000 | 46336.000 | n/a |
| gate-cv3 | 1 | 22394.000 | 22394.000 | n/a |
| gate-gba-ref | 1 | 22818.000 | 22818.000 | n/a |
| gate-kirbyadv | 1 | 0.000 | 0.000 | n/a |
| gate-kss | 1 | 0.000 | 0.000 | n/a |
| gate-rockman2 | 1 | 23318.000 | 23318.000 | n/a |
| gate-smb3 | 1 | 20594.000 | 20594.000 | n/a |
| gate-smrpg | 1 | 48038.000 | 48038.000 | n/a |
| gate-starfox | 1 | 21422.000 | 21422.000 | n/a |
| gate-yoshi | 1 | 22272.000 | 22272.000 | n/a |

## Input latency median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 16.100 | 16.100 | n/a |
| gate-cv3 | 1 | 15.600 | 15.600 | n/a |
| gate-gba-ref | 1 | 17.800 | 17.800 | n/a |
| gate-kirbyadv | 1 | 16.500 | 16.500 | n/a |
| gate-kss | 1 | 24.100 | 24.100 | n/a |
| gate-rockman2 | 1 | 16.100 | 16.100 | n/a |
| gate-smb3 | 1 | 16.400 | 16.400 | n/a |
| gate-smrpg | 1 | 28.400 | 28.400 | n/a |
| gate-starfox | 1 | 22.900 | 22.900 | n/a |
| gate-yoshi | 1 | 22.200 | 22.200 | n/a |

## Input latency p99 (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 24.500 | 24.500 | n/a |
| gate-cv3 | 1 | 24.300 | 24.300 | n/a |
| gate-gba-ref | 1 | 27.600 | 27.600 | n/a |
| gate-kirbyadv | 1 | 24.800 | 24.800 | n/a |
| gate-kss | 1 | 33.100 | 33.100 | n/a |
| gate-rockman2 | 1 | 25.100 | 25.100 | n/a |
| gate-smb3 | 1 | 24.800 | 24.800 | n/a |
| gate-smrpg | 1 | 50.000 | 50.000 | n/a |
| gate-starfox | 1 | 31.700 | 31.700 | n/a |
| gate-yoshi | 1 | 32.800 | 32.800 | n/a |

## Input latency max (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 28.500 | 28.500 | n/a |
| gate-cv3 | 1 | 24.900 | 24.900 | n/a |
| gate-gba-ref | 1 | 30.700 | 30.700 | n/a |
| gate-kirbyadv | 1 | 25.400 | 25.400 | n/a |
| gate-kss | 1 | 33.400 | 33.400 | n/a |
| gate-rockman2 | 1 | 28.600 | 28.600 | n/a |
| gate-smb3 | 1 | 27.500 | 27.500 | n/a |
| gate-smrpg | 1 | 51.200 | 51.200 | n/a |
| gate-starfox | 1 | 32.200 | 32.200 | n/a |
| gate-yoshi | 1 | 38.900 | 38.900 | n/a |

## Presents that missed a latch (total over the session)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 1.000 | 1.000 | n/a |
| gate-cv3 | 1 | 2.000 | 2.000 | n/a |
| gate-gba-ref | 1 | 0.000 | 0.000 | n/a |
| gate-kirbyadv | 1 | 1.000 | 1.000 | n/a |
| gate-kss | 1 | 1.000 | 1.000 | n/a |
| gate-rockman2 | 1 | 2.000 | 2.000 | n/a |
| gate-smb3 | 1 | 0.000 | 0.000 | n/a |
| gate-smrpg | 1 | 1.000 | 1.000 | n/a |
| gate-starfox | 1 | 0.000 | 0.000 | n/a |
| gate-yoshi | 1 | 1.000 | 1.000 | n/a |

## Presents drawn early (total)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 144.000 | 144.000 | n/a |
| gate-cv3 | 1 | 109.000 | 109.000 | n/a |
| gate-gba-ref | 1 | 124.000 | 124.000 | n/a |
| gate-kirbyadv | 1 | 52.000 | 52.000 | n/a |
| gate-kss | 1 | 20.000 | 20.000 | n/a |
| gate-rockman2 | 1 | 84.000 | 84.000 | n/a |
| gate-smb3 | 1 | 82.000 | 82.000 | n/a |
| gate-smrpg | 1 | 18.000 | 18.000 | n/a |
| gate-starfox | 1 | 95.000 | 95.000 | n/a |
| gate-yoshi | 1 | 79.000 | 79.000 | n/a |

## Work per frame, median over 600 frame windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 6.000 | 6.000 | n/a |
| gate-cv3 | 1 | 6.500 | 6.500 | n/a |
| gate-gba-ref | 1 | 8.100 | 8.100 | n/a |
| gate-kirbyadv | 1 | 6.700 | 6.700 | n/a |
| gate-kss | 1 | 15.500 | 15.500 | n/a |
| gate-rockman2 | 1 | 6.500 | 6.500 | n/a |
| gate-smb3 | 1 | 6.500 | 6.500 | n/a |
| gate-smrpg | 1 | 16.700 | 16.700 | n/a |
| gate-starfox | 1 | 13.300 | 13.300 | n/a |
| gate-yoshi | 1 | 12.100 | 12.100 | n/a |

## Work per frame, worst 600 frame window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 15.400 | 15.400 | n/a |
| gate-cv3 | 1 | 8.200 | 8.200 | n/a |
| gate-gba-ref | 1 | 9.700 | 9.700 | n/a |
| gate-kirbyadv | 1 | 8.100 | 8.100 | n/a |
| gate-kss | 1 | 18.300 | 18.300 | n/a |
| gate-rockman2 | 1 | 8.400 | 8.400 | n/a |
| gate-smb3 | 1 | 7.800 | 7.800 | n/a |
| gate-smrpg | 1 | 18.200 | 18.200 | n/a |
| gate-starfox | 1 | 15.000 | 15.000 | n/a |
| gate-yoshi | 1 | 17.500 | 17.500 | n/a |

## Present period, median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 16.780 | 16.780 | n/a |
| gate-cv3 | 1 | 16.780 | 16.780 | n/a |
| gate-gba-ref | 1 | 16.790 | 16.790 | n/a |
| gate-kirbyadv | 1 | 16.780 | 16.780 | n/a |
| gate-kss | 1 | 16.790 | 16.790 | n/a |
| gate-rockman2 | 1 | 16.790 | 16.790 | n/a |
| gate-smb3 | 1 | 16.790 | 16.790 | n/a |
| gate-smrpg | 1 | 16.780 | 16.780 | n/a |
| gate-starfox | 1 | 16.790 | 16.790 | n/a |
| gate-yoshi | 1 | 16.790 | 16.790 | n/a |

## Present interval p50, median over windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 16.780 | 16.780 | n/a |
| gate-cv3 | 1 | 16.790 | 16.790 | n/a |
| gate-gba-ref | 1 | 16.790 | 16.790 | n/a |
| gate-kirbyadv | 1 | 16.780 | 16.780 | n/a |
| gate-kss | 1 | 16.780 | 16.780 | n/a |
| gate-rockman2 | 1 | 16.790 | 16.790 | n/a |
| gate-smb3 | 1 | 16.780 | 16.780 | n/a |
| gate-smrpg | 1 | 16.790 | 16.790 | n/a |
| gate-starfox | 1 | 16.790 | 16.790 | n/a |
| gate-yoshi | 1 | 16.790 | 16.790 | n/a |

## Present interval p99, worst window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 17.340 | 17.340 | n/a |
| gate-cv3 | 1 | 17.350 | 17.350 | n/a |
| gate-gba-ref | 1 | 18.280 | 18.280 | n/a |
| gate-kirbyadv | 1 | 17.410 | 17.410 | n/a |
| gate-kss | 1 | 17.990 | 17.990 | n/a |
| gate-rockman2 | 1 | 17.360 | 17.360 | n/a |
| gate-smb3 | 1 | 17.350 | 17.350 | n/a |
| gate-smrpg | 1 | 19.240 | 19.240 | n/a |
| gate-starfox | 1 | 18.140 | 18.140 | n/a |
| gate-yoshi | 1 | 18.440 | 18.440 | n/a |

## Present interval, longest (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 72.710 | 72.710 | n/a |
| gate-cv3 | 1 | 46.930 | 46.930 | n/a |
| gate-gba-ref | 1 | 24.160 | 24.160 | n/a |
| gate-kirbyadv | 1 | 63.500 | 63.500 | n/a |
| gate-kss | 1 | 30.900 | 30.900 | n/a |
| gate-rockman2 | 1 | 51.190 | 51.190 | n/a |
| gate-smb3 | 1 | 22.480 | 22.480 | n/a |
| gate-smrpg | 1 | 30.930 | 30.930 | n/a |
| gate-starfox | 1 | 19.540 | 19.540 | n/a |
| gate-yoshi | 1 | 29.600 | 29.600 | n/a |

## Crash lines

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gate-battletoads | 1 | 0.000 | 0.000 | n/a |
| gate-cv3 | 1 | 0.000 | 0.000 | n/a |
| gate-gba-ref | 1 | 0.000 | 0.000 | n/a |
| gate-kirbyadv | 1 | 0.000 | 0.000 | n/a |
| gate-kss | 1 | 0.000 | 0.000 | n/a |
| gate-rockman2 | 1 | 0.000 | 0.000 | n/a |
| gate-smb3 | 1 | 0.000 | 0.000 | n/a |
| gate-smrpg | 1 | 0.000 | 0.000 | n/a |
| gate-starfox | 1 | 0.000 | 0.000 | n/a |
| gate-yoshi | 1 | 0.000 | 0.000 | n/a |

## Sessions that ended cleanly (summary line present)

| Pair | Runs | Clean |
|---|---|---|
| gate-battletoads | 1 | 1 |
| gate-cv3 | 1 | 1 |
| gate-gba-ref | 1 | 1 |
| gate-kirbyadv | 1 | 1 |
| gate-kss | 1 | 1 |
| gate-rockman2 | 1 | 1 |
| gate-smb3 | 1 | 1 |
| gate-smrpg | 1 | 1 |
| gate-starfox | 1 | 1 |
| gate-yoshi | 1 | 1 |
