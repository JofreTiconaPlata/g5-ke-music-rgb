"""Read-only audio monitor discovery for PipeWire's PulseAudio compatibility layer.

No privileged operations, file writes, or changes to existing audio routing.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass


class AudioDiscoveryError(RuntimeError):
    """A monitor source could not be discovered or verified."""


@dataclass(frozen=True)
class MonitorSelection:
    name: str
    available: tuple[str, ...]
    default_sink: str | None
    origin: str


def _pactl(*args: str) -> str:
    try:
        proc = subprocess.run(
            ["pactl", *args], capture_output=True, text=True,
            timeout=5, check=False,
        )
    except FileNotFoundError as exc:
        raise AudioDiscoveryError("Falta pactl. En Fedora: sudo dnf install pulseaudio-utils") from exc
    except subprocess.TimeoutExpired as exc:
        raise AudioDiscoveryError("pactl no respondio en 5 segundos") from exc
    if proc.returncode:
        raise AudioDiscoveryError(
            f"pactl {' '.join(args)} fallo ({proc.returncode}): "
            + (proc.stderr.strip() or proc.stdout.strip() or "sin detalles")
        )
    return proc.stdout.strip()


def list_monitors() -> tuple[str, ...]:
    """Return actual monitor names, in pactl source-list order."""
    names: list[str] = []
    for line in _pactl("list", "short", "sources").splitlines():
        columns = line.split()
        if len(columns) >= 2 and columns[1].endswith(".monitor"):
            names.append(columns[1])
    return tuple(dict.fromkeys(names))


def select_monitor(requested: str | None = None) -> MonitorSelection:
    monitors = list_monitors()
    if not monitors:
        raise AudioDiscoveryError(
            "No se detecto ningun monitor de salida. Comprueba que "
            "PipeWire/PulseAudio esta disponible: pactl info"
        )
    default_sink: str | None = None
    try:
        default_sink = _pactl("get-default-sink").splitlines()[0].strip()
    except (AudioDiscoveryError, IndexError):
        # Older pactl versions may not support this subcommand.
        pass

    if requested is not None:
        if requested not in monitors:
            raise AudioDiscoveryError(
                f"Monitor no disponible: {requested!r}. "
                f"Opciones: {', '.join(monitors)}"
            )
        return MonitorSelection(requested, monitors, default_sink, "explicit")

    preferred = f"{default_sink}.monitor" if default_sink else None
    if preferred in monitors:
        return MonitorSelection(preferred, monitors, default_sink, "default-sink")
    if len(monitors) == 1:
        return MonitorSelection(monitors[0], monitors, default_sink, "unique-monitor")
    raise AudioDiscoveryError(
        "Hay varios monitores y no se pudo identificar el predeterminado. "
        "Selecciona uno con --monitor NOMBRE: " + ", ".join(monitors)
    )
