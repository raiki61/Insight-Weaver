
## How to develop

enter your venv on project root.

- `uv sync`
- `uv pip install -e .[dev]`
- `uv pip install -e .[test]`

### format

- `uv run ruff check --fix .`
- `uv run ruff format .`

## How to test

- `uv run pytest`