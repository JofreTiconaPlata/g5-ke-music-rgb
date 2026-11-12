import contextlib
import io
import subprocess
import unittest

from types import SimpleNamespace
from unittest.mock import Mock, patch

import music_rgb
from audio_devices import AudioDiscoveryError
from writer_handshake import WriterStartupError


class RuntimeErrorTests(unittest.TestCase):
    def check_cli_failure(self, error, expected):
        stderr = io.StringIO()

        with (
            patch("sys.argv", ["music_rgb.py", "--dry-run"]),
            patch.object(music_rgb, "run", side_effect=error),
            contextlib.redirect_stderr(stderr),
        ):
            result = music_rgb.main()

        self.assertEqual(result, 1)
        self.assertIn(expected, stderr.getvalue())

    def test_audio_error_is_readable(self):
        self.check_cli_failure(
            AudioDiscoveryError("Monitor no disponible"),
            "ERROR: Monitor no disponible",
        )

    def test_writer_startup_error_is_readable(self):
        self.check_cli_failure(
            WriterStartupError("READY no recibido"),
            "ERROR: READY no recibido",
        )

    def test_capture_error_is_readable(self):
        self.check_cli_failure(
            RuntimeError("La captura de audio se ha detenido"),
            "ERROR: La captura de audio se ha detenido",
        )

    def test_unexpected_programming_error_is_not_hidden(self):
        with (
            patch("sys.argv", ["music_rgb.py", "--dry-run"]),
            patch.object(
                music_rgb, "run",
                side_effect=ValueError("programming defect"),
            ),
        ):
            with self.assertRaisesRegex(
                ValueError, "programming defect"
            ):
                music_rgb.main()

    def test_missing_monitor_does_not_start_sudo(self):
        lock = Mock()

        with (
            patch.object(
                music_rgb,
                "acquire_instance_lock",
                return_value=lock,
            ),
            patch.object(
                music_rgb,
                "select_monitor",
                side_effect=AudioDiscoveryError(
                    "Monitor no disponible"
                ),
            ),
            patch.object(
                music_rgb.subprocess, "run"
            ) as sudo_command,
        ):
            args = SimpleNamespace(
                dry_run=False,
                monitor=None,
            )

            with self.assertRaises(AudioDiscoveryError):
                music_rgb.run(args)

        sudo_command.assert_not_called()
        lock.close.assert_called_once_with()

    def test_missing_led_does_not_start_sudo(self):
        lock = Mock()

        with (
            patch.object(
                music_rgb,
                "acquire_instance_lock",
                return_value=lock,
            ),
            patch.object(
                music_rgb,
                "select_monitor",
                return_value=SimpleNamespace(
                    name="fake.monitor"
                ),
            ),
            patch.object(
                music_rgb.os.path,
                "exists",
                return_value=False,
            ),
            patch.object(
                music_rgb.subprocess,
                "run",
            ) as sudo_command,
        ):
            args = SimpleNamespace(
                dry_run=False,
                monitor=None,
            )

            with self.assertRaisesRegex(
                RuntimeError, "controlador RGB"
            ):
                music_rgb.run(args)

        sudo_command.assert_not_called()
        lock.close.assert_called_once_with()
