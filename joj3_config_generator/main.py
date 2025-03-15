import json
from pathlib import Path
from typing import Optional

import rtoml
import typer
from typing_extensions import Annotated

from joj3_config_generator.generator import (
    convert_joj1_conf,
    convert_joj3_conf,
    create_joj3_task_conf,
)
from joj3_config_generator.loader import (
    load_joj1_yaml,
    load_joj3_task_toml_answers,
    load_joj3_toml,
)
from joj3_config_generator.models.const import JOJ3_CONFIG_ROOT
from joj3_config_generator.utils.logger import logger

app = typer.Typer(add_completion=False)


@app.command()
def create(
    toml_path: Annotated[Optional[Path], typer.Argument()] = None,
) -> None:
    """
    Create a new JOJ3 task toml config file
    """
    answers = load_joj3_task_toml_answers()
    answers_dict = answers.model_dump(mode="json", by_alias=True)
    logger.debug(f"Got answers: {answers_dict}")
    task_model = create_joj3_task_conf(answers)
    result_dict = task_model.model_dump(
        mode="json", by_alias=True, exclude_none=True, exclude_unset=True
    )
    toml_str = rtoml.dumps(result_dict)
    if toml_path is None:
        logger.info("Writing task toml to stdout")
        print(toml_str)
    else:
        logger.info(f"Creating task toml file {toml_path}")
        toml_path.write_text(toml_str)


@app.command()
def convert_joj1(yaml_path: Path, toml_path: Path) -> None:
    """
    Convert a JOJ1 yaml config file to JOJ3 task toml config file
    """
    logger.info(f"Converting yaml file {yaml_path}")
    joj1_model = load_joj1_yaml(yaml_path)
    task_model = convert_joj1_conf(joj1_model)
    result_dict = task_model.model_dump(mode="json", by_alias=True, exclude_none=True)
    toml_path.write_text(rtoml.dumps(result_dict))


@app.command()
def convert(
    root: Annotated[
        Path,
        typer.Argument(
            help=f"root directory of config files, located at {JOJ3_CONFIG_ROOT} in JTC"
        ),
    ] = Path("."),
) -> None:
    """
    Convert given dir of JOJ3 toml config files to JOJ3 json config files
    """
    logger.info(f"Converting files in {root.absolute()}")
    for repo_toml_path in root.glob("**/repo.toml"):
        for task_toml_path in repo_toml_path.parent.glob("**/*.toml"):
            if repo_toml_path == task_toml_path:
                continue
            toml_name = task_toml_path.name.removesuffix(".toml")
            result_json_path = task_toml_path.parent / f"{toml_name}.json"
            logger.info(
                f"Converting {repo_toml_path} & {task_toml_path} to {result_json_path}"
            )
            repo_conf, task_conf = load_joj3_toml(root, repo_toml_path, task_toml_path)
            result_model = convert_joj3_conf(repo_conf, task_conf)
            result_dict = result_model.model_dump(
                mode="json", by_alias=True, exclude_none=True
            )
            with result_json_path.open("w") as result_file:
                json.dump(result_dict, result_file, ensure_ascii=False, indent=4)
                result_file.write("\n")
