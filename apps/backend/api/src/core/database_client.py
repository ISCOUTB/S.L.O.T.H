from src.core.config import settings
from proto_utils.database.base_client import DatabaseClient


database_client = DatabaseClient(settings.DATABASE_CONNECTION_CHANNEL)
