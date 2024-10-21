import json
import os
from typing import Any, Dict, List, Tuple

import pytest
import rtoml

from joj3_config_generator.models import RepoConfig, TaskConfig
from tests.utils import safe_id


def read_convert_files(root: str) -> Tuple[RepoConfig, TaskConfig, Dict[str, Any]]:
    repo_toml_path = os.path.join(root, "repo.toml")
    task_toml_path = os.path.join(root, "task.toml")
    result_json_path = os.path.join(root, "task.json")
    with open(repo_toml_path) as repo_file:
        repo_toml = repo_file.read()
    with open(task_toml_path) as task_file:
        task_toml = task_file.read()
    with open(result_json_path) as result_file:
        expected_result: Dict[str, Any] = json.load(result_file)
    repo_obj = rtoml.loads(repo_toml)
    task_obj = rtoml.loads(task_toml)
    return RepoConfig(**repo_obj), TaskConfig(**task_obj), expected_result


def get_test_cases() -> List[Tuple[str, RepoConfig, TaskConfig, Dict[str, Any]]]:
    test_cases = []
    tests_dir = os.path.dirname(os.path.realpath(__file__))
    for dir_name in os.listdir(tests_dir):
        dir_path = os.path.join(tests_dir, dir_name)
        if os.path.isdir(dir_path) and dir_name != "__pycache__":
            repo, task, expected_result = read_convert_files(dir_path)
            test_cases.append((dir_name, repo, task, expected_result))
    return test_cases


@pytest.fixture(params=get_test_cases(), ids=safe_id)
def test_case(
    request: pytest.FixtureRequest,
) -> Tuple[RepoConfig, TaskConfig, Dict[str, Any]]:
    return request.param[1:]
