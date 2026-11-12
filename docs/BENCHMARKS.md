# Measurements and reproducibility

These are **observed engineering measurements**, not a universal performance benchmark. Different song segments and background tasks can change both RGB command rate and ACPI interrupts.

## Tested V3.3 (adaptive scheduler)

| Run | Duration | FFT analyses | Analysis rate | RGB commands | RGB commands/s | Skipped updates |
| :-- | --: | --: | --: | --: | --: | --: |
| Original validation | ~180 s | 3,876 | 21.52 Hz | 1,903 | 10.57 | 50.90% |
| Consolidated `music_rgb.py` | 60.04 s | 1,291 | 21.50 Hz | 650 | 10.83 | 49.65% |
| Additional long run | 195.39 s | 4,206 | 21.53 Hz | 2,180 | 11.16 | 48.17% |

## Compared prototypes

| Variant | RGB commands/s | Reduction vs. analysis cadence |
| :-- | --: | --: |
| V3.2 (near-every-analysis RGB) | 21.19 | approximately 0% |
| **V3.3 (selected)** | **10.57** | **50.90%** |
| V3.4 (spectral-event scheduler) | 11.32 | 47.39% |

V3.3 and V3.4 felt practically indistinguishable on the tested hardware; V3.3 was chosen because it was simpler and sent fewer writes in the observed sessions. This is **not** a same-audio A/B experiment.

## IRQ9 / ACPI observations

| Condition | Observed IRQ9/s |
| :-- | --: |
| RGB animation stopped | ~44.07 |
| V3.2 | ~1,340 |
| V3.3 | ~691.20 |
| V3.4 | ~728.53 |

The counts are collected through `/proc/interrupts` using timed differences. ACPI IRQ9 can be shared with activity other than keyboard RGB. **Do not infer watts from IRQ/s.**

## Battery testing caveat

UPower's `energy-rate` reports total power discharged by the battery, not CPU-only or LED-only power. Preliminary laptop discharge readings were not collected under sufficiently controlled paired conditions to isolate the incremental music-RGB effect. A precise per-feature wattage figure is therefore **not published**.

## How to reproduce safely

1. Record hardware model, kernel, Fedora version, TUXEDO/driver state and whether the GPU is suspended.
2. Keep music, display brightness, power source, audio output, power profile and background tasks as constant as practical.
3. Take a baseline IRQ9 sample with RGB animation stopped.
4. Run `python3 music_rgb.py --seconds 180`, logging the printed counters.
5. Sample IRQ9 **while the animation is running**, not after it ends.
6. Repeat multiple on/off trials rather than trusting a single interval.
7. Do not poll `nvidia-smi` during a battery comparison if doing so wakes the dGPU.

Example **read-only** IRQ9 measurement:

```bash
read_irq9() {
  awk '$1=="9:" {s=0; for(i=2;i<=NF;i++) {if ($i ~ /^[0-9]+$/) s+=$i; else break} print s}' /proc/interrupts
}
a=$(read_irq9)
sleep 15
b=$(read_irq9)
awk -v n="$((b-a))" 'BEGIN {printf "IRQ9/s: %.2f\n",n/15}'
```

## What is not measured

- Per-key LED performance (hardware is one zone).
- Physical LED transition latency measured with a camera or photodiode.
- Reliable incremental energy use in watts.
- Stability across days or other laptop models.
