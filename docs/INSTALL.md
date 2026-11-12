# Installation and first run

> Tested environment: Fedora Workstation 45 on a GIGABYTE G5 KE. This project **does not** install the necessary keyboard kernel driver.

## Before you begin

- The keyboard RGB interface must already work through the Linux LED subsystem.
- Fedora should use PipeWire with PulseAudio compatibility for the `parec` monitor capture.
- A Python 3 interpreter with NumPy and `parec` must be available.
- You should be able to use `sudo` for the **dedicated LED writer**; do not run the entire analyzer as root.
- Close other RGB control applications during testing to avoid competing writes.

## Install userspace packages

```bash
sudo dnf install git python3 python3-numpy pulseaudio-utils
```

Check:

```bash
python3 -c 'import numpy; print("NumPy:", numpy.__version__)'
command -v parec
command -v pactl
```

## Clone and inspect

```bash
git clone https://github.com/JofreTiconaPlata/g5-ke-music-rgb.git
cd g5-ke-music-rgb
python3 -m py_compile music_rgb.py
```

Review the source, especially the privileged writer, before the first hardware run.

## Verify compatible sysfs LEDs

```bash
LED=/sys/class/leds/rgb:kbd_backlight
for item in multi_intensity brightness; do
    test -r "$LED/$item" && echo "Found: $item" || echo "Missing: $item"
done
```

If either file is missing, **stop**. Do not follow instructions for unrelated Clevo models, copy unsigned modules, disable Secure Boot, or poke EC registers to force compatibility.

## Audio monitor selection

List monitor sources:

```bash
pactl list short sources
pactl info
```

The tested source was:

```text
alsa_output.pci-0000_00_1f.3.analog-stereo.monitor
```

That is **not a universal value**. Search `music_rgb.py` for the monitor setting (for example, `alsa_output` or `MONITOR`) and ensure it matches your active *output monitor*. Source naming and output routing vary between installations. The current baseline does not provide automatic source detection.

## Run and verify

With audio playing:

```bash
python3 music_rgb.py --dry-run --seconds 15
```

You should see nonzero RMS values and changing RGB values. A successful dry-run **does not** prove hardware write permissions.

Next:

```bash
python3 music_rgb.py --seconds 60
```

Provide `sudo` authorization when requested. The program should animate the entire keyboard (one-zone RGB). For continuous mode:

```bash
python3 music_rgb.py
```

Stop with **Ctrl+C**. Verify that your previous keyboard state returns after a normal exit. Abrupt process termination, hardware errors or a system crash may prevent restoration.

## Known boundaries

- This project does not configure or install the TUXEDO/Clevo modules.
- Not all GIGABYTE or Clevo models share this LED sysfs implementation.
- Keyboard color is global, not per-key.
- Do not enable unattended autostart or passwordless `sudo` until a separate security review.

Next: [Troubleshooting](TROUBLESHOOTING.md) · [Security](SECURITY.md).
