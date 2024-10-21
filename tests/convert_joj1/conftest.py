import json
import os
from typing import Any, Dict, List, Tuple

import pytest
import rtoml

from joj3_config_generator.models import JOJ1Config, TaskConfig
from tests.utils import safe_id


def read_convert_joj1_files(root: str) -> Tuple[JOJ1Config, TaskConfig, Dict[str, Any]]:
    task_yaml_path = os.path.join(root, "task.yaml")
    task_toml_path = os.path.join(root, "task.toml")
    expected_json_path = os.path.join(root, "task.json")
    with open(task_yaml_path) as repo_file:
        task_yaml = repo_file.read()
    with open(task_toml_path) as task_file:
        task_toml = task_file.read()
    with open(expected_json_path) as result_file:
        expected_result: Dict[str, Any] = json.load(result_file)
    joj1_obj = rtoml.loads(task_yaml)
    task_obj = rtoml.loads(task_toml)
    return JOJ1Config(**joj1_obj), TaskConfig(**task_obj), expected_result


def get_test_cases() -> List[Tuple[str, JOJ1Config, TaskConfig, Dict[str, Any]]]:
    test_cases = []
    tests_dir = os.path.dirname(os.path.realpath(__file__))
    for dir_name in os.listdir(tests_dir):
        dir_path = os.path.join(tests_dir, dir_name)
        if os.path.isdir(dir_path) and dir_name != "__pycache__":
            joj1, task, expected_result = read_convert_joj1_files(dir_path)
            test_cases.append((dir_name, joj1, task, expected_result))
    return test_cases


@pytest.fixture(params=get_test_cases(), ids=safe_id)
def test_case(
    request: pytest.FixtureRequest,
) -> Tuple[JOJ1Config, TaskConfig, Dict[str, Any]]:
    return request.param[1:]
