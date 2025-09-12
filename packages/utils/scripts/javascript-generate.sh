cd javascript/

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

EXPORT_PATH="./src/generated"

if [ ! -d "$EXPORT_PATH" ]; then
    mkdir -p $EXPORT_PATH
fi

protoc \
    --plugin=./node_modules/.bin/protoc-gen-ts \
    --ts_out=./src/generated \
    --proto_path=$PROTO_PATH \
    $PROTO_FILES