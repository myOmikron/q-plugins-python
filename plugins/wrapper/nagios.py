import argparse
import shlex
import subprocess

__help__ = """This is a wrapper around nagios plugins.
It formats the output as well as includes the nagios return code as parsed status code."""
__requirements__ = []


def execute(utils, debug=False):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--command",
        action="store",
        dest="command",
        required=True,
        help="Full command to execute"
    )
    parser.add_argument(
        "--timeout",
        action="store",
        type=int,
        dest="timeout",
        required=False,
        default=15,
        help="Timeout in seconds. Defaults to %(default)s"
    )
    config = parser.parse_known_args()[0]
    split_cmd = shlex.split(config.command)
    process = subprocess.Popen(split_cmd, stdout=subprocess.PIPE)
    stdout, _ = process.communicate(timeout=config.timeout)

    datasets = []
    split_out = stdout.decode("utf-8").split("|")
    text = split_out[0].strip()
    data = split_out[1].strip().split()
    for d in data:
        datasets.append(
            utils.build_dataset(
                name=d.split("'")[1],
                value=d.split("=")[1].split(";")[0]
            )
        )

    state = utils.OutputState.OK if process.returncode == 0 else utils.OutputState.WARN if process.returncode == 1 \
        else utils.OutputState.CRITICAL if process.returncode == 2 else utils.OutputState.UNKNOWN
    utils.build_output(
        state=state,
        output=text,
        datasets=datasets
    )
