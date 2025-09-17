import json
from pathlib import Path
from typing import Optional

import tomlkit
import typer
from typing_extensions import Annotated

from joj3_config_generator import get_version
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

app = typer.Typer(add_completion=False, name="joj3-forge")


def version_callback(value: bool) -> None:
    if value:
        print(f"{app.info.name} Version: {get_version()}")
        raise typer.Exit()


@app.callback()
def common(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            help="Show the application version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    if ctx.resilient_parsing:
        return
    logger.info(f"Running '{ctx.invoked_subcommand}' command. Version: {get_version()}")


@app.command(hidden=True)
def create(
    toml_path: Annotated[Optional[Path], typer.Argument()] = None,
) -> None:
    """
    [WIP] Create a new JOJ3 task toml config file
    """
    answers = load_joj3_task_toml_answers()
    task_model = create_joj3_task_conf(answers)
    result_dict = task_model.model_dump(
        mode="json", by_alias=True, exclude_none=True, exclude_unset=True
    )
    toml_str = tomlkit.dumps(result_dict)
    if toml_path is None:
        logger.info("Writing task toml to stdout")
        print(toml_str)
    else:
        logger.info(f"Creating task toml file {toml_path}")
        toml_path.write_text(toml_str)


@app.command(hidden=True)
def convert_joj1(yaml_path: Path, toml_path: Path) -> None:
    """
    [WIP] Convert a JOJ1 yaml config file to JOJ3 task toml config file
    """
    logger.info(f"Converting yaml file {yaml_path}")
    joj1_model = load_joj1_yaml(yaml_path)
    task_model = convert_joj1_conf(joj1_model)
    result_dict = task_model.model_dump(mode="json", by_alias=True, exclude_none=True)
    toml_path.write_text(tomlkit.dumps(result_dict))


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
    app.pretty_exceptions_enable = False
    logger.info(f"Converting files in {root.absolute()}")
    error_json_paths = []
    for repo_toml_path in root.glob("**/repo.toml"):
        if not any(p != repo_toml_path for p in repo_toml_path.parent.glob("*.toml")):
            fallback_toml_path = repo_toml_path.parent / "conf.toml"
            if not fallback_toml_path.exists():
                fallback_toml_path.write_text(
                    'name = "health check"\nmax-total-score = 0\n'
                )
        for task_toml_path in repo_toml_path.parent.glob("**/*.toml"):
            if repo_toml_path == task_toml_path:
                continue
            toml_name = task_toml_path.name.removesuffix(".toml")
            result_json_path = task_toml_path.parent / f"{toml_name}.json"
            logger.info(
                f"Converting {repo_toml_path} & {task_toml_path} to {result_json_path}"
            )
            try:
                repo_conf, task_conf = load_joj3_toml(
                    root, repo_toml_path, task_toml_path
                )
            except Exception:
                error_json_paths.append(result_json_path)
                continue
            result_model = convert_joj3_conf(repo_conf, task_conf)
            result_dict = result_model.model_dump(
                mode="json", by_alias=True, exclude_none=True
            )
            with result_json_path.open("w", newline="") as result_file:
                json.dump(result_dict, result_file, ensure_ascii=False, indent=4)
                result_file.write("\n")
    if error_json_paths:
        logger.error(
            f"Failed to convert {len(error_json_paths)} file(s): {', '.join(str(json_path) for json_path in error_json_paths)}. Check previous errors for details."
        )
        raise typer.Exit(code=1)
