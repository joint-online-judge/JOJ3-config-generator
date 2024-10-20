import json
import os
from typing import Any

import rtoml

from joj3_config_generator.models import Repo, Task


def read_convert_files(root: str) -> tuple[Repo, Task, dict[str, Any]]:
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
    return Repo(**repo_obj), Task(**task_obj), expected_result
