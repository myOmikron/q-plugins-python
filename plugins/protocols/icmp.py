import argparse

__help__ = "A plugin to check a host with ICMP, broadly known as ping"
__requirements__ = ["icmplib"]


def send_ping(utils, debug, config):
    from icmplib import ping
    result = ping(
        config.hostaddress,
        privileged=False,
        count=config.count,
        source=config.source,
        interval=config.interval,
        family=None if not config.ipv4 and not config.ipv6 else 4 if config.ipv4 else 6
    )
    if debug:
        print(result)

    datasets = [
        utils.build_dataset(
            name="packetloss", value=int(result.packet_loss * 100)
        ),
        utils.build_dataset(
            name="min_rtt", value=result.min_rtt
        ),
        utils.build_dataset(
            name="avg_rtt", value=result.avg_rtt
        ),
        utils.build_dataset(
            name="max_rtt", value=result.max_rtt
        ),
        utils.build_dataset(
            name="jitter", value=result.jitter
        )
    ]

    if not result.is_alive:
        utils.build_output(
            state=utils.OutputState.CRITICAL,
            output=f"{config.hostaddress} is not reachable",
            datasets=datasets
        )

    if int(result.packet_loss*100) >= config.critical_packetloss:
        utils.build_output(
            state=utils.OutputState.CRITICAL,
            output=f"Packetloss critical: {int(result.packet_loss*100)}",
            datasets=datasets
        )
    elif int(result.packet_loss*100) >= config.warning_packetloss:
        utils.build_output(
            state=utils.OutputState.WARN,
            output=f"Packetloss warn: {int(result.packet_loss*100)}",
            datasets=datasets
        )

    if result.avg_rtt >= config.critical_rta:
        utils.build_output(
            state=utils.OutputState.CRITICAL,
            output=f"RTA critical: {result.avg_rtt} ms",
            datasets=datasets
        )
    elif result.avg_rtt >= config.warning_rta:
        utils.build_output(
            state=utils.OutputState.WARN,
            output=f"RTA warn: {result.avg_rtt} ms",
            datasets=datasets
        )

    utils.build_output(
        state=utils.OutputState.OK,
        output=f"Ping OK, RTA: {result.avg_rtt} ms",
        datasets=datasets
    )


def execute(utils, debug):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hostaddress", "-H",
        action="store",
        dest="hostaddress",
        required=True,
        help="Hostname, IP or domain of the target"
    )
    parser.add_argument(
        "--count",
        action="store",
        dest="count",
        type=int,
        default=3,
        help="Number of pings to perform. (default: %(default)s)"
    )
    parser.add_argument(
        "--source",
        action="store",
        dest="source",
        help="Source IP address"
    )
    parser.add_argument(
        "--timeout",
        action="store",
        dest="timeout",
        type=float,
        default=1,
        help="The maximum waiting time for receiving a reply in seconds. (default: %(default)s)"
    )
    parser.add_argument(
        "--interval",
        action="store",
        dest="interval",
        type=float,
        default=0.5,
        help="The interval in seconds between sending each packet. (default: %(default)s)"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-4", "--4",
        action="store_true",
        dest="ipv4",
        help="Specify if you only want to use ipv4"
    )
    group.add_argument(
        "-6", "--6",
        action="store_true",
        dest="ipv6",
        help="Specify if you want only to use ipv6."
    )
    parser.add_argument(
        "--warning-packetloss",
        action="store",
        dest="warning_packetloss",
        type=int,
        default=34,
        help="Waning threshold in percent of lost packages. (default: %(default)s)"
    )
    parser.add_argument(
        "--critical-packetloss",
        action="store",
        dest="critical_packetloss",
        type=int,
        default=67,
        help="Critical threshold in percent of lost packages. (default: %(default)s)"
    )
    parser.add_argument(
        "--warning-rta",
        action="store",
        dest="warning_rta",
        type=int,
        default=150,
        help="Warning threshold of the round-travel-average in ms. (default: %(default)s)"
    )
    parser.add_argument(
        "--critical-rta",
        action="store",
        dest="critical_rta",
        type=int,
        default=500,
        help="Critical threshold of the round-travel-average in ms. (default: %(default)s)"
    )
    c = parser.parse_known_args()[0]
    send_ping(utils, debug, c)
