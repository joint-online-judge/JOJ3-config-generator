import json
import os
from typing import Any

import rtoml

from joj3_config_generator.models import RepoConfig, TaskConfig


def read_convert_files(root: str) -> tuple[RepoConfig, TaskConfig, dict[str, Any]]:
    repo_toml_path = os.path.join(root, "repo.toml")
    task_toml_path = os.path.join(root, "task.toml")
    result_json_path = os.path.join(root, "task.json")
    with open(repo_toml_path) as repo_file:
        repo_toml = repo_file.read()
    with open(task_toml_path) as task_file:
        task_toml = task_file.read()
    with open(result_json_path) as result_file:
        expected_result: dict[str, Any] = json.load(result_file)
    repo_obj = rtoml.loads(repo_toml)
    task_obj = rtoml.loads(task_toml)
    return RepoConfig(**repo_obj), TaskConfig(**task_obj), expected_result
