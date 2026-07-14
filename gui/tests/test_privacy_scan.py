import json
import tempfile
import unittest
from pathlib import Path

from cas_harness.privacy import make_public_summary
from cas_harness.security import scan_paths


class PrivacyScanTests(unittest.TestCase):
    def test_public_summary_drops_private_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = {
                "sympy_version": "1.15.0.dev",
                "sympy_commit": "abc123",
                "result_dir": "/private/run",
                "sympy_checkout_path": "/private/sympy",
                "python_executable": "/private/python",
                "bug_artifacts": [{"artifact_dir": str(root / "bug-report" / "bug-001-demo")}],
            }
            public = make_public_summary(summary, root)
            text = json.dumps(public)
            self.assertNotIn("/private", text)
            self.assertEqual(public["bug_artifacts"][0]["artifact_dir"], "bug-report/bug-001-demo")

    def test_security_scan_ignores_internal_and_flags_public(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public = root / "README.md"
            public.write_text("bad /private marker /ryu/example\n", encoding="utf-8")
            internal = root / "docs" / "internal" / "PLAN.md"
            internal.parent.mkdir(parents=True)
            internal.write_text("allowed internal marker /ryu/example\n", encoding="utf-8")
            findings = scan_paths([root])
            self.assertTrue(any("README.md" in item for item in findings))
            self.assertFalse(any("PLAN.md" in item for item in findings))

    def test_security_scan_flags_windows_user_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "README.md"
            path.write_text(
                "private C:\\Users\\Example\\sympy checkout\n",
                encoding="utf-8",
            )
            findings = scan_paths([path])
            self.assertTrue(any("\\Users\\" in item for item in findings))


if __name__ == "__main__":
    unittest.main()
