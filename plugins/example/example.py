import argparse

# As this help may be printed on consoles, consider to use multiline strings.
__help__ = """A demo plugin to demonstrate how plugins are added.
Provides some basic arguments to test.
"""

# Specify requirements for your plugin here.
# Leave empty if you don't need any requirements, don't remove the attribute.
__requirements__ = []


def execute(utils, debug=False):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hostaddress",
        action="store",
        dest="hostaddress",
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

    utils.build_output(state=utils.OutputState.OK, output="Example plugins returns OK")
