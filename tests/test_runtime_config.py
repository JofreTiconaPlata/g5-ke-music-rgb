import argparse
import unittest

import numpy as np

from runtime_config import (
    adjust_samples,
    brightness_argument,
    cap_brightness,
    sensitivity_argument,
)


class RuntimeConfigTests(unittest.TestCase):
    def test_default_brightness(self):
        self.assertEqual(
            cap_brightness((255, 90, 40, 240), 255),
            (255, 90, 40, 240),
        )

    def test_brightness_cap_preserves_color(self):
        self.assertEqual(
            cap_brightness((255, 90, 40, 240), 120),
            (255, 90, 40, 113),
        )

    def test_brightness_remains_reactive(self):
        values = [40, 90, 150, 210, 255]
        scaled = [
            cap_brightness((255, 90, 40, value), 120)[3]
            for value in values
        ]

        self.assertEqual(scaled, [19, 42, 71, 99, 120])
        self.assertEqual(scaled, sorted(scaled))
        self.assertEqual(len(set(scaled)), len(scaled))

    def test_brightness_boundaries(self):
        self.assertEqual(brightness_argument("0"), 0)
        self.assertEqual(brightness_argument("255"), 255)

        for invalid in ("-1", "256", "abc", "3.5"):
            with self.subTest(value=invalid):
                with self.assertRaises(argparse.ArgumentTypeError):
                    brightness_argument(invalid)

    def test_default_sensitivity_preserves_samples(self):
        samples = np.array([-0.5, 0.0, 0.5])
        result = adjust_samples(samples, 1.0)
        self.assertIs(result, samples)

    def test_sensitivity_gain_and_clipping(self):
        samples = np.array([-0.75, 0.0, 0.75])
        result = adjust_samples(samples, 2.0)
        np.testing.assert_array_equal(
            result, [-1.0, 0.0, 1.0]
        )

    def test_full_brightness_preserves_all_outputs(self):
        for brightness in (0, 12, 75, 120, 200, 255):
            with self.subTest(brightness=brightness):
                output = (128, 220, 64, brightness)
                self.assertEqual(
                    cap_brightness(output, 255), output
                )

    def test_proportional_brightness_order(self):
        original = [12, 75, 120, 180, 255]
        scaled = [
            cap_brightness((128, 220, 64, value), 150)
            for value in original
        ]

        self.assertTrue(
            all(item[:3] == (128, 220, 64) for item in scaled)
        )
        values = [item[3] for item in scaled]
        self.assertEqual(values, sorted(values))
        self.assertEqual(values[-1], 150)
        self.assertGreater(len(set(values)), 1)

    def test_sensitivity_validation(self):
        self.assertEqual(sensitivity_argument("0.5"), 0.5)
        self.assertEqual(sensitivity_argument("1.0"), 1.0)
        self.assertEqual(sensitivity_argument("2.0"), 2.0)

        for invalid in ("0", "2.1", "nan", "inf", "-inf", "abc"):
            with self.subTest(value=invalid):
                with self.assertRaises(argparse.ArgumentTypeError):
                    sensitivity_argument(invalid)
