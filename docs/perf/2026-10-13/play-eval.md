# Performance evaluation, automated play on the device

    date 2026-10-13
    device Linux 4.9.170 aarch64
    governor performance
    power Full 
    input nodes: A /dev/input/event1, B /dev/input/event1, START /dev/input/event1, MENU /dev/input/event1, hat /dev/input/event1
    play 3 minutes per run, 1 runs per pair

Each cell is median / worst over runs. Every run plays the same script on every core: START x3, then right held with A every 700 ms and B every 2.3 s, then eject. Latency is input to screen swap. Slot logs no per-frame wall time: the pace lines (work per frame, missed latches) are the nearest frame-time figure, and only exist with the latency trace on. Starved and dropped count samples, not events. A run without a session summary line did not end cleanly.

## GBA mGBA baseline, heavy and light side by side

| Metric | gba-mgba-heavy | gba-mgba-light |
|---|---|---|
| Boot to first frame (ms) | 554 / 554 | 549 / 549 |
| Insert or resume to first game frame (ms) | 206 / 206 | 1.02e+03 / 1.02e+03 |
| Audio starved samples, session total | 5.12e+03 / 5.12e+03 | 6.14e+03 / 6.14e+03 |
| Audio dropped samples, session total | 2.27e+04 / 2.27e+04 | 2.3e+04 / 2.3e+04 |
| Audio starved, trace maximum (per 300 frames, cumulative) | 5.12e+03 / 5.12e+03 | 6.14e+03 / 6.14e+03 |
| Audio dropped, trace maximum | 2.27e+04 / 2.27e+04 | 2.3e+04 / 2.3e+04 |
| Input latency median (ms) | 17.4 / 17.4 | 18.9 / 18.9 |
| Input latency p99 (ms) | 27.5 / 27.5 | 27.4 / 27.4 |
| Input latency max (ms) | 28.3 / 28.3 | 30.8 / 30.8 |
| Presents that missed a latch (total over the session) | 1 / 1 | 1 / 1 |
| Presents drawn early (total) | 113 / 113 | 104 / 104 |
| Work per frame, median over 600 frame windows (ms) | 7.6 / 7.6 | 9.4 / 9.4 |
| Work per frame, worst 600 frame window (ms) | 9.8 / 9.8 | 11.4 / 11.4 |
| Present period, median (ms) | 16.8 / 16.8 | 16.8 / 16.8 |
| Present interval p50, median over windows (ms) | n/a | n/a |
| Present interval p99, worst window (ms) | n/a | n/a |
| Present interval, longest (ms) | n/a | n/a |
| Crash lines | 0 / 0 | 0 / 0 |

## Boot to first frame (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 554.400 | 554.400 | n/a |
| gba-mgba-light | 1 | 549.000 | 549.000 | n/a |
| gba-gpsp-heavy | 1 | 577.300 | 577.300 | +4.1% |
| gba-gpsp-light | 1 | 534.700 | 534.700 | -2.6% |
| gbc-mgba-card | 1 | 589.900 | 589.900 | +6.4% |
| nes-fceumm-heavy | 1 | 764.800 | 764.800 | +38.0% |
| nes-fceumm-light | 1 | 573.000 | 573.000 | +4.4% |
| nes-nestopia-heavy | 1 | 869.600 | 869.600 | +56.9% |
| nes-nestopia-light | 1 | 588.600 | 588.600 | +7.2% |
| snes-snes9x-heavy | 1 | 731.400 | 731.400 | +31.9% |
| snes-snes9x-light | 1 | 588.400 | 588.400 | +7.2% |
| snes-snes9x2005_plus-heavy | 1 | 611.600 | 611.600 | +10.3% |
| snes-snes9x2005_plus-light | 1 | 560.900 | 560.900 | +2.2% |

## Insert or resume to first game frame (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 206.200 | 206.200 | n/a |
| gba-mgba-light | 1 | 1024.200 | 1024.200 | n/a |
| gba-gpsp-heavy | 1 | 252.500 | 252.500 | +22.5% |
| gba-gpsp-light | 1 | 295.000 | 295.000 | -71.2% |
| gbc-mgba-card | 1 | 131.300 | 131.300 | -36.3% |
| nes-fceumm-heavy | 1 | 384.900 | 384.900 | +86.7% |
| nes-fceumm-light | 1 | 153.700 | 153.700 | -85.0% |
| nes-nestopia-heavy | 1 | 786.800 | 786.800 | +281.6% |
| nes-nestopia-light | 1 | 305.700 | 305.700 | -70.2% |
| snes-snes9x-heavy | 1 | 453.400 | 453.400 | +119.9% |
| snes-snes9x-light | 1 | 143.900 | 143.900 | -86.0% |
| snes-snes9x2005_plus-heavy | 1 | 131.200 | 131.200 | -36.4% |
| snes-snes9x2005_plus-light | 1 | 152.900 | 152.900 | -85.1% |

## Audio starved samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 5120.000 | 5120.000 | n/a |
| gba-mgba-light | 1 | 6144.000 | 6144.000 | n/a |
| gba-gpsp-heavy | 1 | 4096.000 | 4096.000 | -20.0% |
| gba-gpsp-light | 1 | 5120.000 | 5120.000 | -16.7% |
| gbc-mgba-card | 1 | 4096.000 | 4096.000 | -20.0% |
| nes-fceumm-heavy | 1 | 6202.000 | 6202.000 | +21.1% |
| nes-fceumm-light | 1 | 1024.000 | 1024.000 | -83.3% |
| nes-nestopia-heavy | 1 | 4096.000 | 4096.000 | -20.0% |
| nes-nestopia-light | 1 | 4096.000 | 4096.000 | -33.3% |
| snes-snes9x-heavy | 1 | 5120.000 | 5120.000 | +0.0% |
| snes-snes9x-light | 1 | 3072.000 | 3072.000 | -50.0% |
| snes-snes9x2005_plus-heavy | 1 | 5120.000 | 5120.000 | +0.0% |
| snes-snes9x2005_plus-light | 1 | 3072.000 | 3072.000 | -50.0% |

## Audio dropped samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 22654.000 | 22654.000 | n/a |
| gba-mgba-light | 1 | 23000.000 | 23000.000 | n/a |
| gba-gpsp-heavy | 1 | 20800.000 | 20800.000 | -8.2% |
| gba-gpsp-light | 1 | 20470.000 | 20470.000 | -11.0% |
| gbc-mgba-card | 1 | 0.000 | 0.000 | -100.0% |
| nes-fceumm-heavy | 1 | 0.000 | 0.000 | -100.0% |
| nes-fceumm-light | 1 | 34304.000 | 34304.000 | +49.1% |
| nes-nestopia-heavy | 1 | 0.000 | 0.000 | -100.0% |
| nes-nestopia-light | 1 | 34348.000 | 34348.000 | +49.3% |
| snes-snes9x-heavy | 1 | 24538.000 | 24538.000 | +8.3% |
| snes-snes9x-light | 1 | 0.000 | 0.000 | -100.0% |
| snes-snes9x2005_plus-heavy | 1 | 23362.000 | 23362.000 | +3.1% |
| snes-snes9x2005_plus-light | 1 | 0.000 | 0.000 | -100.0% |

## Audio starved, trace maximum (per 300 frames, cumulative)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 5120.000 | 5120.000 | n/a |
| gba-mgba-light | 1 | 6144.000 | 6144.000 | n/a |
| gba-gpsp-heavy | 1 | 4096.000 | 4096.000 | -20.0% |
| gba-gpsp-light | 1 | 5120.000 | 5120.000 | -16.7% |
| gbc-mgba-card | 1 | 4096.000 | 4096.000 | -20.0% |
| nes-fceumm-heavy | 1 | 6202.000 | 6202.000 | +21.1% |
| nes-fceumm-light | 1 | 1024.000 | 1024.000 | -83.3% |
| nes-nestopia-heavy | 1 | 4096.000 | 4096.000 | -20.0% |
| nes-nestopia-light | 1 | 4096.000 | 4096.000 | -33.3% |
| snes-snes9x-heavy | 1 | 5120.000 | 5120.000 | +0.0% |
| snes-snes9x-light | 1 | 3072.000 | 3072.000 | -50.0% |
| snes-snes9x2005_plus-heavy | 1 | 5120.000 | 5120.000 | +0.0% |
| snes-snes9x2005_plus-light | 1 | 3072.000 | 3072.000 | -50.0% |

## Audio dropped, trace maximum

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 22654.000 | 22654.000 | n/a |
| gba-mgba-light | 1 | 23000.000 | 23000.000 | n/a |
| gba-gpsp-heavy | 1 | 20800.000 | 20800.000 | -8.2% |
| gba-gpsp-light | 1 | 20470.000 | 20470.000 | -11.0% |
| gbc-mgba-card | 1 | 0.000 | 0.000 | -100.0% |
| nes-fceumm-heavy | 1 | 0.000 | 0.000 | -100.0% |
| nes-fceumm-light | 1 | 34304.000 | 34304.000 | +49.1% |
| nes-nestopia-heavy | 1 | 0.000 | 0.000 | -100.0% |
| nes-nestopia-light | 1 | 34348.000 | 34348.000 | +49.3% |
| snes-snes9x-heavy | 1 | 24538.000 | 24538.000 | +8.3% |
| snes-snes9x-light | 1 | 0.000 | 0.000 | -100.0% |
| snes-snes9x2005_plus-heavy | 1 | 23362.000 | 23362.000 | +3.1% |
| snes-snes9x2005_plus-light | 1 | 0.000 | 0.000 | -100.0% |

## Input latency median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 17.400 | 17.400 | n/a |
| gba-mgba-light | 1 | 18.900 | 18.900 | n/a |
| gba-gpsp-heavy | 1 | 15.400 | 15.400 | -11.5% |
| gba-gpsp-light | 1 | 15.300 | 15.300 | -19.0% |
| gbc-mgba-card | 1 | 15.700 | 15.700 | -9.8% |
| nes-fceumm-heavy | 1 | 15.700 | 15.700 | -9.8% |
| nes-fceumm-light | 1 | 20.500 | 20.500 | +8.5% |
| nes-nestopia-heavy | 1 | 17.900 | 17.900 | +2.9% |
| nes-nestopia-light | 1 | 20.300 | 20.300 | +7.4% |
| snes-snes9x-heavy | 1 | 22.900 | 22.900 | +31.6% |
| snes-snes9x-light | 1 | 18.800 | 18.800 | -0.5% |
| snes-snes9x2005_plus-heavy | 1 | 18.800 | 18.800 | +8.0% |
| snes-snes9x2005_plus-light | 1 | 17.700 | 17.700 | -6.3% |

## Input latency p99 (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 27.500 | 27.500 | n/a |
| gba-mgba-light | 1 | 27.400 | 27.400 | n/a |
| gba-gpsp-heavy | 1 | 23.900 | 23.900 | -13.1% |
| gba-gpsp-light | 1 | 24.600 | 24.600 | -10.2% |
| gbc-mgba-card | 1 | 23.800 | 23.800 | -13.5% |
| nes-fceumm-heavy | 1 | 24.100 | 24.100 | -12.4% |
| nes-fceumm-light | 1 | 48.500 | 48.500 | +77.0% |
| nes-nestopia-heavy | 1 | 27.200 | 27.200 | -1.1% |
| nes-nestopia-light | 1 | 47.800 | 47.800 | +74.5% |
| snes-snes9x-heavy | 1 | 32.900 | 32.900 | +19.6% |
| snes-snes9x-light | 1 | 30.300 | 30.300 | +10.6% |
| snes-snes9x2005_plus-heavy | 1 | 29.600 | 29.600 | +7.6% |
| snes-snes9x2005_plus-light | 1 | 26.900 | 26.900 | -1.8% |

## Input latency max (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 28.300 | 28.300 | n/a |
| gba-mgba-light | 1 | 30.800 | 30.800 | n/a |
| gba-gpsp-heavy | 1 | 24.700 | 24.700 | -12.7% |
| gba-gpsp-light | 1 | 26.300 | 26.300 | -14.6% |
| gbc-mgba-card | 1 | 24.400 | 24.400 | -13.8% |
| nes-fceumm-heavy | 1 | 24.900 | 24.900 | -12.0% |
| nes-fceumm-light | 1 | 49.000 | 49.000 | +59.1% |
| nes-nestopia-heavy | 1 | 31.900 | 31.900 | +12.7% |
| nes-nestopia-light | 1 | 49.500 | 49.500 | +60.7% |
| snes-snes9x-heavy | 1 | 43.000 | 43.000 | +51.9% |
| snes-snes9x-light | 1 | 31.000 | 31.000 | +0.6% |
| snes-snes9x2005_plus-heavy | 1 | 33.400 | 33.400 | +18.0% |
| snes-snes9x2005_plus-light | 1 | 28.600 | 28.600 | -7.1% |

## Presents that missed a latch (total over the session)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 1.000 | 1.000 | n/a |
| gba-mgba-light | 1 | 1.000 | 1.000 | n/a |
| gba-gpsp-heavy | 1 | 1.000 | 1.000 | +0.0% |
| gba-gpsp-light | 1 | 1.000 | 1.000 | +0.0% |
| gbc-mgba-card | 1 | 2.000 | 2.000 | +100.0% |
| nes-fceumm-heavy | 1 | 0.000 | 0.000 | -100.0% |
| nes-fceumm-light | 1 | 1.000 | 1.000 | +0.0% |
| nes-nestopia-heavy | 1 | 0.000 | 0.000 | -100.0% |
| nes-nestopia-light | 1 | 1.000 | 1.000 | +0.0% |
| snes-snes9x-heavy | 1 | 0.000 | 0.000 | -100.0% |
| snes-snes9x-light | 1 | 1.000 | 1.000 | +0.0% |
| snes-snes9x2005_plus-heavy | 1 | 0.000 | 0.000 | -100.0% |
| snes-snes9x2005_plus-light | 1 | 1.000 | 1.000 | +0.0% |

## Presents drawn early (total)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 113.000 | 113.000 | n/a |
| gba-mgba-light | 1 | 104.000 | 104.000 | n/a |
| gba-gpsp-heavy | 1 | 125.000 | 125.000 | +10.6% |
| gba-gpsp-light | 1 | 93.000 | 93.000 | -10.6% |
| gbc-mgba-card | 1 | 62.000 | 62.000 | -45.1% |
| nes-fceumm-heavy | 1 | 21.000 | 21.000 | -81.4% |
| nes-fceumm-light | 1 | 1559.000 | 1559.000 | +1399.0% |
| nes-nestopia-heavy | 1 | 49.000 | 49.000 | -56.6% |
| nes-nestopia-light | 1 | 1432.000 | 1432.000 | +1276.9% |
| snes-snes9x-heavy | 1 | 84.000 | 84.000 | -25.7% |
| snes-snes9x-light | 1 | 26.000 | 26.000 | -75.0% |
| snes-snes9x2005_plus-heavy | 1 | 407.000 | 407.000 | +260.2% |
| snes-snes9x2005_plus-light | 1 | 54.000 | 54.000 | -48.1% |

## Work per frame, median over 600 frame windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 7.600 | 7.600 | n/a |
| gba-mgba-light | 1 | 9.400 | 9.400 | n/a |
| gba-gpsp-heavy | 1 | 5.400 | 5.400 | -28.9% |
| gba-gpsp-light | 1 | 5.400 | 5.400 | -42.6% |
| gbc-mgba-card | 1 | 5.200 | 5.200 | -31.6% |
| nes-fceumm-heavy | 1 | 6.400 | 6.400 | -15.8% |
| nes-fceumm-light | 1 | 8.000 | 8.000 | -14.9% |
| nes-nestopia-heavy | 1 | 8.800 | 8.800 | +15.8% |
| nes-nestopia-light | 1 | 8.700 | 8.700 | -7.4% |
| snes-snes9x-heavy | 1 | 12.800 | 12.800 | +68.4% |
| snes-snes9x-light | 1 | 10.100 | 10.100 | +7.4% |
| snes-snes9x2005_plus-heavy | 1 | 10.500 | 10.500 | +38.2% |
| snes-snes9x2005_plus-light | 1 | 8.400 | 8.400 | -10.6% |

## Work per frame, worst 600 frame window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 9.800 | 9.800 | n/a |
| gba-mgba-light | 1 | 11.400 | 11.400 | n/a |
| gba-gpsp-heavy | 1 | 7.400 | 7.400 | -24.5% |
| gba-gpsp-light | 1 | 7.600 | 7.600 | -33.3% |
| gbc-mgba-card | 1 | 5.700 | 5.700 | -41.8% |
| nes-fceumm-heavy | 1 | 7.600 | 7.600 | -22.4% |
| nes-fceumm-light | 1 | 15.800 | 15.800 | +38.6% |
| nes-nestopia-heavy | 1 | 10.600 | 10.600 | +8.2% |
| nes-nestopia-light | 1 | 15.900 | 15.900 | +39.5% |
| snes-snes9x-heavy | 1 | 15.700 | 15.700 | +60.2% |
| snes-snes9x-light | 1 | 13.400 | 13.400 | +17.5% |
| snes-snes9x2005_plus-heavy | 1 | 13.200 | 13.200 | +34.7% |
| snes-snes9x2005_plus-light | 1 | 10.400 | 10.400 | -8.8% |

## Present period, median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 16.780 | 16.780 | n/a |
| gba-mgba-light | 1 | 16.780 | 16.780 | n/a |
| gba-gpsp-heavy | 1 | 16.780 | 16.780 | +0.0% |
| gba-gpsp-light | 1 | 16.780 | 16.780 | +0.0% |
| gbc-mgba-card | 1 | 16.780 | 16.780 | +0.0% |
| nes-fceumm-heavy | 1 | 16.790 | 16.790 | +0.1% |
| nes-fceumm-light | 1 | 16.780 | 16.780 | +0.0% |
| nes-nestopia-heavy | 1 | 16.780 | 16.780 | +0.0% |
| nes-nestopia-light | 1 | 16.790 | 16.790 | +0.1% |
| snes-snes9x-heavy | 1 | 16.780 | 16.780 | +0.0% |
| snes-snes9x-light | 1 | 16.790 | 16.790 | +0.1% |
| snes-snes9x2005_plus-heavy | 1 | 16.780 | 16.780 | +0.0% |
| snes-snes9x2005_plus-light | 1 | 16.780 | 16.780 | +0.0% |

## Present interval p50, median over windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | n/a | | |
| gba-mgba-light | 1 | n/a | | |
| gba-gpsp-heavy | 1 | n/a | | |
| gba-gpsp-light | 1 | n/a | | |
| gbc-mgba-card | 1 | n/a | | |
| nes-fceumm-heavy | 1 | n/a | | |
| nes-fceumm-light | 1 | n/a | | |
| nes-nestopia-heavy | 1 | n/a | | |
| nes-nestopia-light | 1 | n/a | | |
| snes-snes9x-heavy | 1 | n/a | | |
| snes-snes9x-light | 1 | n/a | | |
| snes-snes9x2005_plus-heavy | 1 | n/a | | |
| snes-snes9x2005_plus-light | 1 | n/a | | |

## Present interval p99, worst window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | n/a | | |
| gba-mgba-light | 1 | n/a | | |
| gba-gpsp-heavy | 1 | n/a | | |
| gba-gpsp-light | 1 | n/a | | |
| gbc-mgba-card | 1 | n/a | | |
| nes-fceumm-heavy | 1 | n/a | | |
| nes-fceumm-light | 1 | n/a | | |
| nes-nestopia-heavy | 1 | n/a | | |
| nes-nestopia-light | 1 | n/a | | |
| snes-snes9x-heavy | 1 | n/a | | |
| snes-snes9x-light | 1 | n/a | | |
| snes-snes9x2005_plus-heavy | 1 | n/a | | |
| snes-snes9x2005_plus-light | 1 | n/a | | |

## Present interval, longest (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | n/a | | |
| gba-mgba-light | 1 | n/a | | |
| gba-gpsp-heavy | 1 | n/a | | |
| gba-gpsp-light | 1 | n/a | | |
| gbc-mgba-card | 1 | n/a | | |
| nes-fceumm-heavy | 1 | n/a | | |
| nes-fceumm-light | 1 | n/a | | |
| nes-nestopia-heavy | 1 | n/a | | |
| nes-nestopia-light | 1 | n/a | | |
| snes-snes9x-heavy | 1 | n/a | | |
| snes-snes9x-light | 1 | n/a | | |
| snes-snes9x2005_plus-heavy | 1 | n/a | | |
| snes-snes9x2005_plus-light | 1 | n/a | | |

## Crash lines

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| gba-mgba-heavy | 1 | 0.000 | 0.000 | n/a |
| gba-mgba-light | 1 | 0.000 | 0.000 | n/a |
| gba-gpsp-heavy | 1 | 0.000 | 0.000 | n/a |
| gba-gpsp-light | 1 | 0.000 | 0.000 | n/a |
| gbc-mgba-card | 1 | 0.000 | 0.000 | n/a |
| nes-fceumm-heavy | 1 | 0.000 | 0.000 | n/a |
| nes-fceumm-light | 1 | 0.000 | 0.000 | n/a |
| nes-nestopia-heavy | 1 | 0.000 | 0.000 | n/a |
| nes-nestopia-light | 1 | 0.000 | 0.000 | n/a |
| snes-snes9x-heavy | 1 | 0.000 | 0.000 | n/a |
| snes-snes9x-light | 1 | 0.000 | 0.000 | n/a |
| snes-snes9x2005_plus-heavy | 1 | 0.000 | 0.000 | n/a |
| snes-snes9x2005_plus-light | 1 | 0.000 | 0.000 | n/a |

## Sessions that ended cleanly (summary line present)

| Pair | Runs | Clean |
|---|---|---|
| gba-mgba-heavy | 1 | 1 |
| gba-mgba-light | 1 | 1 |
| gba-gpsp-heavy | 1 | 1 |
| gba-gpsp-light | 1 | 1 |
| gbc-mgba-card | 1 | 1 |
| nes-fceumm-heavy | 1 | 1 |
| nes-fceumm-light | 1 | 1 |
| nes-nestopia-heavy | 1 | 1 |
| nes-nestopia-light | 1 | 1 |
| snes-snes9x-heavy | 1 | 1 |
| snes-snes9x-light | 1 | 1 |
| snes-snes9x2005_plus-heavy | 1 | 1 |
| snes-snes9x2005_plus-light | 1 | 1 |
