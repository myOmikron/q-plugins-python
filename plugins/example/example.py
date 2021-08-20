import argparse

__help__ = """A demo plugin to demonstrate how plugins are added"""


def execute():
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
