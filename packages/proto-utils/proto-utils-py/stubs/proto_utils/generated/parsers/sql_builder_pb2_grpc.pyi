from _typeshed import Incomplete

GRPC_GENERATED_VERSION: str
GRPC_VERSION: Incomplete

class SQLBuilderStub:
    BuildSQL: Incomplete
    def __init__(self, channel) -> None: ...

class SQLBuilderServicer:
    def BuildSQL(self, request, context) -> None: ...

def add_SQLBuilderServicer_to_server(servicer, server) -> None: ...

class SQLBuilder:
    @staticmethod
    def BuildSQL(request, target, options=(), channel_credentials=None, call_credentials=None, insecure: bool = False, compression=None, wait_for_ready=None, timeout=None, metadata=None): ...
