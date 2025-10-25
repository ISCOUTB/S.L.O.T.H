#!/bin/bash

PROTO_PATH="../../proto"

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

