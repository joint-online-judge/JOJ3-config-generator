import json
from pathlib import Path

import inquirer
import rtoml
import typer
import yaml
from typing_extensions import Annotated

from joj3_config_generator.convert import convert as convert_conf
from joj3_config_generator.convert import convert_joj1 as convert_joj1_conf
from joj3_config_generator.models import joj1, repo, task
from joj3_config_generator.utils.logger import logger

app = typer.Typer(add_completion=False)


@app.command()
def create(toml: typer.FileTextWrite) -> None:
    """
    Create a new JOJ3 toml config file
    """
    logger.info("Creating")
    questions = [
        inquirer.List(
            "size",
            message="What size do you need?",
            choices=["Jumbo", "Large", "Standard", "Medium", "Small", "Micro"],
        ),
    ]
    answers = inquirer.prompt(questions)
    logger.info(answers)


@app.command()
def convert_joj1(yaml_file: typer.FileText, toml_file: typer.FileTextWrite) -> None:
    """
    Convert a JOJ1 yaml config file to JOJ3 toml config file
    """
    logger.info(f"Converting yaml file {yaml_file}")
    joj1_obj = yaml.safe_load(yaml_file.read())
    joj1_model = joj1.Config(**joj1_obj)
    task_model = convert_joj1_conf(joj1_model)
    result_dict = task_model.model_dump(by_alias=True)
    toml_file.write(rtoml.dumps(result_dict))


@app.command()
def convert(
    root: Annotated[
        Path,
        typer.Argument(
            help="root directory of config files, "
            "located at /home/tt/.config/joj in JTC"
        ),
    ] = Path(".")
) -> None:
    """
    Convert given dir of JOJ3 toml config files to JOJ3 json config files
    """
    logger.info(f"Converting files in {root.absolute()}")
    for repo_toml_path in root.glob("**/repo.toml"):
        repo_path = repo_toml_path.parent
        repo_obj = rtoml.loads(repo_toml_path.read_text())
        for task_toml_path in repo_path.glob("**/*.toml"):
            if repo_toml_path == task_toml_path:
                continue
            toml_name = task_toml_path.name.removesuffix(".toml")
            result_json_path = task_toml_path.parent / f"{toml_name}.json"
            logger.info(
                f"Converting {repo_toml_path} & {task_toml_path} to {result_json_path}"
            )
            task_obj = rtoml.loads(task_toml_path.read_text())
            repo_conf = repo.Config(**repo_obj)
            repo_conf.root = root
            repo_conf.path = repo_toml_path.relative_to(root)
            task_conf = task.Config(**task_obj)
            task_conf.root = root
            task_conf.path = task_toml_path.relative_to(root)
            result_model = convert_conf(repo_conf, task_conf)
            result_dict = result_model.model_dump(by_alias=True, exclude_none=True)
            with result_json_path.open("w") as result_file:
                json.dump(result_dict, result_file, ensure_ascii=False, indent=4)
                result_file.write("\n")
