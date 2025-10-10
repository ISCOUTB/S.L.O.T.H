from proto_utils.database.base_client import DatabaseClient

from src.core.config import settings

database_client = DatabaseClient(settings.DATABASE_CONNECTION_CHANNEL)
