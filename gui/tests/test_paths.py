import tempfile
import unittest
from pathlib import Path

from cas_harness.io import safe_mkdir
from cas_harness.paths import (
    PathPolicyError,
    resolve_run_root,
    safe_run_path,
    validate_report_filename,
)


class PathPolicyTests(unittest.TestCase):
    def test_validate_report_filename_rejects_path_traversal(self):
        with self.assertRaises(PathPolicyError):
            validate_report_filename("../../outside.tex")

    def test_validate_report_filename_rejects_absolute_path(self):
        with self.assertRaises(PathPolicyError):
            validate_report_filename("/tmp/outside.tex")

    def test_validate_report_filename_accepts_tex_filename(self):
        self.assertEqual(validate_report_filename("technical_report.tex"), "technical_report.tex")

    def test_safe_run_path_accepts_contained_absolute(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "candidates" / "candidate-001" / "root_cause.md"
            got = safe_run_path(root, target, allowed_subtree="candidates")
            self.assertEqual(got, target.resolve(strict=False))

    def test_safe_run_path_rejects_absolute_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(PathPolicyError):
                safe_run_path(Path(tmp), "/tmp/outside")

    def test_safe_run_path_accepts_contained_parent_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            got = safe_run_path(
                root,
                "candidates/scratch/../candidate-001/root_cause.md",
                allowed_subtree="candidates",
            )
            expected = root / "candidates" / "candidate-001" / "root_cause.md"
            self.assertEqual(got, expected.resolve(strict=False))

    def test_safe_run_path_rejects_parent_traversal_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(PathPolicyError):
                safe_run_path(Path(tmp), "../outside")

    def test_safe_run_path_accepts_contained_subtree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            got = safe_run_path(root, "final-report/technical_report.tex", allowed_subtree="final-report")
            self.assertEqual(got, (root / "final-report" / "technical_report.tex").resolve(strict=False))

    def test_safe_run_path_rejects_symlinked_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            (root / "bug-report").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(PathPolicyError):
                safe_run_path(root, "bug-report/file.txt", allowed_subtree="bug-report")

    def test_safe_mkdir_rejects_symlinked_output_dir_escape(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            (root / "_work").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(PathPolicyError):
                safe_mkdir(root, root / "_work" / "gui")

    def test_safe_mkdir_accepts_symlinked_output_dir_inside_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real_work = root / "real-work"
            real_work.mkdir()
            (root / "_work").symlink_to(real_work, target_is_directory=True)
            got = safe_mkdir(root, root / "_work" / "gui")
            self.assertEqual(got, (real_work / "gui").resolve())

    def test_resolve_run_root_accepts_symlink_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = base / "target"
            target.mkdir()
            link = base / "run-root"
            link.symlink_to(target, target_is_directory=True)
            self.assertEqual(resolve_run_root(link), target.resolve())

    def test_resolve_run_root_rejects_broken_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            link = base / "run-root"
            link.symlink_to(base / "missing", target_is_directory=True)
            with self.assertRaises(PathPolicyError):
                resolve_run_root(link)


if __name__ == "__main__":
    unittest.main()
