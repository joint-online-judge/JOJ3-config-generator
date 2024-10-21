import os
from typing import Any, List

import pytest

from joj3_config_generator.models import RepoConfig, TaskConfig
from tests.convert.utils import read_convert_files


def get_test_cases() -> List[tuple[str, RepoConfig, TaskConfig, dict[str, Any]]]:
    test_cases = []
    tests_dir = os.path.dirname(os.path.realpath(__file__))
    for dir_name in os.listdir(tests_dir):
        dir_path = os.path.join(tests_dir, dir_name)
        if os.path.isdir(dir_path) and dir_name != "__pycache__":
            repo, task, expected_result = read_convert_files(dir_path)
            test_cases.append((dir_name, repo, task, expected_result))
    return test_cases


@pytest.fixture(params=get_test_cases(), ids=lambda x: x[0])
def test_case(
    request: pytest.FixtureRequest,
) -> tuple[RepoConfig, TaskConfig, dict[str, Any]]:
    return request.param[1:]  # return repo, task, expected_result
