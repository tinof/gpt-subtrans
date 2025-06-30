#!/usr/bin/env python3
"""
Local test runner for pipx installation validation.

This script allows developers to test the pipx installation process locally
before committing changes. It provides detailed output and can be run
independently of the CI pipeline.
"""

import contextlib
import os
import subprocess  # nosec B404
import sys
import tempfile
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


class PipxInstallationTester:
    """Test pipx installation process locally."""

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

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.errors: list[str] = []

    def log(self, message: str, color: str = Colors.END):
        """Log a message with optional color."""
        if self.verbose:
            print(f"{color}{message}{Colors.END}")

    def log_success(self, message: str):
        """Log a success message."""
        self.log(f"✓ {message}", Colors.GREEN)

    def log_error(self, message: str):
        """Log an error message."""
        self.log(f"✗ {message}", Colors.RED)
        self.errors.append(message)

    def log_warning(self, message: str):
        """Log a warning message."""
        self.log(f"⚠ {message}", Colors.YELLOW)

    def log_info(self, message: str):
        """Log an info message."""
        self.log(f"ℹ {message}", Colors.BLUE)

    def run_command(self, cmd: list[str], timeout: int = 30) -> tuple[bool, str, str]:
        """Run a command and return success, stdout, stderr."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)  # nosec B603
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout if e.stdout else "", e.stderr if e.stderr else str(e)
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except FileNotFoundError:
            return False, "", f"Command not found: {cmd[0]}"

    def check_pipx_available(self) -> bool:
        """Check if pipx is available."""
        self.log_info("Checking pipx availability...")
        success, stdout, stderr = self.run_command(["pipx", "--version"])

        if success:
            self.log_success(f"pipx is available: {stdout.strip()}")
            return True
        else:
            self.log_error(f"pipx not available: {stderr}")
            return False

    def install_package(self) -> bool:
        """Install the package using pipx."""
        self.log_info("Installing package with pipx...")

        # Get the project root directory
        project_root = Path(__file__).parent.parent

        success, stdout, stderr = self.run_command(["pipx", "install", str(project_root), "--force"], timeout=120)

        if success:
            self.log_success("Package installed successfully")
            if self.verbose:
                self.log(f"Installation output:\n{stdout}")
            return True
        else:
            self.log_error(f"Package installation failed: {stderr}")
            return False

    def test_cli_tools_in_path(self) -> bool:
        """Test that all CLI tools are available in PATH."""
        self.log_info("Testing CLI tools availability in PATH...")

        missing_tools = []
        cmd = "where" if sys.platform == "win32" else "which"

        for tool in self.EXPECTED_CLI_TOOLS:
            success, stdout, stderr = self.run_command([cmd, tool])
            if success:
                self.log_success(f"{tool} found at: {stdout.strip()}")
            else:
                missing_tools.append(tool)
                self.log_error(f"{tool} not found in PATH")

        return len(missing_tools) == 0

    def test_cli_help_commands(self) -> bool:
        """Test that all CLI tools can display help."""
        self.log_info("Testing CLI help commands...")

        failed_tools = []

        for tool in self.EXPECTED_CLI_TOOLS:
            success, stdout, stderr = self.run_command([tool, "--help"])

            if success and "usage:" in stdout.lower():
                self.log_success(f"{tool} help command works")
            else:
                failed_tools.append(tool)
                self.log_error(f"{tool} help command failed")

        return len(failed_tools) == 0

    def test_srt_parsing(self) -> bool:
        """Test basic SRT file parsing."""
        self.log_info("Testing SRT file parsing...")

        test_srt_content = """1
00:00:01,000 --> 00:00:03,000
Hello, world!

2
00:00:04,000 --> 00:00:06,000
This is a test subtitle.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".srt", delete=False) as f:
            f.write(test_srt_content)
            temp_srt_path = f.name

        try:
            success, stdout, stderr = self.run_command(["gpt-subtrans", temp_srt_path, "--maxlines", "0", "--debug"])

            output = stdout + stderr
            if "2 subtitles" in output.lower():
                self.log_success("SRT file parsing works correctly")
                return True
            else:
                self.log_error("SRT file parsing failed - subtitle count not detected")
                return False

        finally:
            with contextlib.suppress(OSError):
                os.unlink(temp_srt_path)

    def run_all_tests(self) -> bool:
        """Run all tests and return overall success."""
        self.log(f"{Colors.BOLD}Starting pipx installation tests...{Colors.END}")

        tests = [
            ("pipx availability", self.check_pipx_available),
            ("package installation", self.install_package),
            ("CLI tools in PATH", self.test_cli_tools_in_path),
            ("CLI help commands", self.test_cli_help_commands),
            ("SRT file parsing", self.test_srt_parsing),
        ]

        all_passed = True

        for test_name, test_func in tests:
            self.log(f"\n{Colors.BOLD}Running test: {test_name}{Colors.END}")

            if not test_func():
                all_passed = False
                self.log_error(f"Test failed: {test_name}")
            else:
                self.log_success(f"Test passed: {test_name}")

        # Summary
        self.log(f"\n{Colors.BOLD}Test Summary:{Colors.END}")
        if all_passed:
            self.log_success("All tests passed! ✨")
        else:
            self.log_error(f"Some tests failed. Errors:")
            for error in self.errors:
                self.log(f"  - {error}", Colors.RED)

        return all_passed


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Test pipx installation process locally")
    parser.add_argument("--quiet", "-q", action="store_true", help="Reduce output verbosity")

    args = parser.parse_args()

    tester = PipxInstallationTester(verbose=not args.quiet)
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
