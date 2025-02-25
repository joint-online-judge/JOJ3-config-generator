from pathlib import Path
from typing import Any, Dict, Tuple

import rtoml
import yaml

from joj3_config_generator.convert import convert_joj1
from joj3_config_generator.models import joj1


def read_convert_joj1_files(case_name: str) -> Tuple[joj1.Config, Dict[str, Any]]:
    root = Path(__file__).resolve().parent
    task_yaml_path = root / case_name / "task.yaml"
    task_yaml = task_yaml_path.read_text()
    task_toml_path = root / case_name / "task.toml"
    task_toml = task_toml_path.read_text()
    return joj1.Config(**yaml.safe_load(task_yaml)), rtoml.loads(task_toml)


def load_case(case_name: str) -> None:
    joj1, expected_result = read_convert_joj1_files(case_name)
    result = convert_joj1(joj1).model_dump(by_alias=True, exclude_none=True)
    assert result == expected_result
