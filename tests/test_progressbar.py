import sys
import time
import unittest
from io import StringIO

from parameterized import parameterized

from mockpip.progress_bar import fake_install_progress
from mockpip.progress_bar import progress_bar


class TestProgressBar(unittest.TestCase):
    def setUp(self):
        # Redirect stdout to capture progress bar output
        self.held_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.held_output

    def tearDown(self):
        # Restore stdout
        sys.stdout = self.original_stdout

    def test_progress_bar_halfway(self):
        # Test progress bar at 50%
        progress_bar(50, bar_length=20)
        output = self.held_output.getvalue()
        expected_output = "\r[==========          ] 50%"
        assert expected_output in output

    def test_progress_bar_complete(self):
        # Test progress bar at 100%
        progress_bar(100, bar_length=20)
        output = self.held_output.getvalue()
        expected_output = "\r[====================] 100%"
        assert expected_output in output

    def test_progress_bar_start(self):
        # Test progress bar at 0%
        progress_bar(0, bar_length=20)
        output = self.held_output.getvalue()
        expected_output = "\r[                    ] 0%"
        assert expected_output in output

    def test_progress_bar_small_steps(self):
        # Test a small step (25%)
        progress_bar(25, bar_length=20)
        output = self.held_output.getvalue()
        expected_output = "\r[=====               ] 25%"
        assert expected_output in output

    @parameterized.expand([1, 2, 5])
    def test_fake_progress_bar(self, duration):
        start_t = time.perf_counter()
        fake_install_progress(total_time=duration)
        total_t = time.perf_counter() - start_t

        assert total_t - duration <= 0.1  # noqa: PLR2004

        output = self.held_output.getvalue()
        expected_output = "\r[========================================] 100%"
        assert expected_output in output


if __name__ == "__main__":
    unittest.main()
