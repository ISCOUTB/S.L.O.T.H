from typing import TypedDict


class ConnectionParams(TypedDict):
    host: str
    port: int
    virtual_host: str
    username: str
    password: str
