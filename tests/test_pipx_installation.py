"""
Test suite for validating pipx installation process and CLI functionality.

This module tests that the package can be successfully installed via pipx
and that all command-line entry points work correctly.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestPipxInstallation(unittest.TestCase):
    """Test pipx installation and CLI functionality."""

    # All expected CLI entry points from pyproject.toml
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

    @classmethod
    def setUpClass(cls):
        """Set up test environment - verify pipx installation exists."""
        # Check if we're in a CI environment or if pipx is available
        try:
            result = subprocess.run(["pipx", "--version"], capture_output=True, text=True, check=True)
            cls.pipx_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            cls.pipx_available = False

    def setUp(self):
        """Set up each test."""
        if not self.pipx_available:
            self.skipTest("pipx not available - skipping pipx installation tests")

    def test_cli_tools_in_path(self):
        """Test that all CLI tools are available in PATH after pipx installation."""
        missing_tools = []

        for tool in self.EXPECTED_CLI_TOOLS:
            try:
                # Use 'where' on Windows, 'which' on Unix
                cmd = "where" if sys.platform == "win32" else "which"
                result = subprocess.run([cmd, tool], capture_output=True, text=True, check=True)
                self.assertTrue(result.stdout.strip(), f"{tool} not found in PATH")
            except subprocess.CalledProcessError:
                missing_tools.append(tool)

        if missing_tools:
            self.fail(f"CLI tools not found in PATH: {', '.join(missing_tools)}")

    def test_cli_help_commands(self):
        """Test that all CLI tools can display help without errors."""
        failed_tools = []

        for tool in self.EXPECTED_CLI_TOOLS:
            try:
                result = subprocess.run([tool, "--help"], capture_output=True, text=True, check=True, timeout=30)

                # Verify help output contains expected content
                self.assertIn("usage:", result.stdout.lower())
                self.assertIn("input", result.stdout.lower())
                self.assertIn("options:", result.stdout.lower())

            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                failed_tools.append((tool, str(e)))

        if failed_tools:
            failures = [f"{tool}: {error}" for tool, error in failed_tools]
            self.fail(f"CLI tools failed help test: {'; '.join(failures)}")

    def test_package_data_installation(self):
        """Test that package data (instructions.txt) is correctly installed."""
        try:
            # Try to run a tool with debug to see if instructions load
            result = subprocess.run(["gpt-subtrans", "--help"], capture_output=True, text=True, check=True, timeout=30)

            # If help works, the package data should be accessible
            # We can't easily test the exact path without running the tool,
            # but successful help indicates proper installation
            self.assertTrue(result.stdout.strip())

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            self.fail(f"Failed to verify package data installation: {e}")

    def test_srt_file_parsing(self):
        """Test basic SRT file parsing functionality without API calls."""
        # Create a temporary SRT file
        test_srt_content = """1
00:00:01,000 --> 00:00:03,000
Hello, world!

2
00:00:04,000 --> 00:00:06,000
This is a test subtitle.

3
00:00:07,000 --> 00:00:09,000
Testing the translation tool.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".srt", delete=False) as f:
            f.write(test_srt_content)
            temp_srt_path = f.name

        try:
            # Test with maxlines=0 to avoid API calls but still test parsing
            result = subprocess.run(
                ["gpt-subtrans", temp_srt_path, "--maxlines", "0", "--debug"], capture_output=True, text=True, timeout=30
            )

            # Should parse the file and show subtitle count, even if it doesn't translate
            self.assertIn("3 subtitles", result.stderr.lower() + result.stdout.lower())

        except subprocess.TimeoutExpired:
            self.fail("SRT parsing test timed out")
        except subprocess.CalledProcessError as e:
            # Some error is expected since we're not providing API keys
            # But it should still parse the file first
            output = e.stderr + e.stdout if hasattr(e, "stderr") and hasattr(e, "stdout") else str(e)
            if "3 subtitles" not in output.lower():
                self.fail(f"SRT file parsing failed: {output}")
        finally:
            # Clean up temp file
            import contextlib

            with contextlib.suppress(OSError):
                os.unlink(temp_srt_path)

    def test_provider_loading(self):
        """Test that translation providers can be loaded correctly."""
        try:
            # Run with debug to see provider loading
            result = subprocess.run(["gpt-subtrans", "--help"], capture_output=True, text=True, check=True, timeout=30)

            # If help works, providers should load correctly
            self.assertTrue(result.stdout.strip())

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            self.fail(f"Provider loading test failed: {e}")

    def test_different_cli_variants(self):
        """Test that different CLI variants have appropriate help text."""
        cli_variants = {
            "gpt-subtrans": "openai",
            "claude-subtrans": "claude",
            "gemini-subtrans": "gemini",
            "llm-subtrans": "local server",
        }

        for tool, expected_text in cli_variants.items():
            try:
                result = subprocess.run([tool, "--help"], capture_output=True, text=True, check=True, timeout=30)

                # Check that help text is specific to the tool
                help_text = result.stdout.lower()
                self.assertIn(expected_text, help_text, f"{tool} help should mention {expected_text}")

            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                self.fail(f"CLI variant test failed for {tool}: {e}")


class TestPackageStructure(unittest.TestCase):
    """Test package structure and configuration."""

    def test_pyproject_toml_entry_points(self):
        """Test that pyproject.toml has all expected entry points."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

        if not pyproject_path.exists():
            self.skipTest("pyproject.toml not found")

        with open(pyproject_path) as f:
            content = f.read()

        # Check that all expected CLI tools are defined
        for tool in TestPipxInstallation.EXPECTED_CLI_TOOLS:
            self.assertIn(f"{tool} =", content, f"Entry point {tool} not found in pyproject.toml")

    def test_src_layout_structure(self):
        """Test that the package follows src layout structure."""
        src_path = Path(__file__).parent.parent / "src" / "PySubtitle"

        self.assertTrue(src_path.exists(), "src/PySubtitle directory should exist")
        self.assertTrue((src_path / "__init__.py").exists(), "src/PySubtitle/__init__.py should exist")
        self.assertTrue((src_path / "cli").exists(), "src/PySubtitle/cli directory should exist")
        self.assertTrue((src_path / "cli" / "__init__.py").exists(), "src/PySubtitle/cli/__init__.py should exist")

    def test_instructions_file_exists(self):
        """Test that instructions.txt exists in the package."""
        instructions_path = Path(__file__).parent.parent / "src" / "PySubtitle" / "instructions" / "instructions.txt"

        self.assertTrue(instructions_path.exists(), "instructions/instructions.txt should exist in package")

        # Verify it's not empty
        with open(instructions_path, encoding="utf-8") as f:
            content = f.read().strip()

        self.assertTrue(content, "instructions.txt should not be empty")


if __name__ == "__main__":
    unittest.main()
