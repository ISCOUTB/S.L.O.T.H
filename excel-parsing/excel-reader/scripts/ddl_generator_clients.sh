python3 -m grpc_tools.protoc \
  ddl_generator.proto \
  --proto_path ../proto/ --python_out ./src/clients/ddl_generator/ \
  --pyi_out ./src/clients/ddl_generator/ \
  --grpc_python_out ./src/clients/ddl_generator/
