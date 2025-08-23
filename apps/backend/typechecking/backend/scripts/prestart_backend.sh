set -e
set -x

# Inicializar DB
python3 -m app.postgres_prestart

# Correr migraciones
python3 -m alembic upgrade head

# Crear la información inicial a la DB
python3 -m app.initial_data
