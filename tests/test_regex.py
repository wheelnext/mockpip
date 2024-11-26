import unittest

import pytest
from packaging.version import Version
from parameterized import parameterized

from mockpip.repository import PackageCandidate
from mockpip.repository import extract_details_from_url


class TestExtractDetailsFromURL(unittest.TestCase):
    @parameterized.expand([
        # Valid cases with valid hash
        (
            "https://files.pythonhosted.org/packages/f9/9b/335f9764261e915ed497fcdeb11df5dfd6f7bf257d4a6a2a686d80da4d54/requests-2.32.3-py3-none-any.whl#sha256=70761cfe03c773ceb22aa2f671b4757976145175cdfca038c02654d061d6dcc6",
            {
                "filename": "requests-2.32.3-py3-none-any.whl",
                "version": Version("2.32.3"),
                "extension": "whl",
                "filehash": "70761cfe03c773ceb22aa2f671b4757976145175cdfca038c02654d061d6dcc6",  # noqa: E501
            },
        ),
        (
            "https://files.pythonhosted.org/packages/63/70/2bf7780ad2d390a8d301ad0b550f1581eadbd9a20f896afe06353c2a2913/requests-2.32.3.tar.gz#sha256=55365417734eb18255590a9ff9eb97e9e1da868d4ccd6402399eaf68af20a760",
            {
                "filename": "requests-2.32.3.tar.gz",
                "version": Version("2.32.3"),
                "extension": "tar.gz",
                "filehash": "55365417734eb18255590a9ff9eb97e9e1da868d4ccd6402399eaf68af20a760",  # noqa: E501
            },
        ),
        # Valid cases without hash
        (
            "https://files.pythonhosted.org/packages/f9/9b/335f9764261e915ed497fcdeb11df5dfd6f7bf257d4a6a2a686d80da4d54/requests-2.32.3-py3-none-any.whl",
            {
                "filename": "requests-2.32.3-py3-none-any.whl",
                "version": Version("2.32.3"),
                "extension": "whl",
                "filehash": None,
            },
        ),
        (
            "https://files.pythonhosted.org/packages/63/70/2bf7780ad2d390a8d301ad0b550f1581eadbd9a20f896afe06353c2a2913/requests-2.32.3.tar.gz",
            {
                "filename": "requests-2.32.3.tar.gz",
                "version": Version("2.32.3"),
                "extension": "tar.gz",
                "filehash": None,
            },
        ),
        # Valid cases with invalid hash
        (
            "https://files.pythonhosted.org/packages/edge-case/requests-1.0.0.tar.gz#sha256=invalidhash",
            {
                "filename": "requests-1.0.0.tar.gz",
                "version": Version("1.0.0"),
                "extension": "tar.gz",
                "filehash": None,
            },
        ),
        (
            "https://files.pythonhosted.org/packages/f9/9b/335f9764261e915ed497fcdeb11df5dfd6f7bf257d4a6a2a686d80da4d54/requests-2.32.3-py3-none-any.whl#sha256=invalidhash",
            {
                "filename": "requests-2.32.3-py3-none-any.whl",
                "version": Version("2.32.3"),
                "extension": "whl",
                "filehash": None,
            },
        ),
    ])
    def test_extract_details_from_url(self, test_url, expected_result):
        """Test the extract_details_from_url function."""
        result = extract_details_from_url(test_url)
        assert result == PackageCandidate(**expected_result)

    @parameterized.expand([
        "",
        "not a url",
        "ftp://invalid.url/does-not-apply",
        "/local/path/to/file.tar.gz",
        "https://example.com/no_version_or_hash",
        "https://example.com/packages/malformed-url.whl#sha256="
        "https://files.pythonhosted.org/packages/edge-case/filename-.tar.gz"
    ])
    def test_invalid_extract_details_from_url(self, test_url):
        with pytest.raises(ValueError, match="Does not match a known python package."):
            _ = extract_details_from_url(test_url)


if __name__ == "__main__":
    unittest.main()
