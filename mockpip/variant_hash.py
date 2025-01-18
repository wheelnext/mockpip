import logging
import re
from importlib.metadata import entry_points

from pip._internal.exceptions import InvalidWheelFilename

logger = logging.getLogger(__name__)


def get_variant_hash_from_wheel(filename: str):
    wheel_file_re = re.compile(
        r"""^(?P<namever>(?P<name>[^\s-]+?)-(?P<ver>[^\s-]*?))
        ((-(?P<build>\d[^-]*?))?(-\#(?P<variant_hash>[0-9a-fA-F]{8}))?-(?P<pyver>[^\s-]+?)
        -(?P<abi>[^\s-]+?)-(?P<plat>[^\s-]+?)\(-(?P<meta_ver>\d[^-]*?)(-(?P<whl_ver>\d[^-]*?).whl|\.dist-info)$""",
        re.VERBOSE,
    )

    wheel_info = wheel_file_re.match(filename)

    if not wheel_info:
        raise InvalidWheelFilename(f"{filename} is not a valid wheel filename.")

    return wheel_info.group("variant_hash")


def discover_and_run_plugins():
    logger.info("Discovering plugins...")
    plugins = entry_points().select(group="mockpip.plugins")
    for plugin in plugins:
        logger.info(f"Loading plugin: {plugin.name}")
        plugin_class = plugin.load()  # Dynamically load the plugin class
        plugin_instance = plugin_class()  # Instantiate the plugin
        plugin_instance.run()  # Call the `run` method of the plugin


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
