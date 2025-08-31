"""Module entrypoint to run the Typer app via `python -m`.

This allows usage without console scripts being on PATH.
"""

from .cli import app

if __name__ == "__main__":
    app()
