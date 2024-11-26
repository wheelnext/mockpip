import shlex
import subprocess
import unittest
from random import choice
from string import ascii_lowercase

from parameterized import parameterized


class TestMockpipMain(unittest.TestCase):

    def run_command(self, command: str):
        return subprocess.run(
            shlex.split(f"mockpip {command}"),  # noqa: S603
            capture_output=True,
            text=True,
            check=False
        )

    @parameterized.expand([
        "",
        "https://pypi.org/simple",
        "https://pypi.org/simple/",
        "https://test.pypi.org/simple",
        "https://test.pypi.org/simple/",
    ])
    def test_install_command_pypi(self, index_url):
        """Test the version command to ensure it returns the correct version."""
        index_flag = f"--index-url={index_url}" if index_url else ""

        if index_url == "":
            index_url = "https://pypi.org/simple"

        result = self.run_command(f"install requests {index_flag}")

        assert f"Received install request for: `requests` from index: {index_url}" in result.stdout  # noqa: E501
        assert f"Querying `{index_url.rstrip('/')}/requests/` for package `requests`" in result.stdout  # noqa: E501
        assert f"Successfully fetched package data from `{index_url.rstrip('/')}/requests/" in result.stdout  # noqa: E501
        assert "Found: requests" in result.stdout
        assert "Installing: requests" in result.stdout
        assert "[========================================] 100%" in result.stdout
        assert "was installed with success ..." in result.stdout

    def test_install_nonexisting_pkg(self):
        """Test the version command to ensure it returns the correct version."""
        pkg_name = "".join(choice(ascii_lowercase) for i in range(12))

        result = self.run_command(f"install {pkg_name}")

        assert f"Received install request for: `{pkg_name}` from index: https://pypi.org/simple" in result.stdout  # noqa: E501
        assert f"Querying `https://pypi.org/simple/{pkg_name}/` for package `{pkg_name}`" in result.stdout  # noqa: E501
        assert f"No candidate found for `{pkg_name}` from `https://pypi.org/simple/{pkg_name}/`" in result.stdout  # noqa: E501

        assert f"No candidate package was found for `{pkg_name}`" in result.stderr
        assert result.returncode != 0


if __name__ == "__main__":
    unittest.main()
