# Hardware and compatibility

Tested laptop: GIGABYTE G5 KE
Processor: Intel Core i5-12500H
GPU: NVIDIA RTX 3060 Laptop
Operating system: Fedora Workstation 45
RGB keyboard: single-zone

Kernel modules present on the tested system:

- clevo_acpi
- tuxedo_io
- tuxedo_keyboard
- tuxedo_compatibility_check

LED sysfs interface:

    /sys/class/leds/rgb:kbd_backlight/multi_intensity
    /sys/class/leds/rgb:kbd_backlight/brightness

The RGB writer uses these interfaces.

The underlying kernel driver may communicate with
the embedded controller through ACPI or other mechanisms.

This project does not distribute kernel modules.

Never install unverified EC control tools or firmware
modifications solely to use this application.

Compatibility with other laptop models is not guaranteed.
