import json
import os
from pathlib import Path

import inquirer
import rtoml
import typer

from joj3_config_generator.convert import convert as convert_conf
from joj3_config_generator.models import RepoConfig, TaskConfig
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
def convert_joj1(yaml: typer.FileText, toml: typer.FileTextWrite) -> None:
    """
    Convert a JOJ1 yaml config file to JOJ3 toml config file
    """
    logger.info("Converting")


@app.command()
def convert(root: Path = Path(".")) -> None:
    """
    Convert given dir of JOJ3 toml config files to JOJ3 json config files
    """
    logger.info(f"Converting files in {root.absolute()}")
    repo_toml_path = os.path.join(root, "repo.toml")
    # TODO: loop through all dirs to find all task.toml
    task_toml_path = os.path.join(root, "task.toml")
    result_json_path = os.path.join(root, "task.json")
    with open(repo_toml_path) as repo_file:
        repo_toml = repo_file.read()
    with open(task_toml_path) as task_file:
        task_toml = task_file.read()
    repo_obj = rtoml.loads(repo_toml)
    task_obj = rtoml.loads(task_toml)
    result_model = convert_conf(RepoConfig(**repo_obj), TaskConfig(**task_obj))
    result_dict = result_model.model_dump(by_alias=True)
    with open(result_json_path, "w") as result_file:
        json.dump(result_dict, result_file, ensure_ascii=False, indent=4)
        result_file.write("\n")
