import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


PINNED_SCRIPT = """\
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if SYMPY_CHECKOUT_PATH:
    sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
"""


class ValidateAdvanceTests(unittest.TestCase):
    def test_malformed_plan_returns_structured_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = root / "_work" / "batch-001" / "plans" / "verify_batch.json"
            write_json(plan, [])
            proc = run_script(
                "scripts/gui_validate_phase.py",
                "--run-root",
                str(root),
                "--batch",
                "1",
                "--phase",
                "verify",
                "--json",
            )
            self.assertEqual(proc.returncode, 0)
            self.assertNotIn("Traceback", proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["status"], "blocked")
            self.assertTrue(any("not an object" in error for error in payload["errors"]))
            self.assertTrue((root / "_work" / "gui" / "validation" / "batch-001-verify.json").is_file())
            self.assertFalse((root / "_work" / "gui" / "repairs").exists())

    def test_advance_requires_validation_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = root / "_work" / "batch-001" / "plans" / "candidate_batch.json"
            write_json(plan, {"status": "no_candidate", "candidates": []})
            proc = run_script(
                "scripts/gui_advance_phase.py",
                "--run-root",
                str(root),
                "--batch",
                "1",
                "--phase",
                "hunter",
            )
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(proc.stderr, "")
            payload = json.loads(proc.stdout)
            self.assertFalse(payload["advanced"])
            self.assertEqual(payload["status"], "blocked_needs_validation")
            self.assertIn("missing validation receipt", payload["error"])

    def test_no_candidate_routes_to_next_hunter_after_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = root / "_work" / "batch-001" / "plans" / "candidate_batch.json"
            write_json(plan, {"status": "no_candidate", "candidates": []})
            validate = run_script(
                "scripts/gui_validate_phase.py",
                "--run-root",
                str(root),
                "--batch",
                "1",
                "--phase",
                "hunter",
                "--json",
            )
            self.assertEqual(validate.returncode, 0, validate.stderr)
            advance = run_script(
                "scripts/gui_advance_phase.py",
                "--run-root",
                str(root),
                "--batch",
                "1",
                "--phase",
                "hunter",
            )
            self.assertEqual(advance.returncode, 0, advance.stderr)
            payload = json.loads(advance.stdout)
            self.assertEqual(payload["next_phase"], "hunter")
            self.assertEqual(payload["next_batch"], 2)
            self.assertTrue(payload["empty_pass"])
            self.assertFalse((root / "_work" / "batch-001" / "plans" / "verify_batch.json").exists())

    def test_diagnosis_accepts_narrowed_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = root / "_work" / "batch-001" / "plans" / "diagnosis_batch.json"
            report = root / "candidates" / "candidate-001" / "root_cause.md"
            write_json(
                plan,
                {
                    "candidates": [
                        {
                            "candidate_number": 1,
                            "root_cause_path": "candidates/candidate-001/root_cause.md",
                        }
                    ]
                },
            )
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(
                "---\n"
                "diagnosis_status: narrowed\n"
                "confidence: 60\n"
                "location: sympy/example.py:10\n"
                "---\n"
                "\n"
                "## Root Cause\n"
                "Localized to a function but not an exact faulty step.\n",
                encoding="utf-8",
            )
            proc = run_script(
                "scripts/gui_validate_phase.py",
                "--run-root",
                str(root),
                "--batch",
                "1",
                "--phase",
                "diagnosis",
                "--json",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["ok"])

    def test_artifact_validation_sanitizes_public_paths_and_copies_root_cause(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "run"
            sympy_dir = Path(tmp) / "sympy-dev"
            candidate_dir = root / "candidates" / "candidate-001"
            artifact_dir = root / "bug-report" / "bug-001-demo"
            plan = root / "_work" / "batch-001" / "plans" / "artifact_batch.json"
            status_path = candidate_dir / "artifact_status.json"
            candidate_json = candidate_dir / "candidate_minimized.json"
            root_cause = candidate_dir / "root_cause.md"

            sympy_dir.mkdir(parents=True)
            artifact_dir.mkdir(parents=True)
            (artifact_dir / "pr" / "tests").mkdir(parents=True)
            write_json(candidate_json, {"title": "demo"})
            root_cause.write_text("root cause details\n", encoding="utf-8")
            (artifact_dir / "README.md").write_text(
                f"Public report leaked {sympy_dir.resolve()}\n",
                encoding="utf-8",
            )
            (artifact_dir / "reproduce_bug.py").write_text(PINNED_SCRIPT, encoding="utf-8")
            (artifact_dir / "related_bugs.py").write_text(PINNED_SCRIPT, encoding="utf-8")
            (artifact_dir / "dedup_report.md").write_text("dedup\n", encoding="utf-8")
            (artifact_dir / "pr" / "README.md").write_text("pr\n", encoding="utf-8")
            (artifact_dir / "pr" / "tests" / "test_bug_001_demo.py").write_text(
                "def test_placeholder():\n    assert True\n",
                encoding="utf-8",
            )
            write_json(
                status_path,
                {
                    "status": "artifact_created",
                    "artifact_dir": "bug-report/bug-001-demo",
                },
            )
            write_json(
                plan,
                {
                    "bug_report_root": "bug-report",
                    "items": [
                        {
                            "candidate_number": 1,
                            "candidate_json_path": "candidates/candidate-001/candidate_minimized.json",
                            "artifact_status_path": "candidates/candidate-001/artifact_status.json",
                        }
                    ],
                },
            )

            proc = run_script(
                "scripts/gui_validate_phase.py",
                "--run-root",
                str(root),
                "--sympy-dir",
                str(sympy_dir),
                "--batch",
                "1",
                "--phase",
                "artifact",
                "--json",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            readme = (artifact_dir / "README.md").read_text(encoding="utf-8")
            self.assertNotIn(str(sympy_dir.resolve()), readme)
            self.assertIn("<SYMPY_CHECKOUT_PATH>", readme)
            self.assertEqual(
                (artifact_dir / "root_cause.md").read_text(encoding="utf-8"),
                "root cause details\n",
            )

    def test_writeup_report_traversal_rejected_after_plan_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = root / "_work" / "writeup" / "gui_writeup_plan.json"
            write_json(plan, {"summary": {"bug_artifacts": []}})
            proc = run_script(
                "scripts/gui_writeup_assemble.py",
                "--run-root",
                str(root),
                "--sympy-dir",
                str(root),
                "--writeup-report-name",
                "../../outside.tex",
                "--skip-pdf",
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("report name must be a filename", proc.stderr)
            self.assertFalse((root.parent / "outside.tex").exists())


if __name__ == "__main__":
    unittest.main()
