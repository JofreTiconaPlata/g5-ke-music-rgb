"""Bounded verification of RGB restoration acknowledgement."""

import os
import selectors
import time


class RestorationNotConfirmed(RuntimeError):
    """The writer did not confirm successful RGB restoration."""


def verify_restoration(writer, timeout=1.0):
    if writer.stdout is None:
        raise RestorationNotConfirmed(
            "No existe canal de confirmacion RGB."
        )

    if timeout <= 0:
        raise ValueError("timeout debe ser positivo")

    deadline = time.monotonic() + timeout
    response = bytearray()

    with selectors.DefaultSelector() as selector:
        selector.register(writer.stdout, selectors.EVENT_READ)

        while True:
            remaining = deadline - time.monotonic()

            if remaining <= 0:
                raise RestorationNotConfirmed(
                    "Tiempo agotado esperando RESTORED."
                )

            if not selector.select(remaining):
                raise RestorationNotConfirmed(
                    "No se recibio confirmacion RESTORED."
                )

            chunk = os.read(writer.stdout.fileno(), 1)

            if not chunk:
                raise RestorationNotConfirmed(
                    "El escritor cerro sin confirmar RESTORED."
                )

            if chunk == bytes([10]):
                break

            response.extend(chunk)

            if len(response) > 64:
                raise RestorationNotConfirmed(
                    "Respuesta de restauracion demasiado larga."
                )

    if response != b"RESTORED":
        raise RestorationNotConfirmed(
            "Confirmacion de restauracion inesperada."
        )

    return True
