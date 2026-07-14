import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("git"), "Git is required")
class SetupSympyTargetTests(unittest.TestCase):
    def test_local_repo_setup_handles_spaces_and_returns_path_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source repo"
            source.mkdir()
            subprocess.run(
                ["git", "init", "--initial-branch=main", str(source)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subprocess.run(
                ["git", "-C", str(source), "config", "user.email", "test@example.com"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(source), "config", "user.name", "Test User"],
                check=True,
            )
            (source / "sympy").mkdir()
            (source / "sympy" / "__init__.py").write_text(
                '__version__ = "test"\n', encoding="utf-8"
            )
            subprocess.run(["git", "-C", str(source), "add", "."], check=True)
            subprocess.run(
                ["git", "-C", str(source), "commit", "-m", "fixture"],
                check=True,
                stdout=subprocess.PIPE,
            )

            base = root / "target area with spaces"
            proc = subprocess.run(
                [
                    sys.executable,
                    "scripts/setup_sympy_target.py",
                    "--base-dir",
                    str(base),
                    "--repo-url",
                    str(source),
                    "--ref",
                    "HEAD",
                    "--run-name",
                    "windows-path-test",
                    "--no-fetch",
                    "--no-conda",
                    "--output",
                    "path",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            target = Path(proc.stdout.strip())
            self.assertTrue((target / "sympy" / "__init__.py").is_file())
            metadata = json.loads(
                (base / "metadata" / "windows-path-test.json").read_text(encoding="utf-8")
            )
            self.assertEqual(Path(metadata["target_dir"]), target)


if __name__ == "__main__":
    unittest.main()
