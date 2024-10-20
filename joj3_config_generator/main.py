from pathlib import Path

import inquirer
import typer

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
def convert(root_path: Path = Path(".")) -> None:
    """
    Convert given dir of JOJ3 toml config files to JOJ3 json config files
    """
    logger.info(f"Converting {root_path.absolute()}")
