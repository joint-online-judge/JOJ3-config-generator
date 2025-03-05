from pathlib import Path
from typing import Dict, Tuple

import inquirer
import rtoml
import yaml

from joj3_config_generator.models import joj1, repo, task


def load_joj3_toml_answers() -> Dict[str, str]:
    questions = [
        inquirer.List(
            "size",
            message="What size do you need?",
            choices=["Jumbo", "Large", "Standard", "Medium", "Small", "Micro"],
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers


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
