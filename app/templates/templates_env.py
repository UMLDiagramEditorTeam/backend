from pathlib import Path

from jinja2 import Environment, FileSystemLoader

templates_dir = Path(__file__).resolve().parent

jinja_env = Environment(
    loader=FileSystemLoader(templates_dir),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)
