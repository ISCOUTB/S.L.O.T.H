#!/bin/bash

PROTO_PATH="../proto"

if [ ! -d "$PROTO_PATH" ]; then
    echo "[error] directory not found $PROTO_PATH"
    exit 1
fi

PROTO_FILES=$(find $PROTO_PATH -name "*.proto")

if [ -z "$PROTO_FILES" ]; then
    echo "[error] no proto files found in $PROTO_PATH"
    exit 1
fi

PACKAGE_PATH="./src/proto_utils"
EXPORT_PATH="$PACKAGE_PATH/generated"

if [ ! -d "$EXPORT_PATH" ]; then
    echo "[info] creating directory $EXPORT_PATH"
    mkdir -p $EXPORT_PATH
fi

uv run python -m grpc_tools.protoc \
    --pyi_out=$EXPORT_PATH \
    --python_out=$EXPORT_PATH \
    --grpc_python_out=$EXPORT_PATH \
    --proto_path=$PROTO_PATH \
    $PROTO_FILES

create_init() {
    local path="$1"
    if [ ! -f "$path/__init__.py" ]; then
        touch "$path/__init__.py"
        echo "[info] created $path/__init__.py"
    fi
}

create_all_inits() {
    local base_dir="$1"

    find "$base_dir" -type d | while read -r dir; do
        if [ ! -f "$dir/__init__.py" ]; then
            touch "$dir/__init__.py"
            echo "[info] created $dir/__init__.py"
        fi
    done
}

populate_main_init() {
    local path=$1

    if [ ! -f "$path" ]; then
        echo "[info] creating $path"
        touch "$path"
    fi

    if [ -s "$path" ]; then
        echo "[info] $path already populated, skipping"
        return 0
    fi

    echo "# Auto-generated exports" >> "$path"
    echo "# ruff: noqa" >> "$path"

    local dir=$(dirname "$path")

    for pyfile in $(find "$dir" -maxdepth 1 -name "*.py" ! -name "__init__.py"); do
        modname=$(basename "$pyfile" .py)
        echo "from .${modname} import *" >> "$path"
    done

    for subdir in $(find "$dir" -mindepth 1 -type d); do
        for pyfile in $(find "$subdir" -maxdepth 1 -name "*.py" ! -name "__init__.py"); do
            modname=$(basename "$pyfile" .py)
            submod=$(basename "$subdir")
            echo "from .${submod}.${modname} import *" >> "$path"
        done
    done

    echo "[success] main_init populated"
}

fix_submodules() {
    local base_dir="$1"
    find "$base_dir" -type f -name "*.py" ! -name "__init__.py" | while read -r file; do
        if grep -q '# FIXED: relative imports' "$file"; then
            continue
        fi

        if grep -qE '^from [a-zA-Z0-9_]+ import [a-zA-Z0-9_]+ as ' "$file"; then
            echo "[fix] $file"
            sed -i -E 's/^from ([a-zA-Z0-9_]+) import ([a-zA-Z0-9_]+) as (.*)$/from . import \2 as \3/' "$file"

            sed -i '1i# ruff: noqa' "$file"
            sed -i '1i# type: ignore' "$file"
            sed -i '1i# FIXED: relative imports' "$file"
        fi
    done
}

create_init "$PACKAGE_PATH"
create_all_inits "$EXPORT_PATH"
populate_main_init "$EXPORT_PATH/__init__.py"
fix_submodules "$EXPORT_PATH"
