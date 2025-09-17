import json
from pathlib import Path
from typing import Any, Dict, Tuple, Type, cast

import inquirer
import tomli
import yaml
from pydantic import AliasChoices, BaseModel, ValidationError

from joj3_config_generator.models import answer, joj1, repo, task
from joj3_config_generator.models.common import Memory, Time
from joj3_config_generator.utils.logger import logger


def load_joj3_task_toml_answers() -> answer.Answers:
    name = inquirer.text("What's the task name?", default="hw0")
    language = inquirer.list_input(
        "What's the language?", choices=[(cls.name, cls) for cls in answer.LANGUAGES]
    )
    language = cast(Type[answer.LanguageInterface], language)
    if inquirer.confirm("Load content from templates?", default=True):
        questions = language.get_template_questions()
        if not questions[0].choices:
            logger.warning("No template files found for the selected language. ")
            return answer.Answers(name=name, language=language)
        answers = inquirer.prompt(questions)
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
    def check_unnecessary_fields(
        pydantic_model_type: Type[BaseModel],
        input_dict: Dict[str, Any],
        file_path: Path,
        current_path: str = "",
    ) -> None:
        def format_value_for_toml_warning(value: Any) -> str:
            if isinstance(value, str):
                escaped_value = value.replace("\\", "\\\\").replace('"', '\\"')
                return f'"{escaped_value}"'
            elif isinstance(value, bool):
                return str(value).lower()
            elif isinstance(value, (int, float)):
                return str(value)
            elif isinstance(value, Path):
                escaped_value = str(value).replace("\\", "\\\\").replace('"', '\\"')
                return f'"{escaped_value}"'
            elif isinstance(value, list):
                formatted_elements = [
                    format_value_for_toml_warning(item) for item in value
                ]
                return f"[{', '.join(formatted_elements)}]"
            elif isinstance(value, dict):
                return json.dumps(value, separators=(",", ":"))
            elif value is None:
                return "None"
            else:
                return repr(value)

        default_instance = pydantic_model_type.model_construct()
        for field_name, field_info in pydantic_model_type.model_fields.items():
            should_warn = False
            full_field_path = (
                f"{current_path}.{field_name}" if current_path else field_name
            )
            toml_field_name = field_name
            if field_info.validation_alias:
                if isinstance(field_info.validation_alias, str):
                    if field_info.validation_alias in input_dict:
                        toml_field_name = field_info.validation_alias
                elif isinstance(field_info.validation_alias, AliasChoices):
                    for choice in field_info.validation_alias.choices:
                        if choice in input_dict:
                            if isinstance(choice, str):
                                toml_field_name = choice
                                break
            if toml_field_name not in input_dict:
                continue
            toml_value = input_dict[toml_field_name]
            default_value = getattr(default_instance, field_name)
            # Handle List[Pydantic.BaseModel]
            if (
                field_info.annotation is not None
                and hasattr(field_info.annotation, "__origin__")
                and field_info.annotation.__origin__ is list
                and hasattr(field_info.annotation, "__args__")
                and len(field_info.annotation.__args__) == 1
                and isinstance(field_info.annotation.__args__[0], type)
                and issubclass(field_info.annotation.__args__[0], BaseModel)
            ):
                nested_model_type = field_info.annotation.__args__[0]
                # Ensure the TOML value is a list (as expected for this type)
                if isinstance(toml_value, list):
                    for i, toml_item in enumerate(toml_value):
                        if isinstance(toml_item, dict):
                            check_unnecessary_fields(
                                nested_model_type,
                                toml_item,
                                file_path,
                                f"{full_field_path}[{i}]",
                            )
                continue
            # Handle directly nested Pydantic models (non-list)
            if isinstance(field_info.annotation, type) and issubclass(
                field_info.annotation, BaseModel
            ):
                if isinstance(toml_value, dict):
                    check_unnecessary_fields(
                        field_info.annotation,
                        toml_value,
                        file_path,
                        full_field_path,
                    )
                continue
            # Handle Path type
            elif (
                isinstance(toml_value, str)
                and isinstance(default_value, Path)
                and Path(toml_value) == default_value
            ):
                should_warn = True
            # Handle Time type
            elif isinstance(default_value, Time) and Time(toml_value) == default_value:
                should_warn = True
            # Handle Memory type
            elif (
                isinstance(default_value, Memory)
                and Memory(toml_value) == default_value
            ):
                should_warn = True
            # Handle non-model list types (e.g., List[str], List[int])
            elif (
                isinstance(toml_value, list)
                and isinstance(default_value, list)
                and toml_value == default_value
            ):
                should_warn = True
            # Handle other basic types (str, int, float, bool, dict)
            elif toml_value == default_value and toml_value != {}:
                should_warn = True
            if should_warn:
                logger.warning(
                    f"In file {file_path}, unnecessary field "
                    f"`{full_field_path} = {format_value_for_toml_warning(toml_value)}`"
                    " can be removed as it matches the default value"
                )

    repo_obj = tomli.loads(repo_toml_path.read_text())
    task_obj = tomli.loads(task_toml_path.read_text())
    try:
        repo_conf = repo.Config(**repo_obj)
    except ValidationError as e:
        logger.error(
            f"Error parsing {repo_toml_path}, most likely to be unknown fields, check the latest sample toml carefully:\n{e}"
        )
        raise
    repo_conf.root = root_path
    repo_conf.path = repo_toml_path.relative_to(root_path)
    try:
        task_conf = task.Config(**task_obj)
    except ValidationError as e:
        logger.error(
            f"Error parsing {task_toml_path}, most likely to be unknown fields, check the latest sample toml carefully:\n{e}"
        )
        raise
    task_conf.root = root_path
    task_conf.path = task_toml_path.relative_to(root_path)
    check_unnecessary_fields(repo.Config, repo_obj, repo_toml_path)
    check_unnecessary_fields(task.Config, task_obj, task_toml_path)
    return repo_conf, task_conf
