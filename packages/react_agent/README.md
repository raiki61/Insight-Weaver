
# First of all

enter your venv on project root. and then enter package that you want to develop.

## How to develop


- `uv sync`
- `uv pip install -e .[dev]`
- `uv pip install -e .[test]`

### format

- `uv run ruff check --fix .`
- `uv run ruff format .`

## How to test

- `uv run pytest`