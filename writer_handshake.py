"""Bounded startup handshake for the privileged RGB writer."""

import os
import selectors
import time


class WriterStartupError(RuntimeError):
    """The RGB writer failed to start correctly."""


def wait_for_writer_ready(writer, timeout=10.0):
    if writer.stdout is None:
        raise WriterStartupError(
            "El escritor RGB no tiene canal de respuesta."
        )

    if timeout <= 0:
        raise ValueError("timeout debe ser positivo")

    deadline = time.monotonic() + timeout
    response = bytearray()

    with selectors.DefaultSelector() as selector:
        selector.register(writer.stdout, selectors.EVENT_READ)

        while True:
            if len(response) >= 64:
                raise WriterStartupError(
                    "Respuesta demasiado larga del escritor RGB."
                )

            remaining = deadline - time.monotonic()

            if remaining <= 0:
                raise WriterStartupError(
                    "Tiempo agotado esperando READY del escritor RGB."
                )

            if not selector.select(remaining):
                raise WriterStartupError(
                    "El escritor RGB no respondio dentro del limite."
                )

            chunk = os.read(writer.stdout.fileno(), 1)

            if not chunk:
                raise WriterStartupError(
                    "El escritor RGB termino sin confirmar READY."
                )

            if chunk == bytes([10]):
                break

            response.extend(chunk)

    if response != b"READY":
        raise WriterStartupError(
            "Respuesta inesperada del escritor RGB."
        )

    return "READY"
