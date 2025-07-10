python3 -m grpc_tools.protoc \
  sql_builder.proto \
  --proto_path ../proto/ --python_out ./src/clients/sql_builder/ \
  --pyi_out ./src/clients/sql_builder/ \
  --grpc_python_out ./src/clients/sql_builder/
