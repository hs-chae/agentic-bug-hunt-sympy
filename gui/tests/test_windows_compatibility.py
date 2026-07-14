import unittest
from pathlib import Path

from core.agentic_harness import latex_compile_command


class WindowsCompatibilityTests(unittest.TestCase):
    def test_powershell_latex_command_quotes_paths_and_checks_exit(self):
        command = latex_compile_command(
            "pdflatex",
            r"C:\Program Files\TeX\pdflatex.exe",
            Path(r"C:\Work Area\report.tex"),
            Path(r"C:\Work Area\out"),
            shell="powershell",
        )
        self.assertIn('"C:\\Program Files\\TeX\\pdflatex.exe"', command)
        self.assertIn("$LASTEXITCODE", command)
        self.assertNotIn(" && ", command)


if __name__ == "__main__":
    unittest.main()
