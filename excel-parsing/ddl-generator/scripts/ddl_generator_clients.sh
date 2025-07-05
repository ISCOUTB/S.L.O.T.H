python3 -m grpc_tools.protoc \
  dtypes.proto ddl_generator.proto \
  --proto_path ../proto/ --python_out ./src/clients/ \
  --pyi_out ./src/clients/ \
  --grpc_python_out ./src/clients/
