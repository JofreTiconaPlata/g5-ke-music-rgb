import unittest
from unittest.mock import patch
import audio_devices


class DiscoveryTests(unittest.TestCase):
    SOURCES = (
        '18\talsa_input.pci-0000_00_1f.3.analog-stereo\tPipeWire\ts16le\t2ch\t48000Hz\tRUNNING\n'
        '19\talsa_output.pci-0000_00_1f.3.analog-stereo.monitor\tPipeWire\ts16le\t2ch\t48000Hz\tIDLE\n'
        '20\tother.monitor\tPipeWire\ts16le\t2ch\t48000Hz\tIDLE'
    )

    def test_prefers_default_sink_monitor(self):
        def fake(*args):
            if args == ('list', 'short', 'sources'):
                return self.SOURCES
            if args == ('get-default-sink',):
                return 'alsa_output.pci-0000_00_1f.3.analog-stereo'
            raise AssertionError(args)
        with patch.object(audio_devices, '_pactl', side_effect=fake):
            result = audio_devices.select_monitor()
        self.assertEqual(result.name, 'alsa_output.pci-0000_00_1f.3.analog-stereo.monitor')
        self.assertEqual(result.origin, 'default-sink')

    def test_explicit_selection(self):
        with patch.object(audio_devices, '_pactl', side_effect=lambda *a: self.SOURCES if a[0]=='list' else 'not-found'):
            result = audio_devices.select_monitor('other.monitor')
        self.assertEqual(result.origin, 'explicit')
        self.assertEqual(result.name, 'other.monitor')

    def test_unknown_monitor_rejected(self):
        with patch.object(audio_devices, '_pactl', side_effect=lambda *a: self.SOURCES if a[0]=='list' else 'not-found'):
            with self.assertRaises(audio_devices.AudioDiscoveryError):
                audio_devices.select_monitor('nonexistent.monitor')

    def test_ambiguous_sources_fail_closed(self):
        with patch.object(audio_devices, '_pactl', side_effect=lambda *a: self.SOURCES if a[0]=='list' else 'not-found'):
            with self.assertRaises(audio_devices.AudioDiscoveryError):
                audio_devices.select_monitor()


if __name__ == '__main__':
    unittest.main()
