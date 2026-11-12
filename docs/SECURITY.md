# Security and privilege model

This project controls keyboard LED brightness and RGB through Linux sysfs. On the tested machine those nodes require elevated privileges.

## Recommendations

- Read `music_rgb.py`, especially the dedicated writer and process management, before running.
- Keep audio capture and FFT analysis in the unprivileged user process.
- Use the smallest privilege boundary possible. Do **not** run the entire music application with `sudo`.
- Never use `chmod 777` on `/sys/class/leds`, broadly permissive udev rules, or unrestricted passwordless `sudo` to make it work.
- Do not modify BIOS, firmware, EC registers, Secure Boot settings, fan curves or kernel modules as part of this application.
- Do not run different keyboard LED applications concurrently.
- Understand that a clean exit can restore previous LED settings; a system crash or forced kill may not.

## Reporting a security concern

Avoid posting working exploits, credentials, access tokens or private device identifiers in a public issue. Contact the repository maintainer privately through their GitHub profile before sharing sensitive details.

## Scope

This project is a userspace RGB controller, not a kernel driver, TUXEDO Control Center replacement, fan-control utility or BIOS-tuning tool.

## Runtime safety boundaries

The runtime safeguards are implemented in application-level
Python code. They do not require changing sudoers, PAM, kernel
modules, firmware, BIOS, EC configuration, udev rules or global
system permissions.

The privileged writer validates RGB channel and brightness
ranges before writing to the keyboard interface.

Unit tests verify lock behavior and writer acknowledgements
using isolated temporary files and local pipes. They do not
require privileged hardware access.

Normal shutdown restoration has been checked on the GIGABYTE
G5 KE. Restoration cannot be guaranteed after abrupt process
termination, power loss or underlying hardware failure.
