import subprocess
import sys
import unittest
from pathlib import Path


EXPECTED_CLI_TOOLS = [
    "gpt-subtrans",
    "claude-subtrans",
    "gemini-subtrans",
    "deepseek-subtrans",
    "mistral-subtrans",
    "bedrock-subtrans",
    "llm-subtrans",
    "azure-subtrans",
]


class TestCliHelpCommon(unittest.TestCase):
    """Validate common CLI args appear in --help across all variants."""

    # Map module short name to fully qualified module for -m invocation
    MODULES = [
        "gpt",
        "claude",
        "gemini",
        "deepseek",
        "mistral",
        "bedrock",
        "llm",
        "azure",
    ]

    # A concise set of high‑value shared flags to lock
    COMMON_FLAGS = [
        "--output",
        "--target_language",
        "--maxlines",
        "--project",
        "--preprocess",
        "--postprocess",
        "--debug",
    ]

    def test_help_contains_usage_and_common_flags(self):
        for mod in self.MODULES:
            with self.subTest(module=mod):
                cmd = [sys.executable, "-m", f"PySubtitle.cli.{mod}", "--help"]
                result = subprocess.run(cmd, capture_output=True, text=True)

                # Argparse prints help then exits with 0
                self.assertEqual(
                    result.returncode,
                    0,
                    msg=f"--help exited non‑zero for module {mod}: {result.stderr or result.stdout}",
                )

                help_text = (result.stdout or "") + (result.stderr or "")
                self.assertIn("usage:", help_text.lower(), msg=f"usage not in help for {mod}")
                self.assertIn("input", help_text.lower(), msg=f"positional input missing in help for {mod}")

                missing = [flag for flag in self.COMMON_FLAGS if flag not in help_text]
                if missing:
                    self.fail(f"Missing common flags in {mod} help: {', '.join(missing)}\n{help_text}")


class TestCliHelpProviderFlags(unittest.TestCase):
    """Validate provider‑specific flags appear in --help for each CLI."""

    PROVIDER_FLAGS = {
        "gpt": ["--apikey", "--apibase", "--model", "--httpx", "--proxy"],
        "claude": ["--apikey", "--model", "--proxy"],
        "gemini": ["--apikey", "--model"],
        "deepseek": ["--apikey", "--apibase", "--model"],
        "mistral": ["--apikey", "--model", "--server_url"],
        "bedrock": ["--accesskey", "--secretkey", "--region", "--model"],
        "azure": ["--apikey", "--apibase", "--apiversion", "--deploymentname"],
        "llm": ["--server", "--endpoint", "--apikey", "--model", "--chat", "--systemmessages", "--timeout"],
    }

    def test_provider_specific_flags(self):
        for mod, flags in self.PROVIDER_FLAGS.items():
            with self.subTest(module=mod):
                cmd = [sys.executable, "-m", f"PySubtitle.cli.{mod}", "--help"]
                result = subprocess.run(cmd, capture_output=True, text=True)

                self.assertEqual(
                    result.returncode,
                    0,
                    msg=f"--help exited non‑zero for module {mod}: {result.stderr or result.stdout}",
                )

                help_text = (result.stdout or "") + (result.stderr or "")
                missing = [flag for flag in flags if flag not in help_text]
                if missing:
                    self.fail(f"Missing provider flags in {mod} help: {', '.join(missing)}\n{help_text}")


class TestEntryPointsAndExports(unittest.TestCase):
    """Validate pyproject scripts and CLI exports remain consistent."""

    def test_pyproject_scripts_entries(self):
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        self.assertTrue(pyproject_path.exists(), "pyproject.toml not found")

        content = pyproject_path.read_text(encoding="utf-8")

        # Ensure each expected script key exists
        for tool in EXPECTED_CLI_TOOLS:
            self.assertIn(f"{tool} =", content, f"Entry point {tool} not found in pyproject.toml")

    def test_cli_init_exports(self):
        # Import and verify that all exported mains exist
        import importlib

        cli_pkg = importlib.import_module("PySubtitle.cli")
        for name in [
            "gpt_main",
            "claude_main",
            "gemini_main",
            "deepseek_main",
            "mistral_main",
            "bedrock_main",
            "llm_main",
            "azure_main",
        ]:
            with self.subTest(export=name):
                self.assertTrue(hasattr(cli_pkg, name), f"Missing export {name} in PySubtitle.cli")
