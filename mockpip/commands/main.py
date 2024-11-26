# #!/usr/bin/env python3

import argparse
from importlib.metadata import entry_points

import mockpip


def main():
    registered_commands = entry_points(group="mockpip.actions")

    parser = argparse.ArgumentParser(prog="mockpip")

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s version: {mockpip.__version__}",
    )

    parser.add_argument(
        "command",
        choices=registered_commands.names,
    )

    parser.add_argument(
        "args",
        help=argparse.SUPPRESS,
        nargs=argparse.REMAINDER,
    )

    args = parser.parse_args()

    main_fn = registered_commands[args.command].load()
    return main_fn(args.args)
