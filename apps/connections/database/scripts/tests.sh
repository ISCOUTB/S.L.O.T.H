set -x

# Opción con prints visibles
uv run coverage run --source=. -m pytest -s
uv run coverage report --show-missing
uv run coverage html --title "${@-coverage}"
uv run coverage xml
