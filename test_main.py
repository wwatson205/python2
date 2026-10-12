import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main


class TestNovaAI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)

        self.dir_patch = patch.object(
            main, "DATA_DIR", self.directory
        )
        self.file_patch = patch.object(
            main, "MEMORY_FILE",
            self.directory / "memory.json"
        )
        self.dir_patch.start()
        self.file_patch.start()
        self.ai = main.NovaAI()

    def tearDown(self):
        self.dir_patch.stop()
        self.file_patch.stop()
        self.temp_dir.cleanup()

    def test_calculation(self):
        self.assertEqual(main.calculate("2 + 3 * 4"), 14)

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            main.calculate("5 / 0")

    def test_reject_python_code(self):
        with self.assertRaises(ValueError):
            main.calculate("__import__('os')")

    def test_memory(self):
        response = self.ai.respond(
            "retiens que Paris est une capitale"
        )
        self.assertIn("je retiens", response.lower())
        self.assertIn("paris", self.ai.memory["facts"])

    def test_memory_persistence(self):
        self.ai.remember("langage", "Python")
        new_ai = main.NovaAI()
        self.assertEqual(
            new_ai.memory["facts"]["langage"], "Python"
        )

    def test_greeting(self):
        self.assertIn(
            self.ai.respond("bonjour"),
            [
                "Bonjour ! Comment puis-je t'aider ?",
                "Salut ! Je suis Nova AI.",
                "Hello ! Que souhaites-tu faire aujourd'hui ?"
            ]
        )


if __name__ == "__main__":
    unittest.main()