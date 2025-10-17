FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /workspace/apps/backend/parsers/ddl-generator/

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.7.6 /uv /uvx /bin/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/workspace/apps/backend/parsers/ddl-generator/.venv/bin:$PATH"

# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Copy shared packages
COPY ./packages/proto-utils/proto-utils-py /workspace/packages/proto-utils/proto-utils-py

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=./apps/backend/parsers/ddl-generator/uv.lock,target=uv.lock \
    --mount=type=bind,source=./apps/backend/parsers/ddl-generator/pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

ENV PYTHONPATH=.

COPY ./apps/backend/parsers/ddl-generator/pyproject.toml \
    ./apps/backend/parsers/ddl-generator/uv.lock \
    ./

COPY ./apps/backend/parsers/ddl-generator/src ./src

# Sync the project
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

CMD ["python", "-m", "src.server"]
