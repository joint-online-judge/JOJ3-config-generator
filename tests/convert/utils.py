import difflib
import json
from pathlib import Path

from joj3_config_generator.generator import convert_joj3_conf
from joj3_config_generator.loader import load_joj3_toml


def load_case(case_name: str) -> None:
    root = Path(__file__).resolve().parent
    repo_toml_path = root / case_name / "repo.toml"
    task_toml_path = root / case_name / "task.toml"
    repo_conf, task_conf = load_joj3_toml(root, repo_toml_path, task_toml_path)
    result_json_path = root / case_name / "task.json"
    expected_result = json.loads(result_json_path.read_text())
    result = convert_joj3_conf(repo_conf, task_conf).model_dump(
        mode="json", by_alias=True, exclude_none=True
    )
    if result != expected_result:
        result_str = json.dumps(result, indent=2, ensure_ascii=False).splitlines()
        expected_str = json.dumps(
            expected_result, indent=2, ensure_ascii=False
        ).splitlines()
        diff = "\n".join(difflib.ndiff(expected_str, result_str))
        print(f"Test case '{case_name}' failed!\nDifferences:\n{diff}")
    assert result == expected_result
