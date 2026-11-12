import os
import unittest

from writer_restore import (
    RestorationNotConfirmed,
    verify_restoration,
)


class FakeWriter:
    def __init__(self):
        read_fd, self.write_fd = os.pipe()
        self.stdout = os.fdopen(read_fd, "rb", buffering=0)

    def send(self, payload):
        os.write(self.write_fd, payload)

    def close(self):
        self.stdout.close()
        os.close(self.write_fd)


class RestorationTests(unittest.TestCase):
    def test_restored_success(self):
        writer = FakeWriter()
        try:
            writer.send(b"RESTORED" + bytes([10]))
            self.assertTrue(
                verify_restoration(writer, timeout=1)
            )
        finally:
            writer.close()

    def test_unexpected_confirmation(self):
        writer = FakeWriter()
        try:
            writer.send(b"ERROR" + bytes([10]))
            with self.assertRaises(RestorationNotConfirmed):
                verify_restoration(writer, timeout=1)
        finally:
            writer.close()

    def test_missing_confirmation(self):
        writer = FakeWriter()
        try:
            with self.assertRaises(RestorationNotConfirmed):
                verify_restoration(writer, timeout=0.05)
        finally:
            writer.close()

    def test_incomplete_confirmation(self):
        writer = FakeWriter()
        try:
            writer.send(b"REST")
            with self.assertRaises(RestorationNotConfirmed):
                verify_restoration(writer, timeout=0.05)
        finally:
            writer.close()
