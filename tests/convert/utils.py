import json
from pathlib import Path

from joj3_config_generator.convert import convert
from joj3_config_generator.load import load_joj3_toml


def load_case(case_name: str) -> None:
    root = Path(__file__).resolve().parent
    repo_toml_path = root / case_name / "repo.toml"
    task_toml_path = root / case_name / "task.toml"
    repo_conf, task_conf = load_joj3_toml(root, repo_toml_path, task_toml_path)
    result_json_path = root / case_name / "task.json"
    expected_result = json.loads(result_json_path.read_text())
    result = convert(repo_conf, task_conf).model_dump(
        mode="json", by_alias=True, exclude_none=True
    )
    assert result == expected_result
