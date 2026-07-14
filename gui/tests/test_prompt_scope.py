import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "gui_prepare_phase.py"


def load_prepare_module():
    spec = importlib.util.spec_from_file_location("gui_prepare_phase", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PromptScopeTests(unittest.TestCase):
    def test_correctness_scope_is_prepended(self):
        module = load_prepare_module()
        prompt = module.add_correctness_scope("Original phase prompt")

        self.assertTrue(prompt.startswith("# Task Scope"))
        self.assertIn("ordinary software quality assurance for SymPy", prompt)
        self.assertIn("incorrect", prompt)
        self.assertIn("symbolic-mathematics results", prompt)
        self.assertTrue(prompt.endswith("Original phase prompt"))

    def test_example_prompt_exposes_pdf_toggle(self):
        prompt = (ROOT / "CHATGPT_APP_EXAMPLE_RUN.txt").read_text(encoding="utf-8")

        self.assertIn("HUNTER_BATCHES: 1", prompt)
        self.assertIn("GENERATE_PDF: true", prompt)
        self.assertIn("GENERATE_PDF is false", prompt)
        self.assertIn("--skip-pdf", prompt)


if __name__ == "__main__":
    unittest.main()
