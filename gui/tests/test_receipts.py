import tempfile
import unittest
from pathlib import Path

from cas_harness.receipts import require_receipt, write_receipt


class ReceiptManifestTests(unittest.TestCase):
    def symlink_or_skip(self, link: Path, target: Path) -> None:
        try:
            link.symlink_to(target, target_is_directory=True)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"directory symlinks are unavailable: {exc}")

    def test_require_receipt_rejects_changed_validated_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = root / "_work" / "batch-001" / "plans" / "verify_batch.json"
            report = root / "candidates" / "candidate-001" / "verify_report.md"
            plan.parent.mkdir(parents=True)
            report.parent.mkdir(parents=True)
            plan.write_text('{"candidates": []}\n', encoding="utf-8")
            report.write_text("verdict: confirmed\n", encoding="utf-8")

            write_receipt(
                run_root=root,
                phase="verify",
                batch=1,
                plan_path=plan,
                ok=True,
                errors=[],
                manifest_paths=[report],
            )
            report.write_text("verdict: refuted\n", encoding="utf-8")

            with self.assertRaises(SystemExit) as cm:
                require_receipt(root, "verify", 1, plan)
            self.assertIn("validation receipt is stale for outputs", str(cm.exception))

    def test_receipt_manifest_accepts_alias_to_same_run_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            real = base / "private-var"
            alias = base / "var"
            real.mkdir()
            self.symlink_or_skip(alias, real)
            root = alias / "run"
            plan = root / "_work" / "batch-001" / "plans" / "verify_batch.json"
            report = root / "candidates" / "candidate-001" / "verify_report.md"
            plan.parent.mkdir(parents=True)
            report.parent.mkdir(parents=True)
            plan.write_text('{"candidates": []}\n', encoding="utf-8")
            report.write_text("verdict: confirmed\n", encoding="utf-8")

            write_receipt(
                run_root=root,
                phase="verify",
                batch=1,
                plan_path=plan,
                ok=True,
                errors=[],
                manifest_paths=[report],
            )
            receipt = require_receipt(root, "verify", 1, plan)
            self.assertTrue(receipt["validated_outputs"])


if __name__ == "__main__":
    unittest.main()
