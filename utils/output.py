import enum
import json
import typing


class OutputState(enum.Enum):
    OK = "ok"
    WARN = "warn"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


def build_dataset(
    *, name, value
):
    """This method is used to build a dataset

    :param name: Name of the dataset
    :param value: Value of the dataset
    :return: dict
    """
    return {"name": name, "value": value}


def build_output(
        *, state: OutputState, output: str, datasets: typing.List[typing.Dict] = None
):
    """This method is used to print a valid output object

    :param state: State the output should have
    :param output: Output of the check
    :param datasets:
    """
    print(json.dumps(
        {
            "state": state.value,
            "output": output,
            "datasets": datasets if datasets else []
        }
    ))
    if state == OutputState.OK:
        exit(0)
    elif state == OutputState.WARN:
        exit(1)
    elif state == OutputState.CRITICAL:
        exit(2)
    else:
        exit(3)
