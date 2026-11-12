# Architecture

## Audio path

1. A normal Linux audio application plays music.
2. `parec` captures PCM samples from a PulseAudio-compatible **output monitor** (typically PipeWire's PulseAudio server).
3. Python accumulates audio samples and computes a NumPy FFT.
4. Eight frequency bands drive a color and brightness model.
5. The adaptive scheduler decides whether a changed LED state is worth sending.
6. A separate privileged writer updates the existing Linux LED sysfs interface.

## Audio and visual cadence

The validated baseline uses approximately 21.5 spectral analyses per second. That is **not** a promise of 21.5 hardware writes per second: V3.3 skips small or redundant updates and prioritizes major color and brightness changes. Across a 180-second test, it sent 1,903 RGB commands (10.57/s).

The RGB keyboard is a **single zone**. It cannot illuminate different keys with different spectral bands: the engine selects one resulting color and brightness for the entire keyboard.

## Privilege boundary

Audio analysis should run under the calling user's account. The LED writer requires elevated rights for sysfs and is invoked separately. The exact writer mechanism is part of `music_rgb.py` and must be audited before using it on additional hardware.

The program uses the kernel's exposed LED interface; it does not write EC memory directly. The underlying keyboard driver may use ACPI or EC messages to fulfill each LED update, causing measurable system interrupts.

## What this project is not

- A replacement for TUXEDO Control Center.
- A keyboard driver or DKMS installer.
- A fan-control or GPU-power-control utility.
- A proven battery-life optimizer.
- A per-key lighting system.

See [Hardware](HARDWARE.md), [Benchmarks](BENCHMARKS.md), and [Security](SECURITY.md).
