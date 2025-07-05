python3 -m grpc_tools.protoc \
  dtypes.proto \
  --proto_path ../proto/ --python_out ./src/clients/dtypes/ \
  --pyi_out ./src/clients/dtypes/ \
  --grpc_python_out ./src/clients/dtypes/
