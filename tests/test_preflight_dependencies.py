import unittest

from preflight import check_dependencies


def available_numpy(name):
    if name != "numpy":
        raise AssertionError("Unexpected dependency")
    return object()


def missing_numpy(name):
    raise ImportError("numpy unavailable")


def available_command(name):
    return "/usr/bin/" + name


def missing_command(name):
    return None


class PreflightDependencyTests(unittest.TestCase):
    def test_dependencies_available(self):
        errors = check_dependencies(
            python_version=(3, 15),
            numpy_import=available_numpy,
            find_executable=available_command,
        )
        self.assertEqual(errors, [])

    def test_missing_numpy(self):
        errors = check_dependencies(
            python_version=(3, 15),
            numpy_import=missing_numpy,
            find_executable=available_command,
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("NumPy", errors[0])

    def test_missing_audio_commands(self):
        errors = check_dependencies(
            python_version=(3, 15),
            numpy_import=available_numpy,
            find_executable=missing_command,
        )
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("pactl" in item for item in errors))
        self.assertTrue(any("parec" in item for item in errors))

    def test_python_version_checked(self):
        errors = check_dependencies(
            python_version=(3, 9),
            numpy_import=available_numpy,
            find_executable=available_command,
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("Python 3.10", errors[0])
