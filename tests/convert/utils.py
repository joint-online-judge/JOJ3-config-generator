import json
from pathlib import Path
from typing import Any, Dict, Tuple

import rtoml

from joj3_config_generator.convert import convert
from joj3_config_generator.models import repo, task


def read_convert_files(
    case_name: str,
) -> Tuple[repo.Config, task.Config, Dict[str, Any]]:
    root = Path(__file__).resolve().parent / case_name
    repo_toml_path = root / "repo.toml"
    repo_toml = repo_toml_path.read_text() if repo_toml_path.exists() else ""
    task_toml_path = root / "task.toml"
    task_toml = task_toml_path.read_text() if task_toml_path.exists() else ""
    result = json.loads((root / "task.json").read_text())
    return (
        repo.Config(root=root, **rtoml.loads(repo_toml)),
        task.Config(root=root, **rtoml.loads(task_toml)),
        result,
    )


def load_case(case_name: str) -> None:
    repo, task, expected_result = read_convert_files(case_name)
    result = convert(repo, task).model_dump(
        mode="json", by_alias=True, exclude_none=True
    )
    assert result == expected_result
