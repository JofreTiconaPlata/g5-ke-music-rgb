# Performance measurements

## Version comparison

Version | RGB commands/s | Reduction
V3.2 | 21.19 | approximately 0 percent
V3.3 | 10.57 | 50.90 percent
V3.4 | 11.32 | 47.39 percent

Different music sessions were used.

## V3.3 final test

Duration: 60.04 seconds
Audio analyses: 1291
Effective frequency: 21.50 Hz
RGB commands: 650
RGB commands per second: 10.83
Reduction: 49.65 percent

## ACPI measurements

No music RGB: 44.07 IRQ9/s
V3.2: approximately 1340 IRQ9/s
V3.3: 691.20 IRQ9/s
V3.4: 728.53 IRQ9/s

IRQ9 measurements may include unrelated ACPI activity.

## Battery measurements

UPower was used to inspect total battery discharge power.

The power consumed exclusively by the RGB keyboard
has not yet been isolated by a controlled experiment.

## Stable version decision

V3.3 was selected because it provided a similar visual
experience to V3.4 with fewer RGB updates.
