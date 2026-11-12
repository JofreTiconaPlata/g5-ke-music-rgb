# G5 KE Music RGB — Guía rápida en español

**Iluminación del teclado RGB que reacciona a la música en Linux.**

Probado en **GIGABYTE G5 KE con Fedora Workstation 45**. El teclado validado es de **una sola zona**; no ofrece colores independientes por tecla.

## Requisitos

- Python 3 y NumPy.
- PipeWire compatible con PulseAudio y utilidad `parec`.
- Controlador de teclado compatible que exponga `rgb:kbd_backlight` en sysfs.
- Autorización `sudo` para el proceso que escribe el RGB.

## Instalación

```bash
sudo dnf install git python3 python3-numpy pulseaudio-utils
git clone https://github.com/JofreTiconaPlata/g5-ke-music-rgb.git
cd g5-ke-music-rgb
```

Comprobar la interfaz **sin modificarla**:

```bash
LED=/sys/class/leds/rgb:kbd_backlight
cat "$LED/multi_intensity"
cat "$LED/brightness"
```

Si los archivos no existen, **no sigas**: este proyecto no instala controladores y no es compatible con todos los modelos Clevo o GIGABYTE.

## Seleccionar el audio correcto

```bash
pactl list short sources
```

La versión probada utiliza `alsa_output.pci-0000_00_1f.3.analog-stereo.monitor`, que puede ser diferente en tu máquina. Revisa la configuración en `music_rgb.py` antes de usarlo.

## Probar el programa

```bash
python3 music_rgb.py --dry-run --seconds 15
python3 music_rgb.py --seconds 60
```

Para ejecutarlo continuamente:

```bash
python3 music_rgb.py
```

Detener mediante **Ctrl+C**. No ejecutes toda la aplicación como root; el código utiliza un escritor privilegiado separado. No concedas permisos globales de escritura a sysfs.

## Resultados y limitaciones

La **V3.3** consiguió 21,52 análisis musicales/s, 10,57 comandos RGB/s y una reducción del 50,90 % de comandos durante una prueba de 180 segundos. Estas cifras dependen de la canción y del equipo.

La compatibilidad con otros portátiles no está verificada. No se ha medido de forma concluyente el consumo eléctrico adicional individual del efecto RGB.

Más información: [README principal](../README.md), [solución de problemas](TROUBLESHOOTING.md), [hardware](HARDWARE.md).
