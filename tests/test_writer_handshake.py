import os
import unittest

from writer_handshake import (
    WriterStartupError,
    wait_for_writer_ready,
)


class FakeWriter:
    def __init__(self):
        self.read_fd, self.write_fd = os.pipe()
        self.stdout = os.fdopen(self.read_fd, "rb", buffering=0)

    def send(self, data):
        os.write(self.write_fd, data)

    def close(self):
        self.stdout.close()
        os.close(self.write_fd)


class WriterHandshakeTests(unittest.TestCase):
    def test_ready_success(self):
        writer = FakeWriter()
        try:
            writer.send(b"READY" + bytes([10]))
            self.assertEqual(
                wait_for_writer_ready(writer, timeout=1),
                "READY"
            )
        finally:
            writer.close()

    def test_unexpected_response(self):
        writer = FakeWriter()
        try:
            writer.send(b"ERROR" + bytes([10]))

            with self.assertRaises(WriterStartupError):
                wait_for_writer_ready(writer, timeout=1)
        finally:
            writer.close()

    def test_timeout_without_response(self):
        writer = FakeWriter()
        try:
            with self.assertRaises(WriterStartupError):
                wait_for_writer_ready(writer, timeout=0.05)
        finally:
            writer.close()

    def test_incomplete_response_times_out(self):
        writer = FakeWriter()
        try:
            writer.send(b"REA")

            with self.assertRaises(WriterStartupError):
                wait_for_writer_ready(writer, timeout=0.05)
        finally:
            writer.close()
