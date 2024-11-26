import shlex
import subprocess
import unittest

from parameterized import parameterized

import mockpip


class TestMockpipMain(unittest.TestCase):

    def run_command(self, command: str):
        return subprocess.run(
            shlex.split(f"mockpip {command}"),  # noqa: S603
            capture_output=True,
            text=True,
            check=False
        )

    @parameterized.expand(["-v", "--version"])
    def test_version_command(self, flag):
        """Test the version command to ensure it returns the correct version."""
        result = self.run_command(flag)
        assert f"mockpip version: {mockpip.__version__}" in result.stdout

    @parameterized.expand(["", "uninstall requests"])
    def test_invalid_command(self, command_str):
        result = self.run_command(command_str)
        assert result.stdout == ""
        assert "usage: mockpip [-h] [-v]" in result.stderr

    @parameterized.expand(["-h", "--help"])
    def test_help_command(self, flag):
        """Test the version command to ensure it returns the correct version."""
        result = self.run_command(flag)
        assert "usage: mockpip [-h] [-v]" in result.stdout
        assert "positional arguments:" in result.stdout
        assert "options:" in result.stdout
        assert "-h, --help" in result.stdout
        assert "-v, --version" in result.stdout


if __name__ == "__main__":
    unittest.main()
