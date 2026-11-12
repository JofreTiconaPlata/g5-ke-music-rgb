# G5 KE Music RGB

Audio-reactive RGB keyboard lighting for Linux.

## Project

Music-reactive RGB keyboard lighting developed and tested on
GIGABYTE G5 KE with Fedora Workstation 45.

Stable algorithm: V3.3
Main program: music_rgb.py
Keyboard: single-zone RGB
Audio analysis: approximately 21.5 Hz

## Features

- PipeWire audio monitor capture.
- NumPy FFT analysis with eight frequency bands.
- Music-reactive colors and adaptive brightness.
- Adaptive RGB update scheduler.
- Reduced redundant hardware writes.
- Dry-run mode for testing without changing the keyboard.

## Requirements

- Python 3
- NumPy
- parec and PipeWire PulseAudio compatibility
- Compatible TUXEDO/Clevo LED driver
- Administrative authorization for RGB sysfs writes

Fedora dependencies:

    sudo dnf install python3 python3-numpy pulseaudio-utils

## Hardware interface

Required Linux sysfs files:

    /sys/class/leds/rgb:kbd_backlight/multi_intensity
    /sys/class/leds/rgb:kbd_backlight/brightness

Verify that these paths exist before running the program.

## Audio monitor

The tested audio source is:

    alsa_output.pci-0000_00_1f.3.analog-stereo.monitor

List available sources with:

    pactl list short sources

Other systems may require changing the monitor device in the code.

## Usage

Analysis without modifying the keyboard:

    python3 music_rgb.py --dry-run --seconds 15

Run the lighting effect for 60 seconds:

    python3 music_rgb.py --seconds 60

Continuous music-reactive lighting:

    python3 music_rgb.py

Stop the application using Ctrl+C.

## Performance

Measured V3.3 results over approximately 180 seconds:

- 3876 audio analyses.
- 21.52 effective analyses per second.
- 1903 RGB commands.
- 10.57 RGB commands per second.
- 50.90 percent fewer RGB commands than updating every analysis.

Performance varies depending on audio content.

## Compatibility and safety

Only tested on GIGABYTE G5 KE.

The application does not install kernel drivers,
modify firmware, change BIOS settings or configure DKMS.

Do not grant unrestricted write access to sysfs.

Do not run multiple keyboard lighting controllers simultaneously.

## Documentation

See docs/HARDWARE.md and docs/BENCHMARKS.md.

## License

A redistribution license has not yet been selected.
Code provenance must be reviewed before public release.

This is an independent project, not officially affiliated
with GIGABYTE or TUXEDO Computers.
