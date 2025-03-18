from pathlib import Path

import tomli

from joj3_config_generator.generator import convert_joj1_conf
from joj3_config_generator.loader import load_joj1_yaml


def load_case(case_name: str) -> None:
    root = Path(__file__).resolve().parent
    task_yaml_path = root / case_name / "task.yaml"
    task_yaml = load_joj1_yaml(task_yaml_path)
    task_toml_path = root / case_name / "task.toml"
    task_toml = task_toml_path.read_text()
    expected_result = tomli.loads(task_toml)
    result = convert_joj1_conf(task_yaml).model_dump(
        mode="json", by_alias=True, exclude_none=True
    )
    assert result == expected_result
