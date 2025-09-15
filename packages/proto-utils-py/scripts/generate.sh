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

EXPORT_PATH="./src/generated"

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

find "$EXPORT_PATH" -type d | while read dir; do
    touch "$dir/__init__.py"
done

MAIN_INIT="$EXPORT_PATH/__init__.py"
echo "# Auto-generated exports" >> "$MAIN_INIT"
echo "# ruff: noqa" >> "$MAIN_INIT"

for pyfile in $(find $EXPORT_PATH -maxdepth 1 -name "*.py" ! -name "__init__.py"); do
    modname=$(basename "$pyfile" .py)
    echo "from .${modname} import *" >> "$MAIN_INIT"
done

for subdir in $(find "$EXPORT_PATH" -mindepth 1 -type d); do
    for pyfile in $(find "$subdir" -maxdepth 1 -name "*.py" ! -name "__init__.py"); do
        modname=$(basename "$pyfile" .py)
        submod=$(basename "$subdir")
        echo "from .${submod}.${modname} import *" >> "$MAIN_INIT"
    done
done

echo "[success] done"