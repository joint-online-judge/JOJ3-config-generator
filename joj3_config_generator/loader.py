from pathlib import Path
from typing import Tuple

import inquirer
import rtoml
import yaml

from joj3_config_generator.models import answer, joj1, repo, task


def load_joj3_task_toml_answers() -> answer.Answers:
    questions = [
        inquirer.Text(name="name", message="What's the task name?"),
        inquirer.Checkbox(
            "stages",
            message="What kind of stages do you need?",
            choices=[member.value for member in answer.StageEnum],
            default=[answer.StageEnum.COMPILATION],
        ),
    ]
    answers = inquirer.prompt(questions)
    return answer.Answers(**answers)


def load_joj1_yaml(yaml_path: Path) -> joj1.Config:
    joj1_obj = yaml.safe_load(yaml_path.read_text())
    return joj1.Config(**joj1_obj)


def load_joj3_toml(
    root_path: Path, repo_toml_path: Path, task_toml_path: Path
) -> Tuple[repo.Config, task.Config]:
    repo_obj = rtoml.loads(repo_toml_path.read_text())
    task_obj = rtoml.loads(task_toml_path.read_text())
    repo_conf = repo.Config(**repo_obj)
    repo_conf.root = root_path
    repo_conf.path = repo_toml_path.relative_to(root_path)
    task_conf = task.Config(**task_obj)
    task_conf.root = root_path
    task_conf.path = task_toml_path.relative_to(root_path)
    return repo_conf, task_conf
