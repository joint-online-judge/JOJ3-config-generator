import json
from pathlib import Path

import rtoml

from joj3_config_generator.create import create
from joj3_config_generator.models import answer


def load_case(case_name: str) -> None:
    root = Path(__file__).resolve().parent
    answers_json_path = root / case_name / "answers.json"
    task_toml_path = root / case_name / "task.toml"
    answers = answer.Answers(**json.loads(answers_json_path.read_text()))
    print(answers)
    expected_result = rtoml.loads(task_toml_path.read_text())
    result = create(answers).model_dump(
        mode="json", by_alias=True, exclude_none=True, exclude_unset=True
    )
    print(result)
    print(expected_result)
    assert result == expected_result
