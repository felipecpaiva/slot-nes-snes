# Performance evaluation, raw core_bench on the device

    date 2026-10-13
    device Linux 4.9.170 aarch64
    zone /sys/class/thermal/thermal_zone0 (cpu_thermal_zone)
    governor performance
    idle_temp_c 48.5 (first reading), run limit 58.5 (idle + 10)
    power Full 
    slot v1.6.0, VERSION ns.0
    runs 3, tries 4, cool 30s
    normal: --frames 1800 --warmup 300 --repeats 3
    serialize: --serialize --frames 300 --warmup 300
    ff: --steps 4 --frames 1800 --warmup 300 --repeats 3

Each cell is median and worst over runs. The last column is the median against gba-mgba (GBA mGBA, card cart) in the same session. Frame cost is the core plus slot copy and audio callbacks, not the GL upload.

## Frame cost, median over repeats (ms per frame, lower is better)

| Pair | Platform | Core | Median | Worst | vs gba-mgba |
|---|---|---|---|---|---|
| gba-mgba | GBA | mgba | 5.346 | 5.351 | +0.0% |
| gba-gpsp | GBA | gpsp | 2.097 | 2.098 | -60.8% |
| gba-mgba-harness | GBA | mgba | 0.794 | 0.796 | -85.1% |
| gba-gpsp-harness | GBA | gpsp | 0.924 | 0.925 | -82.7% |
| gb-mgba-card | GB | mgba | no workload (no GB cart on the card) | | |
| gbc-mgba-card | GBC | mgba | no workload (no GBC cart on the card) | | |
| gb-mgba-harness | GB | mgba | 1.150 | 1.153 | -78.5% |
| gbc-mgba-harness | GBC | mgba | 1.107 | 1.108 | -79.3% |
| nes-fceumm | NES | fceumm | 5.970 | 5.981 | +11.7% |
| nes-nestopia | NES | nestopia | 5.532 | 5.544 | +3.5% |
| snes-snes9x | SNES | snes9x | 10.326 | 10.332 | +93.2% |
| snes-snes9x2005_plus | SNES | snes9x2005_plus | 4.661 | 4.662 | -12.8% |

## Frame cost, worst repeat (ms per frame, lower is better)

| Pair | Platform | Core | Median | Worst | vs gba-mgba |
|---|---|---|---|---|---|
| gba-mgba | GBA | mgba | 5.350 | 5.371 | +0.0% |
| gba-gpsp | GBA | gpsp | 2.097 | 2.098 | -60.8% |
| gba-mgba-harness | GBA | mgba | 0.794 | 0.796 | -85.2% |
| gba-gpsp-harness | GBA | gpsp | 0.924 | 0.925 | -82.7% |
| gb-mgba-card | GB | mgba | no workload (no GB cart on the card) | | |
| gbc-mgba-card | GBC | mgba | no workload (no GBC cart on the card) | | |
| gb-mgba-harness | GB | mgba | 1.153 | 1.156 | -78.4% |
| gbc-mgba-harness | GBC | mgba | 1.107 | 1.112 | -79.3% |
| nes-fceumm | NES | fceumm | 5.971 | 5.982 | +11.6% |
| nes-nestopia | NES | nestopia | 5.538 | 5.544 | +3.5% |
| snes-snes9x | SNES | snes9x | 10.327 | 10.333 | +93.0% |
| snes-snes9x2005_plus | SNES | snes9x2005_plus | 4.662 | 4.667 | -12.9% |

## Speed headroom in normal play (x real time, higher is better)

| Pair | Platform | Core | Median | Worst | vs gba-mgba |
|---|---|---|---|---|---|
| gba-mgba | GBA | mgba | 3.117 | 3.115 | +0.0% |
| gba-gpsp | GBA | gpsp | 7.948 | 7.943 | +155.0% |
| gba-mgba-harness | GBA | mgba | 20.980 | 20.938 | +573.2% |
| gba-gpsp-harness | GBA | gpsp | 18.045 | 18.025 | +479.0% |
| gb-mgba-card | GB | mgba | no workload (no GB cart on the card) | | |
| gbc-mgba-card | GBC | mgba | no workload (no GBC cart on the card) | | |
| gb-mgba-harness | GB | mgba | 14.487 | 14.455 | +364.8% |
| gbc-mgba-harness | GBC | mgba | 15.060 | 15.037 | +383.2% |
| nes-fceumm | NES | fceumm | 2.792 | 2.787 | -10.4% |
| nes-nestopia | NES | nestopia | 3.013 | 3.007 | -3.3% |
| snes-snes9x | SNES | snes9x | 1.613 | 1.613 | -48.2% |
| snes-snes9x2005_plus | SNES | snes9x2005_plus | 3.577 | 3.575 | +14.8% |

## Fast-forward, 4 frames per present, no frameskip (ms per emulated frame, lower is better)

| Pair | Platform | Core | Median | Worst | vs gba-mgba |
|---|---|---|---|---|---|
| gba-mgba | GBA | mgba | 5.355 | 5.363 | +0.0% |
| gba-gpsp | GBA | gpsp | 2.098 | 2.100 | -60.8% |
| gba-mgba-harness | GBA | mgba | 0.795 | 0.795 | -85.2% |
| gba-gpsp-harness | GBA | gpsp | 0.924 | 0.925 | -82.7% |
| gb-mgba-card | GB | mgba | no workload (no GB cart on the card) | | |
| gbc-mgba-card | GBC | mgba | no workload (no GBC cart on the card) | | |
| gb-mgba-harness | GB | mgba | 1.150 | 1.150 | -78.5% |
| gbc-mgba-harness | GBC | mgba | 1.106 | 1.106 | -79.3% |
| nes-fceumm | NES | fceumm | 5.974 | 5.974 | +11.6% |
| nes-nestopia | NES | nestopia | 5.558 | 5.570 | +3.8% |
| snes-snes9x | SNES | snes9x | 10.319 | 10.325 | +92.7% |
| snes-snes9x2005_plus | SNES | snes9x2005_plus | 4.663 | 4.667 | -12.9% |

## Fast-forward speed reached, no frameskip (x real time, higher is better)

| Pair | Platform | Core | Median | Worst | vs gba-mgba |
|---|---|---|---|---|---|
| gba-mgba | GBA | mgba | 3.112 | 3.108 | +0.0% |
| gba-gpsp | GBA | gpsp | 7.943 | 7.935 | +155.3% |
| gba-mgba-harness | GBA | mgba | 20.960 | 20.958 | +573.6% |
| gba-gpsp-harness | GBA | gpsp | 18.038 | 18.025 | +479.7% |
| gb-mgba-card | GB | mgba | no workload (no GB cart on the card) | | |
| gbc-mgba-card | GBC | mgba | no workload (no GBC cart on the card) | | |
| gb-mgba-harness | GB | mgba | 14.495 | 14.490 | +365.8% |
| gbc-mgba-harness | GBC | mgba | 15.073 | 15.068 | +384.4% |
| nes-fceumm | NES | fceumm | 2.790 | 2.790 | -10.3% |
| nes-nestopia | NES | nestopia | 2.998 | 2.992 | -3.6% |
| snes-snes9x | SNES | snes9x | 1.615 | 1.613 | -48.1% |
| snes-snes9x2005_plus | SNES | snes9x2005_plus | 3.573 | 3.572 | +14.8% |

## Fast-forward speed reached, frameskip on, mgba and gpsp only (x real time, higher is better)

| Pair | Platform | Core | Median | Worst | vs gba-mgba |
|---|---|---|---|---|---|
| gba-mgba | GBA | mgba | 4.430 | 4.425 | +0.0% |
| gba-gpsp | GBA | gpsp | 19.970 | 19.957 | +350.8% |
| gba-mgba-harness | GBA | mgba | 42.608 | 42.590 | +861.8% |
| gba-gpsp-harness | GBA | gpsp | 58.803 | 58.795 | +1227.4% |
| gb-mgba-card | GB | mgba | no workload (no GB cart on the card) | | |
| gbc-mgba-card | GBC | mgba | no workload (no GBC cart on the card) | | |
| gb-mgba-harness | GB | mgba | 29.290 | 29.275 | +561.2% |
| gbc-mgba-harness | GBC | mgba | 31.812 | 31.773 | +618.1% |

## Rewind: frame cost while serializing every frame, median (ms)

| Pair | Platform | Core | Median | Worst | vs gba-mgba |
|---|---|---|---|---|---|
| gba-mgba | GBA | mgba | 5.074 | 5.075 | +0.0% |
| gba-gpsp | GBA | gpsp | 2.747 | 2.750 | -45.9% |
| gba-mgba-harness | GBA | mgba | 1.904 | 1.907 | -62.5% |
| gba-gpsp-harness | GBA | gpsp | 1.125 | 1.132 | -77.8% |
| gb-mgba-card | GB | mgba | no workload (no GB cart on the card) | | |
| gbc-mgba-card | GBC | mgba | no workload (no GBC cart on the card) | | |
| gb-mgba-harness | GB | mgba | 1.243 | 1.244 | -75.5% |
| gbc-mgba-harness | GBC | mgba | 1.188 | 1.189 | -76.6% |
| nes-fceumm | NES | fceumm | 6.097 | 6.109 | +20.2% |
| nes-nestopia | NES | nestopia | 5.497 | 5.498 | +8.3% |
| snes-snes9x | SNES | snes9x | 9.942 | 9.958 | +95.9% |
| snes-snes9x2005_plus | SNES | snes9x2005_plus | 4.576 | 4.585 | -9.8% |

## Rewind: serialize per frame, median (ms)

| Pair | Platform | Core | Median | Worst | vs gba-mgba |
|---|---|---|---|---|---|
| gba-mgba | GBA | mgba | 2.027 | 2.047 | +0.0% |
| gba-gpsp | GBA | gpsp | 0.398 | 0.443 | -80.4% |
| gba-mgba-harness | GBA | mgba | 4.692 | 4.699 | +131.5% |
| gba-gpsp-harness | GBA | gpsp | 0.315 | 0.323 | -84.5% |
| gb-mgba-card | GB | mgba | no workload (no GB cart on the card) | | |
| gbc-mgba-card | GBC | mgba | no workload (no GBC cart on the card) | | |
| gb-mgba-harness | GB | mgba | 0.877 | 0.898 | -56.7% |
| gbc-mgba-harness | GBC | mgba | 0.861 | 0.876 | -57.5% |
| nes-fceumm | NES | fceumm | 0.019 | 0.020 | -99.1% |
| nes-nestopia | NES | nestopia | 0.068 | 0.069 | -96.6% |
| snes-snes9x | SNES | snes9x | 1.297 | 1.326 | -36.0% |
| snes-snes9x2005_plus | SNES | snes9x2005_plus | 0.663 | 0.679 | -67.3% |

## Rewind: serialize per frame, worst (ms)

| Pair | Platform | Core | Median | Worst | vs gba-mgba |
|---|---|---|---|---|---|
| gba-mgba | GBA | mgba | 2.723 | 2.752 | +0.0% |
| gba-gpsp | GBA | gpsp | 0.838 | 0.974 | -69.2% |
| gba-mgba-harness | GBA | mgba | 5.484 | 5.509 | +101.4% |
| gba-gpsp-harness | GBA | gpsp | 0.792 | 0.819 | -70.9% |
| gb-mgba-card | GB | mgba | no workload (no GB cart on the card) | | |
| gbc-mgba-card | GBC | mgba | no workload (no GBC cart on the card) | | |
| gb-mgba-harness | GB | mgba | 1.292 | 1.450 | -52.6% |
| gbc-mgba-harness | GBC | mgba | 1.300 | 1.300 | -52.3% |
| nes-fceumm | NES | fceumm | 0.038 | 0.059 | -98.6% |
| nes-nestopia | NES | nestopia | 0.186 | 0.188 | -93.2% |
| snes-snes9x | SNES | snes9x | 1.781 | 1.868 | -34.6% |
| snes-snes9x2005_plus | SNES | snes9x2005_plus | 1.286 | 1.356 | -52.8% |

## Rewind: unserialize per frame, median (ms)

| Pair | Platform | Core | Median | Worst | vs gba-mgba |
|---|---|---|---|---|---|
| gba-mgba | GBA | mgba | 1.035 | 1.037 | +0.0% |
| gba-gpsp | GBA | gpsp | 0.571 | 0.578 | -44.8% |
| gba-mgba-harness | GBA | mgba | 1.524 | 1.553 | +47.2% |
| gba-gpsp-harness | GBA | gpsp | 0.477 | 0.489 | -53.9% |
| gb-mgba-card | GB | mgba | no workload (no GB cart on the card) | | |
| gbc-mgba-card | GBC | mgba | no workload (no GBC cart on the card) | | |
| gb-mgba-harness | GB | mgba | 0.390 | 0.403 | -62.3% |
| gbc-mgba-harness | GBC | mgba | 0.386 | 0.387 | -62.7% |
| nes-fceumm | NES | fceumm | 0.064 | 0.065 | -93.8% |
| nes-nestopia | NES | nestopia | 0.039 | 0.040 | -96.2% |
| snes-snes9x | SNES | snes9x | 2.328 | 2.373 | +124.9% |
| snes-snes9x2005_plus | SNES | snes9x2005_plus | 0.519 | 0.524 | -49.9% |

## Rewind: unserialize per frame, worst (ms)

| Pair | Platform | Core | Median | Worst | vs gba-mgba |
|---|---|---|---|---|---|
| gba-mgba | GBA | mgba | 1.464 | 1.469 | +0.0% |
| gba-gpsp | GBA | gpsp | 0.925 | 0.938 | -36.8% |
| gba-mgba-harness | GBA | mgba | 2.061 | 2.135 | +40.8% |
| gba-gpsp-harness | GBA | gpsp | 0.933 | 1.038 | -36.3% |
| gb-mgba-card | GB | mgba | no workload (no GB cart on the card) | | |
| gbc-mgba-card | GBC | mgba | no workload (no GBC cart on the card) | | |
| gb-mgba-harness | GB | mgba | 0.591 | 0.637 | -59.6% |
| gbc-mgba-harness | GBC | mgba | 0.558 | 0.664 | -61.9% |
| nes-fceumm | NES | fceumm | 0.105 | 0.110 | -92.8% |
| nes-nestopia | NES | nestopia | 0.105 | 0.108 | -92.8% |
| snes-snes9x | SNES | snes9x | 2.894 | 2.902 | +97.7% |
| snes-snes9x2005_plus | SNES | snes9x2005_plus | 0.912 | 0.923 | -37.7% |

## Pair status

| Pair | Status |
|---|---|
| gba-mgba | ok |
| gba-gpsp | ok |
| gba-mgba-harness | ok |
| gba-gpsp-harness | ok |
| gb-mgba-card | no workload (no GB cart on the card) |
| gbc-mgba-card | no workload (no GBC cart on the card) |
| gb-mgba-harness | ok |
| gbc-mgba-harness | ok |
| nes-fceumm | ok |
| nes-nestopia | ok |
| snes-snes9x | ok |
| snes-snes9x2005_plus | ok |
