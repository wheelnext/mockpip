# #!/usr/bin/env python3

import argparse
import logging
from urllib.parse import unquote

from mockpip.progress_bar import fake_install_progress
from mockpip.repository import list_candidates
from mockpip.variant_hash import discover_and_run_plugins
from mockpip.variant_hash import get_variant_hash_from_wheel

logger = logging.getLogger(__name__)


def install(args: list[str]) -> int:
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(prog="mockpip install")

    parser.add_argument(
        "package_name",  # Positional Argument
        type=str,
        help="Package name with optional version specifier (e.g., 'requests>=2.0.0').",
    )

    parser.add_argument(
        "-i",
        "--index-url",
        dest="index_url",
        type=str,
        default="https://pypi.org/simple",
        required=False,
        help="Python Package Repository URL.",
    )

    parsed_args = parser.parse_args(args)

    logger.info(
        f"Received install request for: `{parsed_args.package_name}` "
        f"from index: {parsed_args.index_url}."
    )

    pkg_candidates = list_candidates(
        package_name=parsed_args.package_name, index_url=parsed_args.index_url
    )

    logger.info("")
    for pkg in pkg_candidates:
        filename = unquote(pkg.filename)
        logger.info(f"Found: `{filename}`")
        variant_hash = get_variant_hash_from_wheel(filename)

    if not pkg_candidates:
        logger.error(f"No candidate package was found for `{parsed_args.package_name}`")
        return 1

    discover_and_run_plugins()

    selected_pkg = pkg_candidates[0]
    logger.info("")
    logger.info(f"Installing: {selected_pkg.filename} ...")
    fake_install_progress(total_time=2)
    logger.info("")

    logger.info(
        f"The package: `{parsed_args.package_name}` "
        f"(Version: `{selected_pkg.version}`) was installed with success ..."
    )

    return 0
