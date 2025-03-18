import json
from pathlib import Path

import tomli

from joj3_config_generator.generator import create_joj3_task_conf
from joj3_config_generator.models import answer


def load_case(case_name: str) -> None:
    root = Path(__file__).resolve().parent
    answers_json_path = root / case_name / "answers.json"
    task_toml_path = root / case_name / "task.toml"
    answers_dict = json.loads(answers_json_path.read_text())
    language = next(x for x in answer.LANGUAGES if str(x) == answers_dict["language"])
    language.set_stages(answers_dict["stages"])
    language.set_attribute(answers_dict["attribute"])
    answers = answer.Answers(name=answers_dict["name"], language=language)
    expected_result = tomli.loads(task_toml_path.read_text())
    result = create_joj3_task_conf(answers).model_dump(
        mode="json", by_alias=True, exclude_none=True, exclude_unset=True
    )
    print(result)
    print(expected_result)
    assert result == expected_result
