"""Safe single-instance lock for G5 KE Music RGB."""

import fcntl
import os
import stat

LOCK_PATH = "/tmp/g5-ke-music-rgb-v3.lock"


class InstanceAlreadyRunning(RuntimeError):
    """The keyboard controller is already running."""


def acquire_instance_lock(path=LOCK_PATH):
    flags = (
        os.O_RDWR
        | os.O_CREAT
        | os.O_CLOEXEC
        | os.O_NOFOLLOW
    )

    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        raise RuntimeError(
            f"No se puede abrir el bloqueo de forma segura: {path}: {exc}"
        ) from exc

    try:
        info = os.fstat(fd)

        if not stat.S_ISREG(info.st_mode):
            raise RuntimeError("El archivo de bloqueo no es regular.")

        if info.st_uid != os.getuid():
            raise RuntimeError(
                "El archivo de bloqueo pertenece a otro usuario."
            )

        if info.st_nlink != 1:
            raise RuntimeError(
                "El archivo de bloqueo tiene enlaces adicionales."
            )

        if info.st_mode & 0o022:
            raise RuntimeError(
                "El archivo de bloqueo permite escrituras de terceros."
            )

        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise InstanceAlreadyRunning(
                "G5 KE Music RGB ya esta en ejecucion. "
                "Deten la instancia anterior con Ctrl+C."
            ) from exc

        return os.fdopen(fd, "r")

    except BaseException:
        os.close(fd)
        raise
