# #!/usr/bin/env python3

import argparse
import logging
import os
import re
from urllib.parse import unquote

from variantlib import VARIANT_HASH_LEN

from mockpip.progress_bar import fake_install_progress
from mockpip.repository import list_candidates
from mockpip.variant_hash import get_variant_hash_from_wheel
from mockpip.variant_hash import get_variant_hashes_by_priority

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

    parser.add_argument(
        "-p",
        "--variant_provider",
        dest="variant_providers",
        action="append",
        help="Variant Providers in order of priority",
    )

    parser.add_argument(
        "--no_variants",
        action="store_true",
        default=False,
        help="disables variant support",
    )

    parsed_args = parser.parse_args(args)

    logger.info(
        f"Received install request for: `{parsed_args.package_name}` "
        f"from index: {parsed_args.index_url}."
    )

    pkg_candidates = list_candidates(
        package_name=parsed_args.package_name, index_url=parsed_args.index_url
    )

    if not pkg_candidates:
        logger.error(f"No candidate package was found for `{parsed_args.package_name}`")
        return 1

    logger.info("")  # visual spacing

    pkg_candidate_dict_by_vhash = {}
    for pkg in pkg_candidates:
        filename = unquote(pkg.filename)
        logger.info(f"Found: `{filename}`")
        variant_hash = get_variant_hash_from_wheel(filename)
        pkg_candidate_dict_by_vhash[variant_hash] = pkg

    logger.info("")  # visual spacing

    if not parsed_args.no_variants:
        variant_providers = parsed_args.variant_providers
        variant_providers = (
            {name: idx for idx, name in enumerate(variant_providers)}
            if variant_providers is not None
            else None
        )

        if (
            forced_vhash := os.environ.get("PIP_FORCE_INSTALL_VARIANT_HASH", None)
        ) is None:
            selected_pkg = None
            for vid, vdesc in enumerate(
                get_variant_hashes_by_priority(variant_providers)
            ):
                vhash = vdesc.hexdigest
                selected_pkg = pkg_candidate_dict_by_vhash.get(vhash)

                logger.info(
                    f"[Variant: {vid:04d}] `{vhash}`: "
                    f"{'FOUND' if selected_pkg is not None else 'NOT FOUND'} ..."
                )

                if selected_pkg is not None:
                    logger.info("Selected Variant:")
                    from pprint import pprint

                    pprint(vdesc.serialize())
                    break

            else:
                # The one package without variant information
                selected_pkg = pkg_candidate_dict_by_vhash[None]

        elif (
            re.match(rf"^[a-fA-F0-9]{{{VARIANT_HASH_LEN}}}$", forced_vhash) is not None
        ):
            logger.info(f"Forced installation of variant: {forced_vhash}")
            selected_pkg = pkg_candidate_dict_by_vhash.get(forced_vhash)

        else:
            logger.info("Forced installation to ignore variant ...")
            selected_pkg = pkg_candidate_dict_by_vhash.get(None)

    else:
        logger.info("Forced installation to ignore variant ...")
        selected_pkg = pkg_candidate_dict_by_vhash.get(None)

    if selected_pkg is not None:
        logger.info("")
        logger.info(f"Installing: {selected_pkg.filename} ...")
        fake_install_progress(total_time=2)
        logger.info("")

        logger.info(
            f"The package: `{parsed_args.package_name}` "
            f"(Version: `{selected_pkg.version}`) was installed with success ..."
        )

    else:
        logger.error("Impossible to find a suitable package to install ...")

    return 0
