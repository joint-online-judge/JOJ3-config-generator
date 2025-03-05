from pathlib import Path

import rtoml

from joj3_config_generator.convert import convert_joj1
from joj3_config_generator.load import load_joj1_yaml


def load_case(case_name: str) -> None:
    root = Path(__file__).resolve().parent
    task_yaml_path = root / case_name / "task.yaml"
    task_yaml = load_joj1_yaml(task_yaml_path)
    task_toml_path = root / case_name / "task.toml"
    task_toml = task_toml_path.read_text()
    expected_result = rtoml.loads(task_toml)
    result = convert_joj1(task_yaml).model_dump(
        mode="json", by_alias=True, exclude_none=True
    )
    assert result == expected_result
