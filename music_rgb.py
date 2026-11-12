#!/usr/bin/env python3
"""G5 KE Music RGB V3 — PipeWire + 8 bandas + HSV.

Diseño inspirado en AudioLevels de G-Helper (GPL-3.0):
https://github.com/seerge/g-helper

No se importa código de G-Helper ni se controlan ventiladores.
"""

import argparse
import colorsys
import collections
import fcntl
import os
import signal
import subprocess
import sys
import time

import numpy as np

LED = "/sys/class/leds/rgb:kbd_backlight"

RATE = 22050
FFT_SIZE = 2048
HOP = 256
FPS_LIMIT = 20
HOPS_PER_UPDATE = 4

# Planificador adaptativo RGB.
# Tiempos en segundos, no frecuencias de la FFT.
RGB_FAST_INTERVAL = 0.040
RGB_NORMAL_INTERVAL = 0.085
RGB_MAX_INTERVAL = 0.220

# Distancia RGB euclidiana y brillo absoluto.
RGB_URGENT_DISTANCE = 165.0
RGB_URGENT_BRIGHTNESS = 48
RGB_MIN_DISTANCE = 16.0
RGB_MIN_BRIGHTNESS = 6

# Espectro de ocho bandas.
EDGES = np.array([
    35, 90, 180, 350, 700,
    1400, 2800, 5600, 9000
])

# Tonalidades: rojo, naranja, amarillo,
# verde, turquesa, cian, azul, violeta.
HUES = np.array([
    0.00, 0.065, 0.14, 0.32,
    0.43, 0.51, 0.62, 0.77
])

# Ganancia espectral inicial por banda.
GAINS = np.array([
    1.00, 1.05, 1.15, 1.25,
    1.35, 1.50, 1.65, 1.80
])

# Parámetros musicales.
BRIGHTNESS_MAX = 255
BRIGHTNESS_FLOOR = 75
SILENCE_BRIGHTNESS = 12
NOISE_GATE = 0.0008

# Ataque y decaimiento.
ATTACK = 0.95
RELEASE = 0.60
HUE_SMOOTH = 0.85
PEAK_DECAY = 0.75

# Solo este código mínimo se ejecuta como administrador.
# No ejecutamos el archivo editable del usuario como root.
WRITER = r'''
import signal
import sys

LED = "/sys/class/leds/rgb:kbd_backlight"
COLOR = LED + "/multi_intensity"
BRIGHTNESS = LED + "/brightness"

signal.signal(signal.SIGINT, signal.SIG_IGN)

def read(path):
    with open(path) as f:
        return f.read().strip()

def write(path, value):
    with open(path, "w") as f:
        f.write(str(value) + "\n")

original_color = read(COLOR)
original_brightness = read(BRIGHTNESS)
maximum = int(read(LED + "/max_brightness"))
last_color = original_color
last_brightness = int(original_brightness)

print("READY", flush=True)

try:
    for line in sys.stdin:
        values = line.split()
        if len(values) != 4:
            continue

        try:
            r, g, b, bright = map(int, values)
        except ValueError:
            continue

        if not all(0 <= x <= 255 for x in (r, g, b)):
            continue

        if not 0 <= bright <= maximum:
            continue

        color = f"{r} {g} {b}"

        if color != last_color:
            write(COLOR, color)
            last_color = color

        if bright != last_brightness:
            write(BRIGHTNESS, bright)
            last_brightness = bright

finally:
    try:
        write(COLOR, original_color)
        write(BRIGHTNESS, original_brightness)
        print("RESTORED", flush=True)
    except OSError as exc:
        print(f"RGB restore failed: {exc}", file=sys.stderr)
'''


class MusicEngine:
    def __init__(self):
        self.window = np.hanning(FFT_SIZE)
        self.freqs = np.fft.rfftfreq(FFT_SIZE, 1 / RATE)

        self.masks = [
            (self.freqs >= a) & (self.freqs < b)
            for a, b in zip(EDGES[:-1], EDGES[1:])
        ]

        self.history = collections.deque(maxlen=100)
        self.band_refs = np.ones(8) * 0.025
        self.envelope = 0.0

        self.rgb = np.array([255.0, 30.0, 0.0])
        self.brightness = float(BRIGHTNESS_FLOOR)
        self.hue = 0.0
        self.last_levels = np.zeros(8)

    def process(self, samples):
        rms = float(np.sqrt(np.mean(samples ** 2)))

        spectrum = np.abs(
            np.fft.rfft(samples * self.window)
        )

        # Promedio de energía en cada intervalo.
        levels = np.array([
            float(np.sqrt(np.mean(spectrum[m] ** 2)))
            for m in self.masks
        ]) * GAINS

        # Referencia adaptativa de cada banda:
        # subida rápida y descenso más lento.
        self.band_refs = np.where(
            levels > self.band_refs,
            self.band_refs * 0.65 + levels * 0.35,
            self.band_refs * 0.985 + levels * 0.015
        )

        if rms < NOISE_GATE:
            target_rgb = np.array([30.0, 12.0, 65.0])
            target_brightness = SILENCE_BRIGHTNESS
            self.envelope *= PEAK_DECAY

        else:
            # Comprime diferencias y evita que una
            # única banda domine permanentemente.
            # Cada banda compite respecto a su propio
            # nivel reciente, no solo por potencia absoluta.
            relative = levels / np.maximum(
                self.band_refs, 0.0001
            )

            relative = np.clip(relative, 0.0, 3.0)

            # Compresion espectral para dar presencia
            # a medios y agudos sin perder los graves.
            weights = np.power(
                np.maximum(levels, 0.0), 0.22
            )
            weights *= np.power(relative + 0.05, 0.85)

            weights /= max(float(weights.sum()), 1e-12)

            # Color por banda, saturación completa.
            band_colors = np.array([
                colorsys.hsv_to_rgb(float(h), 1.0, 1.0)
                for h in HUES
            ])

            mixed = weights @ band_colors

            # Identifica la frecuencia dominante.
            dominant = int(np.argmax(weights))

            dominant_color = band_colors[dominant]

            # La banda dominante determina parte
            # del color; el resto mantiene riqueza.
            target_rgb = (
                0.60 * mixed + 0.40 * dominant_color
            )

            target_rgb *= (
                255.0 / max(float(target_rgb.max()), 1e-9)
            )

            # Historial de volumen y referencia P90.
            self.history.append(rms)
            history = np.asarray(self.history)

            low = float(np.percentile(history, 15))
            high = float(np.percentile(history, 95))

            # Contraste local del volumen, en vez
            # de saturar todo con RMS / pico.
            dynamic_range = max(
                high - low, high * 0.12, 0.005
            )

            loudness = float(np.clip(
                0.22 + 0.72 * (rms - low)
                / dynamic_range,
                0.12, 0.97
            ))

            # Detector de cambios positivos:
            # golpes de bombo y percusión.
            onset = np.maximum(
                levels - self.last_levels, 0.0
            )

            onset_strength = float(
                np.sum(onset[:4])
                / max(np.sum(self.band_refs[:4]), 0.01)
            )

            impact = min(0.30, onset_strength * 0.20)

            self.envelope = max(
                self.envelope * PEAK_DECAY,
                min(1.0, loudness + impact)
            )

            # Curva sensible también en pasajes suaves.
            intensity = np.power(
                np.clip(self.envelope, 0, 1),
                0.65
            )

            target_brightness = (
                BRIGHTNESS_FLOOR
                + (BRIGHTNESS_MAX - BRIGHTNESS_FLOOR)
                * intensity
            )

        self.last_levels = levels

        # Transiciones RGB con ataque rápido.
        self.rgb += HUE_SMOOTH * (
            target_rgb - self.rgb
        )

        # Brillo responde inmediatamente al golpe,
        # con una caída más suave.
        alpha = (
            ATTACK
            if target_brightness > self.brightness
            else RELEASE
        )

        self.brightness += alpha * (
            target_brightness - self.brightness
        )

        rgb = tuple(
            int(x) for x in np.clip(
                np.rint(self.rgb), 0, 255
            )
        )

        brightness = int(np.clip(
            round(self.brightness), 0, BRIGHTNESS_MAX
        ))

        return (*rgb, brightness), rms, dominant if rms >= NOISE_GATE else -1


def audio_monitor():
    sink = subprocess.check_output(
        ["pactl", "get-default-sink"],
        text=True
    ).strip()

    monitor = sink + ".monitor"

    sources = subprocess.check_output(
        ["pactl", "list", "short", "sources"],
        text=True
    )

    if monitor not in sources:
        raise RuntimeError(
            f"Monitor de audio no encontrado: {monitor}"
        )

    return monitor


def run(args):
    # Evita ejecutar dos copias de esta aplicación.
    lock = open("/tmp/g5-ke-music-rgb-v3.lock", "w")

    try:
        fcntl.flock(
            lock, fcntl.LOCK_EX | fcntl.LOCK_NB
        )
    except BlockingIOError:
        raise RuntimeError(
            "Ya existe una instancia de RGB Music V3"
        )

    if not args.dry_run:
        if not os.path.exists(LED + "/multi_intensity"):
            raise RuntimeError(
                "El controlador RGB no está disponible"
            )

        # Contraseña en el terminal normal.
        # Sin sudo -n ni start_new_session.
        subprocess.run(["sudo", "-v"], check=True)

    writer = None
    audio = None
    frames_processed = 0
    commands_sent = 0
    urgent_sent = 0
    normal_sent = 0
    refresh_sent = 0
    skipped_frames = 0
    started_at = None
    last_sent_at = None

    try:
        if not args.dry_run:
            writer = subprocess.Popen(
                [
                    "sudo",
                    "/usr/bin/python3",
                    "-I",
                    "-u",
                    "-c",
                    WRITER,
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                bufsize=0,
            )

            ready = writer.stdout.readline().decode().strip()

            if ready != "READY":
                raise RuntimeError(
                    "No se pudo iniciar el escritor RGB. "
                    "Comprueba la autenticación sudo."
                )

        monitor = audio_monitor()

        audio = subprocess.Popen(
            [
                "parec",
                "--device=" + monitor,
                "--format=s16le",
                "--rate=" + str(RATE),
                "--channels=1",
                "--latency-msec=25",
                "--raw",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        engine = MusicEngine()

        buffer = np.zeros(FFT_SIZE)
        previous = None
        hop_counter = 0
        last_debug = 0.0
        start = time.monotonic()
        started_at = start

        print("\n========== G5 KE RGB MUSIC V3 ==========")
        print("Monitor:", monitor)
        print("Bandas:", len(HUES))
        print("Brillo máximo:", BRIGHTNESS_MAX)
        print(
            "Cadencia nominal:",
            f"{RATE / (HOP * HOPS_PER_UPDATE):.2f} Hz"
        )
        print("Modo:", "SOLO ANÁLISIS" if args.dry_run else "RGB ACTIVO")
        print("Detener: Ctrl+C\n", flush=True)

        while True:
            # 46 ms de nuevas muestras por iteración.
            chunk = audio.stdout.read(HOP * 2)

            if len(chunk) != HOP * 2:
                raise RuntimeError(
                    "La captura de audio se ha detenido"
                )

            samples = np.frombuffer(
                chunk, dtype="<i2"
            ).astype(np.float64) / 32768.0

            buffer[:-HOP] = buffer[HOP:]
            buffer[-HOP:] = samples

            now = time.monotonic()

            # Procesar cada 4 bloques de audio.
            # 4 * 256 / 22050 = 46.4 ms nominales.
            hop_counter += 1
            if hop_counter < HOPS_PER_UPDATE:
                continue

            hop_counter = 0

            output, rms, dominant = engine.process(buffer)
            frames_processed += 1

            if args.dry_run:
                if now - last_debug >= 0.5:
                    print(
                        f"RMS={rms:.4f} "
                        f"Banda={dominant + 1 if dominant >= 0 else 0} "
                        f"RGB={output[:3]} "
                        f"Brillo={output[3]}",
                        flush=True
                    )
                    last_debug = now
            else:
                if writer.poll() is not None:
                    raise RuntimeError(
                        "El proceso RGB finalizo inesperadamente"
                    )

                if previous is None:
                    should_send = True
                    reason = "inicio"
                else:
                    age = now - last_sent_at

                    delta_rgb = np.array(
                        output[:3], dtype=np.float64
                    ) - np.array(
                        previous[:3], dtype=np.float64
                    )
                    color_distance = float(
                        np.linalg.norm(delta_rgb)
                    )
                    brightness_distance = abs(
                        output[3] - previous[3]
                    )

                    urgent = (
                        color_distance >= RGB_URGENT_DISTANCE
                        or brightness_distance
                        >= RGB_URGENT_BRIGHTNESS
                    )
                    significant = (
                        color_distance >= RGB_MIN_DISTANCE
                        or brightness_distance
                        >= RGB_MIN_BRIGHTNESS
                    )

                    if (
                        urgent
                        and age >= RGB_FAST_INTERVAL
                    ):
                        should_send = True
                        reason = "urgente"
                    elif (
                        significant
                        and age >= RGB_NORMAL_INTERVAL
                    ):
                        should_send = True
                        reason = "normal"
                    elif (
                        output != previous
                        and age >= RGB_MAX_INTERVAL
                    ):
                        should_send = True
                        reason = "refresco"
                    else:
                        should_send = False
                        reason = "omitido"

                if should_send:
                    try:
                        writer.stdin.write(
                            ("%d %d %d %d\n" % output).encode()
                        )
                        writer.stdin.flush()
                    except (BrokenPipeError, OSError):
                        raise RuntimeError(
                            "Fallo al enviar el color al escritor RGB"
                        ) from None

                    commands_sent += 1
                    last_sent_at = now
                    previous = output

                    if reason == "urgente":
                        urgent_sent += 1
                    elif reason == "normal":
                        normal_sent += 1
                    elif reason == "refresco":
                        refresh_sent += 1
                else:
                    skipped_frames += 1

            if args.seconds and now - start >= args.seconds:
                break

    except KeyboardInterrupt:
        print("\nDeteniendo visualizador...", flush=True)

    finally:
        if audio is not None:
            if audio.poll() is None:
                audio.terminate()
            try:
                audio.wait(timeout=3)
            except subprocess.TimeoutExpired:
                audio.kill()
                audio.wait()

        if writer is not None:
            if writer.stdin:
                try:
                    writer.stdin.close()
                except OSError:
                    pass

            try:
                writer.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(
                    "ADVERTENCIA: restauración RGB no confirmada.",
                    file=sys.stderr
                )
                writer.terminate()
                try:
                    writer.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    writer.kill()
                    writer.wait()

            if writer.returncode != 0:
                print(
                    "ADVERTENCIA: el escritor terminó con error.",
                    file=sys.stderr
                )

        if started_at is not None:
            elapsed = max(
                time.monotonic() - started_at, 0.001
            )
            print()
            print("========== ESTADISTICAS V3.3 ==========")
            print(f"Duracion: {elapsed:.2f} s")
            print(f"Analisis realizados: {frames_processed}")
            print(
                "Frecuencia efectiva:",
                f"{frames_processed / elapsed:.2f} Hz"
            )
            if not args.dry_run:
                print(f"Comandos RGB enviados: {commands_sent}")
                print(f"Comandos urgentes: {urgent_sent}")
                print(f"Comandos normales: {normal_sent}")
                print(f"Refrescos: {refresh_sent}")
                print(f"Analisis sin envio: {skipped_frames}")
                if frames_processed:
                    reduction = 100.0 * (
                        1.0 - commands_sent / frames_processed
                    )
                    print(
                        "Reduccion de comandos:",
                        f"{reduction:.2f}%"
                    )
                print(
                    "Comandos por segundo:",
                    f"{commands_sent / elapsed:.2f}"
                )
            print("======================================")

        lock.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analizar sin modificar el teclado"
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=0,
        help="Detener después de N segundos"
    )

    args = parser.parse_args()

    if args.seconds < 0:
        parser.error("--seconds debe ser >= 0")

    run(args)


if __name__ == "__main__":
    main()
