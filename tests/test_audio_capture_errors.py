import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import music_rgb


class CaptureErrorTests(unittest.TestCase):
    def test_capture_exited_with_error(self):
        capture = Mock()
        capture.poll.return_value = 1

        message = music_rgb.capture_interruption_message(capture)

        self.assertIn("codigo 1", message)
        self.assertIn("preflight.py", message)

    def test_capture_exited_normally(self):
        capture = Mock()
        capture.poll.return_value = 0

        message = music_rgb.capture_interruption_message(capture)

        self.assertIn("dejo de entregar audio", message)

    def test_capture_without_exit_status(self):
        capture = Mock()
        capture.poll.return_value = None

        message = music_rgb.capture_interruption_message(capture)

        self.assertIn("datos incompletos", message)

    def test_capture_cleanup_after_exit(self):
        from contextlib import redirect_stdout
        from io import StringIO

        capture = Mock()
        capture.stdout.read.return_value = b""
        capture.poll.return_value = 1

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
                return_value=SimpleNamespace(name="test.monitor"),
            ),
            patch.object(
                music_rgb.subprocess,
                "Popen",
                return_value=capture,
            ),
            redirect_stdout(StringIO()),
        ):
            args = SimpleNamespace(
                dry_run=True,
                monitor=None,
                brightness=255,
                sensitivity=1.0,
                seconds=0,
            )

            with self.assertRaisesRegex(
                RuntimeError, "parec termino con codigo 1"
            ):
                music_rgb.run(args)

        capture.terminate.assert_not_called()
        capture.wait.assert_called_once_with(timeout=3)
        lock.close.assert_called_once_with()

    def test_keyboard_interrupt_closes_capture(self):
        from contextlib import redirect_stdout
        from io import StringIO

        capture = Mock()
        capture.stdout.read.side_effect = KeyboardInterrupt
        capture.poll.return_value = None

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
                return_value=SimpleNamespace(name="test.monitor"),
            ),
            patch.object(
                music_rgb.subprocess,
                "Popen",
                return_value=capture,
            ),
            redirect_stdout(StringIO()),
        ):
            args = SimpleNamespace(
                dry_run=True,
                monitor=None,
                brightness=255,
                sensitivity=1.0,
                seconds=0,
            )

            music_rgb.run(args)

        capture.terminate.assert_called_once_with()
        capture.wait.assert_called_once_with(timeout=3)
        lock.close.assert_called_once_with()

    def test_missing_parec_is_reported_without_real_process(self):
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
                return_value=SimpleNamespace(name="test.monitor"),
            ),
            patch.object(
                music_rgb.subprocess,
                "Popen",
                side_effect=FileNotFoundError("parec"),
            ),
            patch.object(
                music_rgb.subprocess,
                "run",
            ) as sudo_command,
        ):
            args = SimpleNamespace(
                dry_run=True,
                monitor=None,
            )

            with self.assertRaisesRegex(
                RuntimeError, "No se encontro parec"
            ):
                music_rgb.run(args)

        sudo_command.assert_not_called()
        lock.close.assert_called_once_with()
