from _typeshed import Incomplete

GRPC_GENERATED_VERSION: str
GRPC_VERSION: Incomplete

class FormulaParserStub:
    ParseFormula: Incomplete
    def __init__(self, channel) -> None: ...

class FormulaParserServicer:
    def ParseFormula(self, request, context) -> None: ...

def add_FormulaParserServicer_to_server(servicer, server) -> None: ...

class FormulaParser:
    @staticmethod
    def ParseFormula(request, target, options=(), channel_credentials=None, call_credentials=None, insecure: bool = False, compression=None, wait_for_ready=None, timeout=None, metadata=None): ...
