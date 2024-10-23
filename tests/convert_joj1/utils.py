import os
from typing import Any, Dict, Tuple

import rtoml
import yaml

from joj3_config_generator.convert import convert_joj1
from joj3_config_generator.models import joj1


def read_convert_joj1_files(case_name: str) -> Tuple[joj1.Config, Dict[str, Any]]:
    root = os.path.dirname(os.path.realpath(__file__))
    task_yaml_path = os.path.join(root, case_name, "task.yaml")
    with open(task_yaml_path) as f:
        task_yaml = f.read()
    task_toml_path = os.path.join(root, case_name, "task.toml")
    with open(task_toml_path) as f:
        task_toml = f.read()
    joj1_obj = yaml.safe_load(task_yaml)
    task_obj = rtoml.loads(task_toml)
    return joj1.Config(**joj1_obj), task_obj


def load_case(case_name: str) -> None:
    joj1, expected_result = read_convert_joj1_files(case_name)
    result = convert_joj1(joj1).model_dump(by_alias=True)
    assert result == expected_result
