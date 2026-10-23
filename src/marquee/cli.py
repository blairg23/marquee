"""marquee CLI entrypoint."""

from __future__ import annotations

import importlib.util

import typer

from marquee import __version__
from marquee.config import load_config
from marquee.runs import new_run

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(False, "--version", help="Show the version and exit."),
) -> None:
    if version:
        typer.echo(f"marquee {__version__}")
        raise typer.Exit()


@app.command()
def doctor() -> None:
    """Check the environment: config presence, Pillow/Raqm support, etc."""
    problems: list[str] = []

    config = load_config()
    if not config.data_dir.exists():
        problems.append(f"data_dir does not exist: {config.data_dir}")

    if importlib.util.find_spec("PIL") is None:
        problems.append("Pillow is not installed")
    else:
        from PIL import features

        if not features.check("raqm"):
            problems.append(
                "Pillow lacks Raqm support -- rebuild with libraqm for correct "
                "kerning, ligatures, and complex text shaping"
            )

    if problems:
        for problem in problems:
            typer.echo(f"FAIL  {problem}")
        raise typer.Exit(code=1)

    typer.echo("OK  environment looks good")


@app.command()
def new(venue: str) -> None:
    """Create a new run for VENUE and print its run directory."""
    config = load_config()
    run_dir = new_run(venue, config=config)
    typer.echo(str(run_dir))


if __name__ == "__main__":
    app()
