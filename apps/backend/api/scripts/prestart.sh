set -e
set -x

# Initialize DB
uv run python -m src.sql_prestart

# Run migrations
uv run python -m alembic upgrade head

# Add initial information to DB
uv run python -m src.initial_data
