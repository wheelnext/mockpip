import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

import requests
from parameterized import parameterized

from mockpip.repository import list_candidates


class TestListCandidatesFromIndex(unittest.TestCase):

    @parameterized.expand([
        ("https://pypi.org/simple",),
        ("https://pypi.org/simple/",),
        ("https://test.pypi.org/simple",),
        ("https://test.pypi.org/simple/",),
    ])
    def test_list_candidates_found(self, index_url):
        candidates = list_candidates("example", index_url=index_url)
        assert len(candidates) >= 1

    def test_list_candidates_not_found(self):
        candidates = list_candidates("nonexistent", index_url="https://pypi.org/simple")
        assert candidates == []

    @parameterized.expand([404, 500])
    @patch("requests.get")
    def test_get_with_bad_status_code(self, status_code: int, mock_get):
        """Simulate an HTTP error response."""

        # Create a mock response object
        mock_response = MagicMock()
        mock_response.status_code = status_code

        # Assign the mock response to requests.get
        mock_get.return_value = mock_response

        # Call the function and verify behavior
        candidates = list_candidates("example", index_url="https://pypi.org/simple")
        assert len(candidates) == 0

    @parameterized.expand([
        requests.RequestException(),
        requests.exceptions.Timeout("Request timed out")
    ])
    @patch("requests.get")
    def test_get_raises_error(self, exception: OSError, mock_get):
        """Simulate an `requests` error."""

        # Assign the mock response to requests.get
        mock_get.side_effect = exception

        # Call the function and verify behavior
        candidates = list_candidates("example", index_url="https://pypi.org/simple")
        assert len(candidates) == 0


if __name__ == "__main__":
    unittest.main()

