import inquirer
import typer

from joj3_config_generator.utils.logger import logger

app = typer.Typer(add_completion=False)


@app.command()
def create() -> None:
    """
    Create a new JOJ3 config file
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
def convert() -> None:
    """
    Convert a JOJ1 config file to JOJ3 config file
    """
    logger.info("Converting")
