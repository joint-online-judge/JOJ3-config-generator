import json
import os
from pathlib import Path
from typing import Any, Dict

import rtoml
import typer
import yaml

from joj3_config_generator.convert import convert as convert_conf
from joj3_config_generator.convert import convert_joj1 as convert_joj1_conf
from joj3_config_generator.convert import distribute_json
from joj3_config_generator.models import joj1, repo, task
from joj3_config_generator.utils.logger import logger

app = typer.Typer(add_completion=False)


@app.command()
def convert_joj1(yaml_file: typer.FileText, toml_file: typer.FileTextWrite) -> None:
    """
    Convert a JOJ1 yaml config file to JOJ3 toml config file
    """
    logger.info(f"Converting yaml file {yaml_file}")
    joj1_obj = yaml.safe_load(yaml_file.read())
    joj1_model = joj1.Config(**joj1_obj)
    task_model = convert_joj1_conf(joj1_model)
    result_dict = task_model.model_dump(by_alias=True, exclude_none=True)
    toml_file.write(rtoml.dumps(result_dict))


@app.command()
def convert(
    root: Path = typer.Option(
        Path("."),
        "--conf-root",
        "-c",
        help="This should be consistent with the root of how you run JOJ3",
    ),
    repo_path: Path = typer.Option(
        Path("."),
        "--repo-root",
        "-r",
        help="This would be where you put your repo.toml file",
    ),
    distribute: bool = typer.Option(
        False, "--distribute", "-d", help="This flag determine whether to distribute"
    ),
) -> Dict[str, Any]:
    logger.info(f"Converting files in {root.absolute()}")
    repo_toml_path = os.path.join(repo_path.absolute(), "basic", "repo.toml")
    task_toml_path = os.path.join(root.absolute(), "basic", "task.toml")
    result_json_path = os.path.join(root.absolute(), "basic", "task.json")
    with open(repo_toml_path, encoding=None) as repo_file:
        repo_toml = repo_file.read()
    with open(task_toml_path, encoding=None) as task_file:
        task_toml = task_file.read()
    repo_obj = rtoml.loads(repo_toml)
    task_obj = rtoml.loads(task_toml)
    result_model = convert_conf(repo.Config(**repo_obj), task.Config(**task_obj), root)
    result_dict = result_model.model_dump(by_alias=True, exclude_none=True)

    with open(result_json_path, "w", encoding=None) as result_file:
        json.dump(result_dict, result_file, ensure_ascii=False, indent=4)
        result_file.write("\n")

    # distribution on json
    # need a get folder path function
    if distribute:
        folder_path = "/home/tt/.config/joj"
        folder_path = f"{Path.home()}/Desktop/engr151-joj/home/tt/.config/joj/homework"
        folder_path = f"{Path.home()}/Desktop/FOCS/JOJ3-config-generator/tests/convert/"
        distribute_json(folder_path, repo_obj, conf_root=root)
    return result_dict
