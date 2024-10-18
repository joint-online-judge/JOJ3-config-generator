import typer

from joj3_config_generator.utils.logger import logger

app = typer.Typer(add_completion=False)


@app.callback()
def callback() -> None:
    """
    Awesome Portal Gun
    """


@app.command()
def shoot() -> None:
    """
    Shoot the portal gun
    """
    typer.echo("Shooting portal gun")
    logger.info("Shooting portal gun")


@app.command()
def load() -> None:
    """
    Load the portal gun
    """
    typer.echo("Loading portal gun")
    logger.info("Loading portal gun")
