import pymongo
import pymongo.database
import pymongo.collection

from src.core.config import settings


class MongoConnection:
    def __init__(self, uri: str, database: str, collection: str):
        self.__client: pymongo.MongoClient = pymongo.MongoClient(uri)
        self.__database: pymongo.database.Database = self.__client[database]
        self.__collection: pymongo.collection.Collection = self.__database[
            collection
        ]

    # ==================== General Purporse ====================
    # To be honest, these functions are a little bit useless, but maybe in a future
    # we would want to make something better, and with this could be easier, than
    # using directly MongoClient. Who knows

    @property
    def client(self) -> pymongo.MongoClient:
        return self.__client

    @property
    def database(self) -> pymongo.database.Database:
        if self.__database is None:
            raise ValueError(
                "Database not set. Please provide a database name."
            )
        return self.__database

    @property
    def collection(self) -> pymongo.collection.Collection:
        if not self.__database:
            raise ValueError(
                "Database not set. Please set a database before accessing collections."
            )
        return self.__collection

    def insert_one(self, document: dict) -> pymongo.results.InsertOneResult:
        """Insert a single document into the collection."""
        return self.__collection.insert_one(document)

    def count_documents(self, filter: dict = {}) -> int:
        """Count the number of documents in the collection."""
        return self.__collection.count_documents(filter)

    def find_one(self, filter: dict = {}, projection: dict = None):
        """Find a single document in the collection."""
        return self.__collection.find_one(filter, projection)

    def update_one(
        self, filter: dict, update: dict
    ) -> pymongo.results.UpdateResult:
        """Update a single document in the collection."""
        return self.__collection.update_one(filter, update)


mongo_connection = MongoConnection(
    str(settings.MONGO_URI), settings.MONGO_DB, settings.MONGO_TASKS_COLLECTION
)
