from typing import Annotated, Any, Dict, Generator

from fastapi import Depends, FastAPI

from src.core.config import settings
from src.core.database_client import DatabaseClient, get_database_client
from src.services.healthcheck import check_databases_connection

app = FastAPI()


def generate_new_db_client() -> Generator[DatabaseClient, None, None]:
    db_client = get_database_client()
    try:
        yield db_client
    finally:
        db_client.close()


DatabaseClientDep = Annotated[DatabaseClient, Depends(generate_new_db_client)]


@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Minimal Typechecking Server is running."}


@app.get("/health")
async def health_check(
    database_client: DatabaseClientDep,
) -> Dict[str, Any]:
    return await check_databases_connection(database_client)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.minimal_server:app",
        host=settings.MINIMAL_SERVER_HOST,
        port=settings.MINIMAL_SERVER_PORT,
        reload=settings.MINIMAL_SERVER_DEBUG,
        reload_dirs=["src/"] if settings.MINIMAL_SERVER_DEBUG else None,
        reload_includes=["*.py"] if settings.MINIMAL_SERVER_DEBUG else None,
        log_level="info",
        use_colors=True,
    )
