import json
import logging
import re
from collections.abc import Generator
from importlib.metadata import entry_points

from pip._internal.configuration import Configuration
from pip._internal.exceptions import ConfigurationError
from pip._internal.exceptions import InvalidWheelFilename
from pip._internal.exceptions import PipError
from variantlib.combination import get_combinations
from variantlib.config import ProviderConfig
from variantlib.meta import VariantDescription

logger = logging.getLogger(__name__)


def get_variant_hash_from_wheel(filename: str):
    wheel_file_re = re.compile(
        r"""^(?P<namever>(?P<name>[^\s-]+?)-(?P<ver>[^\s-]*?))
        ((-(?P<build>\d[^-]*?))?(~(?P<variant_hash>[0-9a-f]{8}))?
        -(?P<pyver>[^\s-]+?)-(?P<abi>[^\s-]+?)-(?P<plat>[^\s-]+?)
        \.whl|\.dist-info)$""",
        re.VERBOSE,
    )

    wheel_info = wheel_file_re.match(filename)

    if not wheel_info:
        raise InvalidWheelFilename(f"{filename} is not a valid wheel filename.")

    return wheel_info.group("variant_hash")


def read_provider_priority_from_pip_config() -> dict[str, int]:
    try:
        # Create a Configuration object and load all sources
        config = Configuration(isolated=False)
        config.load()  # Loads configuration from all applicable sources

        # Retrieve and return the merged configuration values
        # return {key: value for key, value in config.items()}

    except PipError:
        logging.exception("Error while reading PIP configuration")
        return {}

    try:
        provider_priority = config.get_value("variantlib.provider_priority")
        provider_priority = json.loads(provider_priority)  # str to list[str]
        if (
            provider_priority is None
            or not isinstance(provider_priority, list)
            or not all(isinstance(provider, str) for provider in provider_priority)
        ):
            return {}

        return {item: idx for idx, item in enumerate(provider_priority)}

    except ConfigurationError:
        # the user didn't set a special configuration
        logging.warning("No Variant Provider prioritization was set inside `pip.conf`.")
        return {}


def get_variant_hashes_by_priority(
    provider_priority_dict: dict[str:int] | None = None,
) -> Generator[VariantDescription]:
    logger.info("Discovering plugins...")
    plugins = entry_points().select(group="variantlib.plugins")

    if provider_priority_dict is not None:
        plugins = [
            plugin for plugin in plugins if plugin.name in provider_priority_dict
        ]

    else:
        # sorting providers in priority order:
        provider_priority_dict = read_provider_priority_from_pip_config()

    plugins = sorted(plugins, key=lambda plg: provider_priority_dict.get(plg.name, 1e6))

    provider_cfgs = []
    for plugin in plugins:
        try:
            logger.info(f"Loading plugin: {plugin.name} - v{plugin.dist.version}")
            plugin_class = plugin.load()  # Dynamically load the plugin class
            plugin_instance = plugin_class()  # Instantiate the plugin
            provider_cfg = plugin_instance.run()  # Call the `run` method of the plugi
            if not isinstance(provider_cfg, ProviderConfig):
                logging.error(
                    f"Provider: {plugin.name} returned an unexpected type: "
                    f"{type(provider_cfg)} - Expected: `ProviderConfig`. Ignoring..."
                )
                continue
            provider_cfgs.append(provider_cfg)
        except Exception:
            logging.exception("An unknown error happened - Ignoring plugin")

    yield from get_combinations(provider_cfgs) if provider_cfgs else []


def get_system_variant_preference_order():
    return [
        # fictional_hw :: architecture :: tars
        # fictional_hw :: compute_capability :: 8
        # fictional_hw :: compute_accuracy :: 8
        # fictional_hw :: humor :: 10
        "714c4f9e",
        # fictional_hw :: architecture :: HAL9000
        # fictional_hw :: compute_capability :: 6
        # fictional_hw :: humor :: 2
        "9f43005d",
        # gcc :: version :: 1.2.3
        "e4d430bf",
        # fictional_hw :: architecture :: mother
        # fictional_hw :: compute_capability :: 4
        "7d95521c",
        # fictional_hw :: architecture :: deepthought
        # fictional_hw :: compute_capability :: 10
        # fictional_hw :: compute_accuracy :: 10
        "411f372e",
    ]
