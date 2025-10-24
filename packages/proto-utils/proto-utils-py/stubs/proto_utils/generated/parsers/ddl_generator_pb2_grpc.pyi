from _typeshed import Incomplete

GRPC_GENERATED_VERSION: str
GRPC_VERSION: Incomplete

class DDLGeneratorStub:
    GenerateDDL: Incomplete
    def __init__(self, channel) -> None: ...

class DDLGeneratorServicer:
    def GenerateDDL(self, request, context) -> None: ...

def add_DDLGeneratorServicer_to_server(servicer, server) -> None: ...

class DDLGenerator:
    @staticmethod
    def GenerateDDL(request, target, options=(), channel_credentials=None, call_credentials=None, insecure: bool = False, compression=None, wait_for_ready=None, timeout=None, metadata=None): ...
