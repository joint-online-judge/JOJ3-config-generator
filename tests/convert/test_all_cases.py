from typing import Any

from joj3_config_generator.convert import convert
from joj3_config_generator.models import RepoConfig, TaskConfig


def test_convert(test_case: tuple[RepoConfig, TaskConfig, dict[str, Any]]) -> None:
    repo, task, expected_result = test_case
    result = convert(repo, task).model_dump(by_alias=True)
    assert result == expected_result
