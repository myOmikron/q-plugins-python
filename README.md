# Q Plugins

## Usage

- List all available plugins:
```bash
$ ./q_plugins.py --list-plugins
The following checks are registered:

example.example:
        A demo plugin to demonstrate how plugins are added
```

- Use plugin:

```bash
# After --plugin has to be a valid identifier to import the plugin. 
$ ./q_plugins.py --plugin example.example
usage: q_plugins.py [-h] --hostname HOSTNAME [--warning WARNING] [--critical CRITICAL]
q_plugins.py: error: the following arguments are required: --hostname
# The help message above originates from the example plugin.
```

- Install dependencies for plugin(s):

```bash
# If --install-requirements is invoked without any subsequent arguments, 
# dependencies for all plugins are installed
$ ./q_plugins.py --install-requirements
[... pip output ...]

# To only install the dependencies for specific plugins, state them after --install-requirements.
# Multiple arguments allowed
$ ./q_plugins.py --install-requirements example.example 
[... pip output ...] 
```

## Writing own plugins

A plugin can be placed under every path at the plugins directory. 

The plugin has to have a `.py` file extension. `__init__.py` are ignored at every level.  

### Example plugin

```python
import argparse

# As this help may be printed on consoles, consider to use multiline strings.
__help__ = """A demo plugin to demonstrate how plugins are added.
Provides some basic arguments to test.
"""

# Specify requirements for your plugin here.
# Leave empty if you don't need any requirements, don't remove the attribute.
__requirements__ = """

"""


def execute(utils, debug=False):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hostname",
        action="store",
        dest="hostname",
        required=True,
        help="Hostname of the target"
    )
    parser.add_argument(
        "--warning", "-w",
        action="store",
        dest="warning",
        type=int,
        default=80,
        help="Warning threshold in percent. Default: %(default)s"
    )
    parser.add_argument(
        "--critical", "-c",
        action="store",
        dest="critical",
        type=int,
        default=90,
        help="Critical threshold in percent. Default: %(default)s"
    )
    config = parser.parse_known_args()[0]
    
    # Write your own code here.
    # It is important to import packages, which aren't part of the standard lib, locally.

    utils.build_output(state=utils.OutputState.OK)
```