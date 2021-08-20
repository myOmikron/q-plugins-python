#!/usr/bin/env python3
import argparse
import importlib
import os
import re

plugin_dir = os.path.dirname(os.path.abspath(__file__))


def list_plugins(config):
    print("The following plugins are registered:\n")
    for dir_path, dir_names, files in os.walk(os.path.join(plugin_dir, "plugins")):
        for file in files:
            if not file.startswith("__init__") and not file.endswith("pyc"):
                import_path = os.path.relpath(
                    os.path.join(
                        dir_path, file.rstrip(".py")
                    ),
                    os.path.join(
                        plugin_dir, "plugins"
                    )
                ).replace("/", ".")
                try:
                    imported = importlib.import_module(f"plugins.{import_path}")
                    print(f"{import_path}:")
                    print(f"\t{imported.__help__}")
                except ModuleNotFoundError or AttributeError:
                    continue
    exit(0)


def execute_plugin(config):
    pattern = re.compile(r"(\w\.)*\w")
    if not pattern.match(config.plugin):
        print("Plugin descriptor is not valid.")
        exit(1)
    try:
        imported = importlib.import_module(f"plugins.{config.plugin}")
        imported.execute()
    except ModuleNotFoundError or AttributeError:
        print("Module is not available or is corrupt")
        exit(1)


def main(config):
    if config.list_plugins:
        list_plugins(config)
    execute_plugin(config)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    first_level_group = parser.add_mutually_exclusive_group(required=True)
    first_level_group.add_argument(
        "--list-plugins",
        action="store_true",
        dest="list_plugins",
        help="Show available plugins"
    )
    first_level_group.add_argument(
        "--plugin",
        dest="plugin",
        help="Plugin to execute"
    )
    c = parser.parse_known_args()
    main(c[0])
