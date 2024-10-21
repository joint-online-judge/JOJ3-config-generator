from typing import Any, Dict, Tuple

from joj3_config_generator.models import JOJ1Config, TaskConfig


def test_convert_joj1(test_case: Tuple[JOJ1Config, TaskConfig, Dict[str, Any]]) -> None:
    joj1, task, expected_result = test_case
    result: Dict[str, Any] = {}
    assert result == expected_result
