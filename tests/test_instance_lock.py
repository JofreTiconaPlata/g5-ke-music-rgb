import os
import tempfile
import unittest
from pathlib import Path

from instance_lock import (
    InstanceAlreadyRunning,
    acquire_instance_lock,
)


class InstanceLockTests(unittest.TestCase):
    def test_acquire_release_and_reacquire(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "lock")
            first = acquire_instance_lock(path)
            first.close()
            second = acquire_instance_lock(path)
            second.close()

    def test_second_instance_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "lock")
            first = acquire_instance_lock(path)
            try:
                with self.assertRaises(InstanceAlreadyRunning):
                    acquire_instance_lock(path)
            finally:
                first.close()

    def test_symbolic_link_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "destination"
            destination.write_text("untouched")
            link = Path(directory) / "lock"
            link.symlink_to(destination)

            with self.assertRaises(RuntimeError):
                acquire_instance_lock(str(link))

            self.assertEqual(destination.read_text(), "untouched")

    def test_group_writable_lock_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lock"
            path.touch(mode=0o600)
            os.chmod(path, 0o666)

            with self.assertRaises(RuntimeError):
                acquire_instance_lock(str(path))
