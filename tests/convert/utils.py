import json
import os
from typing import Any, Dict, Tuple

import rtoml

from joj3_config_generator.models import repo, task


def read_convert_files(
    case_name: str,
) -> Tuple[repo.Config, task.Config, Dict[str, Any]]:
    root = os.path.dirname(os.path.realpath(__file__))
    repo_toml_path = os.path.join(root, case_name, "repo.toml")
    task_toml_path = os.path.join(root, case_name, "task.toml")
    result_json_path = os.path.join(root, case_name, "task.json")
    with open(repo_toml_path) as repo_file:
        repo_toml = repo_file.read()
    with open(task_toml_path) as task_file:
        task_toml = task_file.read()
    with open(result_json_path) as result_file:
        result: Dict[str, Any] = json.load(result_file)
    repo_obj = rtoml.loads(repo_toml)
    task_obj = rtoml.loads(task_toml)
    return repo.Config(**repo_obj), task.Config(**task_obj), result
