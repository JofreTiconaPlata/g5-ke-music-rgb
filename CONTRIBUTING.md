# Contributing to G5 KE Music RGB

Thanks for helping make Linux keyboard lighting easier to reproduce.

## Useful contributions

- **Compatibility reports** for other laptops that expose comparable Linux LED sysfs nodes.
- Documentation fixes and setup screenshots (with private information removed).
- Safer, narrower privilege handling and better process cleanup.
- Audio monitor auto-detection and tests that do **not** require RGB hardware.
- Reproducible measurements under controlled on/off conditions.

## Before opening a pull request

1. Open an issue explaining the problem and hardware involved.
2. Keep changes focused. Avoid modifying fan control, EC registers, BIOS, DKMS or power profiles.
3. Run `python3 -m py_compile music_rgb.py`.
4. Report the real hardware and audio tests performed; **do not** call a change tested if it was not.
5. Keep personally identifying information, serial numbers, credentials and secrets out of issues and commits.
6. Preserve the validated V3.3 behavior unless a change explicitly sets out to modify it.

## Licensing note

No public software license has been selected yet. The maintainers need to review code provenance and compatible permissions before accepting substantial external code contributions. Please discuss licensing **before submitting code that would require redistribution rights**.
