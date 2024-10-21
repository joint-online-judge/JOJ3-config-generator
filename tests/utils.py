from typing import Any


def safe_id(x: Any) -> str:
    if not x or not isinstance(x, (tuple, list)) or len(x) == 0:
        return "no_test_cases"
    return str(x[0])
