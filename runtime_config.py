"""User-facing audio sensitivity and RGB brightness limits.

No hardware access or privileged operations.
"""

import argparse
import math

import numpy as np


def brightness_argument(value):
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError(
            "El brillo debe ser un numero entero de 0 a 255."
        ) from exc

    if not 0 <= result <= 255:
        raise argparse.ArgumentTypeError(
            "El brillo debe estar entre 0 y 255."
        )

    return result


def sensitivity_argument(value):
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError(
            "La sensibilidad debe ser numerica."
        ) from exc

    if not math.isfinite(result) or not 0.5 <= result <= 2.0:
        raise argparse.ArgumentTypeError(
            "La sensibilidad debe estar entre 0.5 y 2.0."
        )

    return result


def adjust_samples(samples, sensitivity):
    """Apply bounded input gain; preserve default samples exactly."""
    if sensitivity == 1.0:
        return samples

    return np.clip(samples * sensitivity, -1.0, 1.0)


def cap_brightness(output, maximum):
    """Scale musical brightness while preserving its relative dynamics."""
    r, g, b, brightness = output

    if maximum == 255:
        return output

    scaled = round(brightness * maximum / 255)

    return r, g, b, scaled
