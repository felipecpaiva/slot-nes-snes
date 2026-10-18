# Performance evaluation, automated play on the device

    date 2026-10-18
    device Linux 4.9.170 aarch64
    governor performance
    power Full 
    input nodes: A /dev/input/event1, B /dev/input/event1, START /dev/input/event1, MENU /dev/input/event1, hat /dev/input/event1
    play 1 minutes per run, 1 runs per pair

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
| md-pal | 1 | 1735.400 | 1735.400 | n/a |
| nes-pal | 1 | 1395.300 | 1395.300 | n/a |
| ps1-pal | 1 | 1773.500 | 1773.500 | n/a |
| rb-gba-mgba | 1 | 1444.300 | 1444.300 | n/a |
| rb-md-gpgx | 1 | 1216.900 | 1216.900 | n/a |
| rb-md2 | 1 | 1871.800 | 1871.800 | n/a |
| rb-nes-fceumm | 1 | 1436.400 | 1436.400 | n/a |
| rb-nes-pal | 1 | 1294.700 | 1294.700 | n/a |
| rb-ps1-pcsx | 1 | 1680.200 | 1680.200 | n/a |
| rb-snes-snes9x | 1 | 1345.800 | 1345.800 | n/a |
| sms-pal | 1 | 1271.100 | 1271.100 | n/a |
| sms-region-auto | 1 | 1711.600 | 1711.600 | n/a |
| sms-region-europe | 1 | 1205.900 | 1205.900 | n/a |

## Insert or resume to first game frame (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 1227.700 | 1227.700 | n/a |
| nes-pal | 1 | 738.200 | 738.200 | n/a |
| ps1-pal | 1 | 1378.900 | 1378.900 | n/a |
| rb-gba-mgba | 1 | 1361.600 | 1361.600 | n/a |
| rb-md-gpgx | 1 | n/a | | |
| rb-md2 | 1 | 1359.200 | 1359.200 | n/a |
| rb-nes-fceumm | 1 | 821.400 | 821.400 | n/a |
| rb-nes-pal | 1 | 658.200 | 658.200 | n/a |
| rb-ps1-pcsx | 1 | 1515.600 | 1515.600 | n/a |
| rb-snes-snes9x | 1 | 801.200 | 801.200 | n/a |
| sms-pal | 1 | 639.700 | 639.700 | n/a |
| sms-region-auto | 1 | 1106.600 | 1106.600 | n/a |
| sms-region-europe | 1 | 530.100 | 530.100 | n/a |

## Audio starved samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 0.000 | 0.000 | n/a |
| nes-pal | 1 | 0.000 | 0.000 | n/a |
| ps1-pal | 1 | 0.000 | 0.000 | n/a |
| rb-gba-mgba | 1 | 0.000 | 0.000 | n/a |
| rb-md-gpgx | 1 | n/a | | |
| rb-md2 | 1 | 0.000 | 0.000 | n/a |
| rb-nes-fceumm | 1 | 0.000 | 0.000 | n/a |
| rb-nes-pal | 1 | 0.000 | 0.000 | n/a |
| rb-ps1-pcsx | 1 | 0.000 | 0.000 | n/a |
| rb-snes-snes9x | 1 | 0.000 | 0.000 | n/a |
| sms-pal | 1 | 0.000 | 0.000 | n/a |
| sms-region-auto | 1 | 0.000 | 0.000 | n/a |
| sms-region-europe | 1 | 0.000 | 0.000 | n/a |

## Audio dropped samples, session total

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 0.000 | 0.000 | n/a |
| nes-pal | 1 | 0.000 | 0.000 | n/a |
| ps1-pal | 1 | 0.000 | 0.000 | n/a |
| rb-gba-mgba | 1 | 0.000 | 0.000 | n/a |
| rb-md-gpgx | 1 | n/a | | |
| rb-md2 | 1 | 0.000 | 0.000 | n/a |
| rb-nes-fceumm | 1 | 0.000 | 0.000 | n/a |
| rb-nes-pal | 1 | 0.000 | 0.000 | n/a |
| rb-ps1-pcsx | 1 | 0.000 | 0.000 | n/a |
| rb-snes-snes9x | 1 | 0.000 | 0.000 | n/a |
| sms-pal | 1 | 0.000 | 0.000 | n/a |
| sms-region-auto | 1 | 0.000 | 0.000 | n/a |
| sms-region-europe | 1 | 0.000 | 0.000 | n/a |

## Audio starved, trace maximum (per 300 frames, cumulative)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 0.000 | 0.000 | n/a |
| nes-pal | 1 | 0.000 | 0.000 | n/a |
| ps1-pal | 1 | 0.000 | 0.000 | n/a |
| rb-gba-mgba | 1 | 0.000 | 0.000 | n/a |
| rb-md-gpgx | 1 | n/a | | |
| rb-md2 | 1 | 0.000 | 0.000 | n/a |
| rb-nes-fceumm | 1 | 0.000 | 0.000 | n/a |
| rb-nes-pal | 1 | 0.000 | 0.000 | n/a |
| rb-ps1-pcsx | 1 | 0.000 | 0.000 | n/a |
| rb-snes-snes9x | 1 | 0.000 | 0.000 | n/a |
| sms-pal | 1 | 0.000 | 0.000 | n/a |
| sms-region-auto | 1 | 0.000 | 0.000 | n/a |
| sms-region-europe | 1 | 0.000 | 0.000 | n/a |

## Audio dropped, trace maximum

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 0.000 | 0.000 | n/a |
| nes-pal | 1 | 0.000 | 0.000 | n/a |
| ps1-pal | 1 | 0.000 | 0.000 | n/a |
| rb-gba-mgba | 1 | 0.000 | 0.000 | n/a |
| rb-md-gpgx | 1 | n/a | | |
| rb-md2 | 1 | 0.000 | 0.000 | n/a |
| rb-nes-fceumm | 1 | 0.000 | 0.000 | n/a |
| rb-nes-pal | 1 | 0.000 | 0.000 | n/a |
| rb-ps1-pcsx | 1 | 0.000 | 0.000 | n/a |
| rb-snes-snes9x | 1 | 0.000 | 0.000 | n/a |
| sms-pal | 1 | 0.000 | 0.000 | n/a |
| sms-region-auto | 1 | 0.000 | 0.000 | n/a |
| sms-region-europe | 1 | 0.000 | 0.000 | n/a |

## Input latency median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 17.300 | 17.300 | n/a |
| nes-pal | 1 | 18.400 | 18.400 | n/a |
| ps1-pal | 1 | 23.100 | 23.100 | n/a |
| rb-gba-mgba | 1 | 17.900 | 17.900 | n/a |
| rb-md-gpgx | 1 | n/a | | |
| rb-md2 | 1 | 17.700 | 17.700 | n/a |
| rb-nes-fceumm | 1 | 15.300 | 15.300 | n/a |
| rb-nes-pal | 1 | 17.500 | 17.500 | n/a |
| rb-ps1-pcsx | 1 | 22.100 | 22.100 | n/a |
| rb-snes-snes9x | 1 | 21.000 | 21.000 | n/a |
| sms-pal | 1 | 17.600 | 17.600 | n/a |
| sms-region-auto | 1 | 16.600 | 16.600 | n/a |
| sms-region-europe | 1 | 17.000 | 17.000 | n/a |

## Input latency p99 (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 40.100 | 40.100 | n/a |
| nes-pal | 1 | 40.800 | 40.800 | n/a |
| ps1-pal | 1 | 45.000 | 45.000 | n/a |
| rb-gba-mgba | 1 | 26.800 | 26.800 | n/a |
| rb-md-gpgx | 1 | n/a | | |
| rb-md2 | 1 | 28.300 | 28.300 | n/a |
| rb-nes-fceumm | 1 | 23.300 | 23.300 | n/a |
| rb-nes-pal | 1 | 39.200 | 39.200 | n/a |
| rb-ps1-pcsx | 1 | 33.500 | 33.500 | n/a |
| rb-snes-snes9x | 1 | 29.800 | 29.800 | n/a |
| sms-pal | 1 | 39.600 | 39.600 | n/a |
| sms-region-auto | 1 | 24.000 | 24.000 | n/a |
| sms-region-europe | 1 | 39.200 | 39.200 | n/a |

## Input latency max (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 42.800 | 42.800 | n/a |
| nes-pal | 1 | 41.500 | 41.500 | n/a |
| ps1-pal | 1 | 48.500 | 48.500 | n/a |
| rb-gba-mgba | 1 | 27.800 | 27.800 | n/a |
| rb-md-gpgx | 1 | n/a | | |
| rb-md2 | 1 | 29.300 | 29.300 | n/a |
| rb-nes-fceumm | 1 | 23.500 | 23.500 | n/a |
| rb-nes-pal | 1 | 40.200 | 40.200 | n/a |
| rb-ps1-pcsx | 1 | 35.200 | 35.200 | n/a |
| rb-snes-snes9x | 1 | 30.200 | 30.200 | n/a |
| sms-pal | 1 | 39.700 | 39.700 | n/a |
| sms-region-auto | 1 | 24.600 | 24.600 | n/a |
| sms-region-europe | 1 | 40.400 | 40.400 | n/a |

## Presents that missed a latch (total over the session)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 2.000 | 2.000 | n/a |
| nes-pal | 1 | 1.000 | 1.000 | n/a |
| ps1-pal | 1 | 1.000 | 1.000 | n/a |
| rb-gba-mgba | 1 | 1.000 | 1.000 | n/a |
| rb-md-gpgx | 1 | 0.000 | 0.000 | n/a |
| rb-md2 | 1 | 2.000 | 2.000 | n/a |
| rb-nes-fceumm | 1 | 1.000 | 1.000 | n/a |
| rb-nes-pal | 1 | 1.000 | 1.000 | n/a |
| rb-ps1-pcsx | 1 | 3.000 | 3.000 | n/a |
| rb-snes-snes9x | 1 | 1.000 | 1.000 | n/a |
| sms-pal | 1 | 1.000 | 1.000 | n/a |
| sms-region-auto | 1 | 1.000 | 1.000 | n/a |
| sms-region-europe | 1 | 0.000 | 0.000 | n/a |

## Presents drawn early (total)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 391.000 | 391.000 | n/a |
| nes-pal | 1 | 79.000 | 79.000 | n/a |
| ps1-pal | 1 | 1703.000 | 1703.000 | n/a |
| rb-gba-mgba | 1 | 210.000 | 210.000 | n/a |
| rb-md-gpgx | 1 | 29.000 | 29.000 | n/a |
| rb-md2 | 1 | 57.000 | 57.000 | n/a |
| rb-nes-fceumm | 1 | 29.000 | 29.000 | n/a |
| rb-nes-pal | 1 | 59.000 | 59.000 | n/a |
| rb-ps1-pcsx | 1 | 699.000 | 699.000 | n/a |
| rb-snes-snes9x | 1 | 10.000 | 10.000 | n/a |
| sms-pal | 1 | 27.000 | 27.000 | n/a |
| sms-region-auto | 1 | 32.000 | 32.000 | n/a |
| sms-region-europe | 1 | 32.000 | 32.000 | n/a |

## Work per frame, median over 600 frame windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 8.100 | 8.100 | n/a |
| nes-pal | 1 | 7.100 | 7.100 | n/a |
| ps1-pal | 1 | 10.400 | 10.400 | n/a |
| rb-gba-mgba | 1 | 8.300 | 8.300 | n/a |
| rb-md-gpgx | 1 | 3.000 | 3.000 | n/a |
| rb-md2 | 1 | 8.900 | 8.900 | n/a |
| rb-nes-fceumm | 1 | 8.100 | 8.100 | n/a |
| rb-nes-pal | 1 | 8.000 | 8.000 | n/a |
| rb-ps1-pcsx | 1 | 10.300 | 10.300 | n/a |
| rb-snes-snes9x | 1 | 12.100 | 12.100 | n/a |
| sms-pal | 1 | 5.800 | 5.800 | n/a |
| sms-region-auto | 1 | 6.100 | 6.100 | n/a |
| sms-region-europe | 1 | 6.000 | 6.000 | n/a |

## Work per frame, worst 600 frame window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 9.900 | 9.900 | n/a |
| nes-pal | 1 | 9.100 | 9.100 | n/a |
| ps1-pal | 1 | 15.700 | 15.700 | n/a |
| rb-gba-mgba | 1 | 14.000 | 14.000 | n/a |
| rb-md-gpgx | 1 | 3.400 | 3.400 | n/a |
| rb-md2 | 1 | 10.900 | 10.900 | n/a |
| rb-nes-fceumm | 1 | 8.900 | 8.900 | n/a |
| rb-nes-pal | 1 | 8.800 | 8.800 | n/a |
| rb-ps1-pcsx | 1 | 14.300 | 14.300 | n/a |
| rb-snes-snes9x | 1 | 15.500 | 15.500 | n/a |
| sms-pal | 1 | 7.400 | 7.400 | n/a |
| sms-region-auto | 1 | 7.800 | 7.800 | n/a |
| sms-region-europe | 1 | 7.000 | 7.000 | n/a |

## Present period, median (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 16.780 | 16.780 | n/a |
| nes-pal | 1 | 16.790 | 16.790 | n/a |
| ps1-pal | 1 | 16.780 | 16.780 | n/a |
| rb-gba-mgba | 1 | 16.780 | 16.780 | n/a |
| rb-md-gpgx | 1 | 16.780 | 16.780 | n/a |
| rb-md2 | 1 | 16.790 | 16.790 | n/a |
| rb-nes-fceumm | 1 | 16.770 | 16.770 | n/a |
| rb-nes-pal | 1 | 16.780 | 16.780 | n/a |
| rb-ps1-pcsx | 1 | 16.790 | 16.790 | n/a |
| rb-snes-snes9x | 1 | 16.780 | 16.780 | n/a |
| sms-pal | 1 | 16.780 | 16.780 | n/a |
| sms-region-auto | 1 | 16.780 | 16.780 | n/a |
| sms-region-europe | 1 | 16.780 | 16.780 | n/a |

## Present interval p50, median over windows (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 16.780 | 16.780 | n/a |
| nes-pal | 1 | 16.780 | 16.780 | n/a |
| ps1-pal | 1 | 16.790 | 16.790 | n/a |
| rb-gba-mgba | 1 | 16.780 | 16.780 | n/a |
| rb-md-gpgx | 1 | 16.790 | 16.790 | n/a |
| rb-md2 | 1 | 16.790 | 16.790 | n/a |
| rb-nes-fceumm | 1 | 16.780 | 16.780 | n/a |
| rb-nes-pal | 1 | 16.780 | 16.780 | n/a |
| rb-ps1-pcsx | 1 | 16.790 | 16.790 | n/a |
| rb-snes-snes9x | 1 | 16.780 | 16.780 | n/a |
| sms-pal | 1 | 16.780 | 16.780 | n/a |
| sms-region-auto | 1 | 16.790 | 16.790 | n/a |
| sms-region-europe | 1 | 16.790 | 16.790 | n/a |

## Present interval p99, worst window (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 17.420 | 17.420 | n/a |
| nes-pal | 1 | 17.390 | 17.390 | n/a |
| ps1-pal | 1 | 18.860 | 18.860 | n/a |
| rb-gba-mgba | 1 | 18.120 | 18.120 | n/a |
| rb-md-gpgx | 1 | 17.070 | 17.070 | n/a |
| rb-md2 | 1 | 17.520 | 17.520 | n/a |
| rb-nes-fceumm | 1 | 17.390 | 17.390 | n/a |
| rb-nes-pal | 1 | 17.400 | 17.400 | n/a |
| rb-ps1-pcsx | 1 | 17.820 | 17.820 | n/a |
| rb-snes-snes9x | 1 | 17.350 | 17.350 | n/a |
| sms-pal | 1 | 17.320 | 17.320 | n/a |
| sms-region-auto | 1 | 17.470 | 17.470 | n/a |
| sms-region-europe | 1 | 17.340 | 17.340 | n/a |

## Present interval, longest (ms)

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 167.840 | 167.840 | n/a |
| nes-pal | 1 | 41.450 | 41.450 | n/a |
| ps1-pal | 1 | 284.570 | 284.570 | n/a |
| rb-gba-mgba | 1 | 190.420 | 190.420 | n/a |
| rb-md-gpgx | 1 | 17.670 | 17.670 | n/a |
| rb-md2 | 1 | 27.690 | 27.690 | n/a |
| rb-nes-fceumm | 1 | 60.210 | 60.210 | n/a |
| rb-nes-pal | 1 | 36.590 | 36.590 | n/a |
| rb-ps1-pcsx | 1 | 33.350 | 33.350 | n/a |
| rb-snes-snes9x | 1 | 28.230 | 28.230 | n/a |
| sms-pal | 1 | 58.270 | 58.270 | n/a |
| sms-region-auto | 1 | 81.380 | 81.380 | n/a |
| sms-region-europe | 1 | 19.570 | 19.570 | n/a |

## Crash lines

| Pair | Runs | Median | Worst | vs GBA mGBA, same weight |
|---|---|---|---|---|
| md-pal | 1 | 0.000 | 0.000 | n/a |
| nes-pal | 1 | 0.000 | 0.000 | n/a |
| ps1-pal | 1 | 0.000 | 0.000 | n/a |
| rb-gba-mgba | 1 | 0.000 | 0.000 | n/a |
| rb-md-gpgx | 1 | 0.000 | 0.000 | n/a |
| rb-md2 | 1 | 0.000 | 0.000 | n/a |
| rb-nes-fceumm | 1 | 0.000 | 0.000 | n/a |
| rb-nes-pal | 1 | 0.000 | 0.000 | n/a |
| rb-ps1-pcsx | 1 | 0.000 | 0.000 | n/a |
| rb-snes-snes9x | 1 | 0.000 | 0.000 | n/a |
| sms-pal | 1 | 0.000 | 0.000 | n/a |
| sms-region-auto | 1 | 0.000 | 0.000 | n/a |
| sms-region-europe | 1 | 0.000 | 0.000 | n/a |

## Sessions that ended cleanly (summary line present)

| Pair | Runs | Clean |
|---|---|---|
| md-pal | 1 | 1 |
| nes-pal | 1 | 1 |
| ps1-pal | 1 | 1 |
| rb-gba-mgba | 1 | 1 |
| rb-md-gpgx | 1 | 0 |
| rb-md2 | 1 | 1 |
| rb-nes-fceumm | 1 | 1 |
| rb-nes-pal | 1 | 1 |
| rb-ps1-pcsx | 1 | 1 |
| rb-snes-snes9x | 1 | 1 |
| sms-pal | 1 | 1 |
| sms-region-auto | 1 | 1 |
| sms-region-europe | 1 | 1 |
