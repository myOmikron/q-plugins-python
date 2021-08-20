import enum
import json


class OutputState(enum.Enum):
    OK = "ok"
    WARN = "warn"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


def build_output(
        *, state: OutputState
):
    """This method is used to create a valid output object

    :param state: State the output should have
    """
    print(json.dumps(
        {
            "state": state.value,
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
