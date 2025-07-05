python3 -m grpc_tools.protoc \
  formula_parser.proto \
  --proto_path ../proto/ --python_out ./src/clients/formula_parser/ \
  --pyi_out ./src/clients/formula_parser/ \
  --grpc_python_out ./src/clients/formula_parser/
