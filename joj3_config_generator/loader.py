from pathlib import Path
from typing import Tuple, Type, cast

import inquirer
import tomli
import yaml

from joj3_config_generator.models import answer, joj1, repo, task


def load_joj3_task_toml_answers() -> answer.Answers:
    name = inquirer.text("What's the task name?", default="hw0")
    language = inquirer.list_input(
        "What's the language?", choices=[(cls.name, cls) for cls in answer.LANGUAGES]
    )
    language = cast(Type[answer.LanguageInterface], language)
    if inquirer.confirm("Load content from templates?", default=True):
        answers = inquirer.prompt(language.get_template_questions())
        template_file_content: str = answers["template_file_content"]
        return answer.Answers(
            name=name, language=language, template_file_content=template_file_content
        )
    stages = inquirer.checkbox(
        "What's the stages?",
        choices=[member.value for member in language.Stage],
        default=[member.value for member in language.Stage],
    )
    language.set_stages(stages)
    attribute = inquirer.prompt(language.get_attribute_questions())
    language.set_attribute(attribute)
    return answer.Answers(name=name, language=language)


def load_joj1_yaml(yaml_path: Path) -> joj1.Config:
    joj1_obj = yaml.safe_load(yaml_path.read_text())
    return joj1.Config(**joj1_obj)


def load_joj3_toml(
    root_path: Path, repo_toml_path: Path, task_toml_path: Path
) -> Tuple[repo.Config, task.Config]:
    repo_obj = tomli.loads(repo_toml_path.read_text())
    task_obj = tomli.loads(task_toml_path.read_text())
    repo_conf = repo.Config(**repo_obj)
    repo_conf.root = root_path
    repo_conf.path = repo_toml_path.relative_to(root_path)
    task_conf = task.Config(**task_obj)
    task_conf.root = root_path
    task_conf.path = task_toml_path.relative_to(root_path)
    return repo_conf, task_conf
