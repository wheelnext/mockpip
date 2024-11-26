import logging
import re
import typing
from urllib.parse import parse_qs
from urllib.parse import urlparse

import requests
from packaging.version import Version

logger = logging.getLogger(__name__)


class PackageCandidate(typing.NamedTuple):
    filename: str
    version: Version
    extension: str        # One of [`tar.gz`, `whl`]
    filehash: str | None  # optional sha256 value


def list_candidates(package_name, index_url):
    """
    Query a package index for available versions.
    Args:
        package_name (str): The name of the package to query.
        index_url (str): The URL of the package index. Defaults to PyPI's Simple Index.
    Returns:
        list[dict]: List of available versions with metadata.
    """
    package_url = f"{index_url.rstrip('/')}/{package_name}/"
    logger.info(f"Querying `{package_url}` for package `{package_name}`")

    try:
        response = requests.get(package_url, timeout=10)

        match response.status_code:

            case 200:
                logger.info(f"Successfully fetched package data from `{package_url}`")
                return parse_versions_from_index(response.text)

            case 404:
                logger.info(
                    f"No candidate found for `{package_name}` from `{package_url}`"
                )

            case _:
                logger.error(
                    f"Failed to fetch package data from {package_url} "
                    f"(HTTP {response.status_code})"
                )

    except requests.exceptions.Timeout:
        logger.error(f"Timeout while accessing: `{package_url}` ...")  # noqa: TRY400

    except requests.RequestException as e:
        logger.error(f"Error connecting to {package_url}: {e}")  # noqa: TRY400

    return []


def extract_href_links(html_content):
    """
    Extracts all href links from the given HTML content.

    Args:
        html_content (str): The HTML content to parse.

    Returns:
        list[str]: A list of href URLs found in the HTML content.
    """
    # Regular expression to match href attributes
    href_pattern = r'href=["\'](.*?)["\']'
    return re.findall(href_pattern, html_content)


def extract_details_from_url(url):
    """
    Extracts filename, version, extension, and file hash from a given URL.

    Args:
        url (str): The URL to parse.

    Returns:
        dict: A dictionary with extracted components.
    """
    # Regex pattern to match the required components
    pattern = (
        r"(?P<filename>"               # Named group 'filename' to capture the entire filename               # noqa: E501
        r"([a-zA-Z0-9_\-]+)"           # Matches the base project name
        r"-"                           # Matches the separator before the version
        r"(?P<version>\d+\.\d+\.\d+)"  # Named group 'version' to capture semantic version (e.g., '2.32.3')  # noqa: E501
        r"([^\s]*?)"                   # Optionally matches additional tags (e.g., '-py3-none-any')          # noqa: E501
        r"\."                          # Matches the dot before the file extension
        r"(?P<extension>"              # Named group 'extension' to capture file extensions                  # noqa: E501
        r"tar\.gz|"                    # Matches '.tar.gz'
        r"whl"                         # Matches '.whl'
        r"))"
    )

    # Parse the URL
    parsed_url = urlparse(url)
    filename_match = re.search(pattern, parsed_url.path)

    if not filename_match:
        raise ValueError("Improper URL - Does not match a known python package.")

    # Extract hash from the fragment if present
    query_hash = parse_qs(parsed_url.fragment)
    filehash = query_hash.get("sha256", [None])[0]

    if filehash is not None:
        sha256_pattern = r"^[a-fA-F0-9]{64}$"
        # if the hash is not a valid sha256 value, drop the value and ignore
        filehash = filehash if re.match(sha256_pattern, filehash) else None

    return PackageCandidate(
        filename = filename_match.group("filename"),
        version = Version(filename_match.group("version")),
        extension = filename_match.group("extension"),
        filehash = filehash,
    )



def parse_versions_from_index(html_content):
    """
    Parse versions and file types of a package from the given HTML content.

    Args:
        html_content (str): The HTML content of the index page.

    Returns:
        list[dict]: A list of dictionaries with 'version' and 'file' keys.
    """

    parsed_versions = []
    for href in extract_href_links(html_content):
        try:
            parsed_versions.append(extract_details_from_url(href))
        except ValueError:
            continue

    filetype_order = {
        "tar.gz": 0,  # sdist
        "whl": 1,     # wheel
    }

    return sorted(
        parsed_versions,
        key=lambda item: (item.version, filetype_order[item.extension]),
        reverse=True
    )
