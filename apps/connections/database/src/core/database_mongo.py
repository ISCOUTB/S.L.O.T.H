"""MongoDB database operations module.

This module provides MongoDB client operations for document storage and retrieval.
It includes a connection wrapper class that simplifies common MongoDB operations
and provides pre-configured connections for tasks and schemas collections.

The module uses PyMongo for database interactions and includes basic CRUD operations
with proper error handling and type hints.
"""

import pymongo
import pymongo.database
import pymongo.collection

from src.core.config import settings


class MongoConnection:
    """MongoDB connection wrapper class.

    Provides a simplified interface for MongoDB operations including
    basic CRUD operations and collection management. Encapsulates
    the MongoDB client, database, and collection objects.

    Args:
        uri (str): MongoDB connection URI.
        database (str): Name of the database to connect to.
        collection (str): Name of the collection to work with.
    """

    def __init__(self, uri: str, database: str, collection: str):
        self.__client: pymongo.MongoClient = pymongo.MongoClient(uri)
        self.__database: pymongo.database.Database = self.__client[database]
        self.__collection: pymongo.collection.Collection = self.__database[collection]

    # ==================== General Purpose ====================
    # To be honest, these functions are a little bit useless, but maybe in a future
    # we would want to make something better, and with this could be easier, than
    # using directly MongoClient. Who knows

    @property
    def client(self) -> pymongo.MongoClient:
        """Get the MongoDB client instance.

        Returns:
            pymongo.MongoClient: The MongoDB client instance.
        """
        return self.__client

    @property
    def database(self) -> pymongo.database.Database:
        """Get the MongoDB database instance.

        Returns:
            pymongo.database.Database: The MongoDB database instance.

        Raises:
            ValueError: If database is not set.
        """
        if self.__database is None:
            raise ValueError("Database not set. Please provide a database name.")
        return self.__database

    @property
    def collection(self) -> pymongo.collection.Collection:
        """Get the MongoDB collection instance.

        Returns:
            pymongo.collection.Collection: The MongoDB collection instance.

        Raises:
            ValueError: If database is not set.
        """
        if self.__database is None:
            raise ValueError(
                "Database not set. Please set a database before accessing collections."
            )
        return self.__collection

    def insert_one(self, document: dict) -> pymongo.results.InsertOneResult:
        """Insert a single document into the collection."""
        return self.__collection.insert_one(document)

    def count_documents(self, filter: dict = None) -> int:
        """Count the number of documents in the collection.

        Args:
            filter (dict, optional): Query filter to count specific documents.
                                   Defaults to None (counts all documents).

        Returns:
            int: Number of documents matching the filter.
        """
        return self.__collection.count_documents(filter if filter is not None else {})

    def find_one(self, filter: dict = None, projection: dict = None):
        """Find a single document in the collection.

        Args:
            filter (dict, optional): Query filter to find specific document.
                                   Defaults to None (finds any document).
            projection (dict, optional): Fields to include/exclude in the result.
                                       Defaults to None (returns all fields).

        Returns:
            dict or None: The found document or None if not found.
        """
        return self.__collection.find_one(
            filter if filter is not None else {}, projection
        )

    def update_one(self, filter: dict, update: dict) -> pymongo.results.UpdateResult:
        """Update a single document in the collection.

        Args:
            filter (dict): Query filter to identify the document to update.
            update (dict): Update operations to apply to the document.

        Returns:
            pymongo.results.UpdateResult: Result of the update operation.
        """
        return self.__collection.update_one(filter, update)

    def delete_one(self, filter: dict) -> pymongo.results.DeleteResult:
        """Delete a single document in the collection.

        Args:
            filter (dict): Query filter to identify the document to delete.

        Returns:
            pymongo.results.DeleteResult: Result of the delete operation.
        """
        return self.__collection.delete_one(filter)


mongo_tasks_connection = MongoConnection(
    str(settings.MONGO_URI),
    settings.MONGO_DB,
    settings.MONGO_TASKS_COLLECTION,
)

mongo_schemas_connection = MongoConnection(
    str(settings.MONGO_URI),
    settings.MONGO_DB,
    settings.MONGO_SCHEMAS_COLLECTION,
)
