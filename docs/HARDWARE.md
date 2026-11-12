# Hardware compatibility

## Tested laptop

| Item | Tested configuration |
| :-- | :-- |
| Model | GIGABYTE G5 KE |
| CPU | Intel Core i5-12500H |
| Dedicated GPU | NVIDIA RTX 3060 Laptop |
| OS | Fedora Workstation 45 |
| Keyboard | Single-zone RGB |
| Interface | Linux LED sysfs `rgb:kbd_backlight` |

The original development system had compatible Clevo/TUXEDO modules available, including `clevo_acpi`, `tuxedo_io`, `tuxedo_keyboard` and `tuxedo_compatibility_check`. **Their presence on that machine does not establish compatibility on yours.**

## Required Linux LED nodes

```text
/sys/class/leds/rgb:kbd_backlight/multi_intensity
/sys/class/leds/rgb:kbd_backlight/brightness
```

`multi_intensity` represents the RGB channels, while `brightness` controls global intensity. The RGB output is applied to **one lighting zone**.

Read-only probe:

```bash
LED=/sys/class/leds/rgb:kbd_backlight
ls -ld "$LED"
cat "$LED/multi_intensity"
cat "$LED/brightness"
```

If the LED nodes are missing, **do not** attempt to remedy this by writing EC registers, disabling Secure Boot, copying another machine's DKMS artifacts, or guessing module parameters.

## Why not promise Clevo-wide support?

OEM firmware, keyboard controllers and Linux driver interfaces vary between models, revisions and kernels. This project has been verified only on the G5 KE. Please include exact hardware, kernel, sysfs listings and a *nonprivileged dry-run* when reporting another model. Avoid posting serial numbers or private identifiers.

## TUXEDO profile is separate

Power profiles, fan curves and CPU frequency limits configured in TUXEDO Control Center are **not** required by the music visualizer's algorithm. This project does not alter those profiles or adjust fan control.
