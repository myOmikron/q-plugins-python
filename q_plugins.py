#!/usr/bin/env python3
import argparse
import importlib
import os
import re
import traceback
from collections import ChainMap


def _check_plugin(plugin):
    if not callable(getattr(plugin, "execute", None)):
        raise AttributeError("Function execute is missing")
    if getattr(plugin, "__requirements__", None) is None:
        raise AttributeError("Parameter __requirements__ is missing")
    if getattr(plugin, "__help__", None) is None:
        raise AttributeError("Parameter __help__ is missing")


def _traverse_plugin_tree():
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_list = {}
    for dir_path, dir_names, files in os.walk(os.path.join(plugin_dir, "plugins")):
        for file in files:
            if file != "__init__.py" and file.endswith("py"):
                import_path = os.path.relpath(
                    os.path.join(
                        dir_path, file[:-3]
                    ),
                    os.path.join(
                        plugin_dir, "plugins"
                    )
                ).replace("/", ".")
                try:
                    imported = importlib.import_module(f"plugins.{import_path}")
                except ModuleNotFoundError:
                    continue
                try:
                    _check_plugin(imported)
                    plugin_list[import_path] = imported
                except AttributeError:
                    continue
    return plugin_list


def list_plugins(config):
    print("The following plugins are registered:\n")
    for path, plugin in _traverse_plugin_tree().items():
        help_formatted = "".join([f"\t{x}\n" for x in plugin.__help__.split("\n")])
        print(f"{path}:\n{help_formatted.rstrip()}")
    exit(0)


def execute_plugin(config):
    pattern = re.compile(r"^(\w+\.)*\w+$")
    if not pattern.fullmatch(config.plugin):
        print("Plugin descriptor is not valid.")
        exit(3)
    try:
        imported = importlib.import_module(f"plugins.{config.plugin}")
    except ModuleNotFoundError:
        print("Module was not found")
        exit(3)
    try:
        _check_plugin(imported)
    except AttributeError:
        print("Plugin is missing required attributes or functions")
        exit(3)
    utils = importlib.import_module("utils")
    try:
        try:
            imported.execute(utils)
        except ModuleNotFoundError as err:
            print("There are missing dependencies for this module. The module lists the following dependencies:")
            print("".join([f"\t- {x}\n" for x in imported.__requirements__.split("\n") if x]).rstrip())
            exit(3)
    except Exception as err:
        utils.build_output(
            state=utils.OutputState.UNKNOWN,
            output="".join(traceback.format_tb(err.__traceback__))
        )


def install_requirements(config):
    requirement_list = []
    all_plugins = _traverse_plugin_tree()
    search_plugins = all_plugins if not config.install_requirements else dict(ChainMap(*[
        {x: all_plugins[x]} for x in all_plugins if x in config.install_requirements
    ]))
    for plugin in search_plugins.values():
        for line in plugin.__requirements__.split("\n"):
            if line and line not in requirement_list:
                requirement_list.append(line)
    if not requirement_list:
        print("There are no requirements listed")
        exit(0)
    os.system(f"/usr/bin/env python3 -m pip install -U {' '.join(requirement_list)} {'--user' if config.user else ''}")
    exit(0)


def main(config):
    if config.list_plugins:
        list_plugins(config)
    if config.plugin:
        execute_plugin(config)
    if config.install_requirements is not None:
        install_requirements(config)


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
    first_level_group.add_argument(
        "--install-requirements",
        nargs="*",
        action="store",
        dest="install_requirements",
        help="List plugins to install the requirements for. \
              If None are listed, requirements for all plugins are installed"
    )
    parser.add_argument(
        "--install-user",
        action="store_true",
        dest="user",
        help="Specify if you want to install with the --user option with pip"
    )
    c = parser.parse_known_args()[0]
    main(c)
