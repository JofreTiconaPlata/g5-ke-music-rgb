# Troubleshooting

## The keyboard does not react

1. Confirm that `--dry-run` reports changing RMS/color values **while music plays**.
2. Check that `multi_intensity` and `brightness` exist under `/sys/class/leds/rgb:kbd_backlight/`.
3. Check that `sudo` authorization succeeded for the privileged writer.
4. Stop other apps controlling the keyboard LEDs and try the 60-second test again.
5. Confirm that the audio monitor corresponds to the **currently playing output**.

A nonzero number of *queued* RGB commands does not by itself prove that the writer completed kernel LED writes. Check read-only LED values during the run:

```bash
LED=/sys/class/leds/rgb:kbd_backlight
cat "$LED/multi_intensity"
cat "$LED/brightness"
```

## The analysis is silent or has zero RMS

```bash
pactl list short sources
pactl info
```

The source used on the development laptop is machine-specific. Verify `parec`'s configured output monitor in `music_rgb.py`, play audio to that output and rerun `--dry-run`.

## Python reports NumPy missing

On Fedora:

```bash
sudo dnf install python3-numpy
python3 -c 'import numpy; print(numpy.__version__)'
```

## `parec` is missing

```bash
sudo dnf install pulseaudio-utils
command -v parec
```

## `sudo` fails or asks for a password

This is expected for a privileged writer. Run interactively in a terminal where you are permitted to use `sudo`. **Do not** work around it by making the LED files world-writable or configuring unrestricted passwordless root execution.

## The keyboard remains on a color after an abnormal exit

Normal termination is designed to restore the previous state, but a crash, `SIGKILL`, system shutdown or driver error can prevent restoration. Stop competing LED programs and use the normal trusted keyboard-lighting interface to restore the preferred color. Avoid blind writes to EC registers.

## High CPU or IRQ9 activity

Read-only observation:

```bash
grep '^ *9:' /proc/interrupts
```

IRQ9 counts include ACPI activity beyond this program. To compare properly, use the same audio, display brightness, power profile and a timed **on/off** measurement. IRQ/s is not a wattage value.

## Still having trouble?

Open a GitHub issue with the Fedora version, kernel, laptop model, dry-run summary, existence of the LED nodes, and the exact error. **Do not post** access tokens, serial numbers, home-directory secrets or your full environment dump.

## Runtime and restoration diagnostics

If the program reports that another instance is running, check
whether an earlier visualizer is still open. Stop that instance
normally with Ctrl+C in its original terminal.

Do not delete lock files or terminate privileged processes
as a routine troubleshooting procedure.

If READY is not received, the application reports a startup
failure after its bounded waiting period.

If RESTORED is not received, or the writer exits unexpectedly,
the application reports a warning. Check the actual keyboard
color and brightness before assuming restoration succeeded.

The dry-run mode analyzes audio without changing keyboard
lighting. It is suitable for verifying audio capture and FFT
processing without performing RGB writes.
