#!/usr/bin/env python3
"""Read-only platform diagnostics; does NOT run the RGB music engine."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

from audio_devices import AudioDiscoveryError, list_monitors, select_monitor

LED_DIR = Path('/sys/class/leds/rgb:kbd_backlight')


def check_led(root: Path = LED_DIR) -> list[str]:
    """Check exposed LED attributes without writing anything to sysfs."""
    errors: list[str] = []
    for name in ("multi_intensity", "brightness"):
        path = root / name
        if not path.is_file():
            errors.append(f"Falta la interfaz LED: {path}")
            continue
        try:
            content = path.read_text().strip()
            if name == 'multi_intensity':
                values = [int(x) for x in content.split()]
                if len(values) != 3 or any(not (0 <= x <= 255) for x in values):
                    errors.append(f"Valor RGB inesperado en {path}: {content!r}")
            else:
                int(content)
        except (OSError, ValueError) as exc:
            errors.append(f"No se pudo leer {path}: {exc}")
    return errors


def check_dependencies(
    *,
    python_version=None,
    numpy_import=None,
    find_executable=None,
) -> list[str]:
    """Check requirements without changing the system.

    Optional dependencies allow isolated unit testing.
    """
    import importlib

    if python_version is None:
        python_version = sys.version_info[:2]

    if numpy_import is None:
        numpy_import = importlib.import_module

    if find_executable is None:
        find_executable = shutil.which

    errors = []

    if tuple(python_version[:2]) < (3, 10):
        errors.append(
            "Se requiere Python 3.10 o posterior."
        )

    try:
        numpy_import("numpy")
    except (ImportError, OSError) as exc:
        errors.append(
            f"NumPy no esta disponible: {exc}. "
            "Fedora: python3-numpy."
        )

    for command in ("pactl", "parec"):
        if not find_executable(command):
            errors.append(
                f"Falta {command}. "
                "Fedora: paquete pulseaudio-utils."
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Diagnostico seguro de audio y LED RGB (solo lectura)')
    parser.add_argument('--list-monitors', action='store_true', help='Listar monitores de salida')
    parser.add_argument('--monitor', help='Seleccionar un nombre exacto de monitor')
    parser.add_argument('--audio-only', action='store_true', help='Omitir diagnostico de LED sysfs')
    args = parser.parse_args(argv)

    dependency_errors = check_dependencies()
    if dependency_errors:
        for error in dependency_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2
    try:
        if args.list_monitors:
            monitors = list_monitors()
            if not monitors:
                print('No se encontraron monitores de audio', file=sys.stderr)
                return 2
            for item in monitors:
                print(item)
            return 0
        selected = select_monitor(args.monitor)
    except AudioDiscoveryError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2

    print('Monitor seleccionado:', selected.name)
    print('Metodo:', selected.origin)
    print('Monitores detectados:', len(selected.available))
    if not args.audio_only:
        errors = check_led()
        if errors:
            for error in errors:
                print('ERROR:', error, file=sys.stderr)
            return 3
        print('Interfaz LED: disponible y legible')
    print('Comprobacion finalizada. No se escribio en el teclado.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
