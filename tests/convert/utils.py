import json
import os
from typing import Any, Dict, Tuple

import rtoml

from joj3_config_generator.convert import convert
from joj3_config_generator.models import repo, task


def read_convert_files(
    case_name: str,
) -> Tuple[repo.Config, task.Config, Dict[str, Any]]:
    root = os.path.dirname(os.path.realpath(__file__))
    repo_toml_path = os.path.join(root, case_name, "repo.toml")
    with open(repo_toml_path) as f:
        repo_toml = f.read()
    task_toml_path = os.path.join(root, case_name, "task.toml")
    with open(task_toml_path) as f:
        task_toml = f.read()
    result_json_path = os.path.join(root, case_name, "task.json")
    with open(result_json_path) as f:
        result: Dict[str, Any] = json.load(f)
    repo_obj = rtoml.loads(repo_toml)
    task_obj = rtoml.loads(task_toml)
    return repo.Config(**repo_obj), task.Config(**task_obj), result


def load_case(case_name: str) -> None:
    repo, task, expected_result = read_convert_files(case_name)
    result = convert(repo, task).model_dump(mode="json", by_alias=True)
    assert result == expected_result
