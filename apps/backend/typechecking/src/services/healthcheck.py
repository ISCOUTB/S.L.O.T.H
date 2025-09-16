import aio_pika
import asyncio
from typing import Dict
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.config import settings
from src.core.database_redis import redis_db


async def check_mongodb_connection() -> Dict[str, str]:
    """Check MongoDB connection health."""
    try:
        mongo_url = str(settings.MONGO_URI)
        client = AsyncIOMotorClient(mongo_url)

        # Ping the database with a timeout
        await asyncio.wait_for(client.admin.command("ping"), timeout=5.0)

        # Get server info
        server_info = await client.server_info()
        client.close()

        return {
            "status": "healthy",
            "version": server_info.get("version", "unknown"),
            "response_time_ms": "< 5000",
        }
    except asyncio.TimeoutError:
        return {
            "status": "unhealthy",
            "error": "Connection timeout",
            "response_time_ms": "> 5000",
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_rabbitmq_connection() -> Dict[str, str]:
    """Check RabbitMQ connection health."""
    try:
        rabbitmq_url = str(settings.RABBITMQ_URI)

        # Connect with timeout
        connection = await asyncio.wait_for(
            aio_pika.connect_robust(rabbitmq_url), timeout=5.0
        )

        # Create a channel to test the connection
        channel = await connection.channel()
        await channel.close()
        await connection.close()

        return {"status": "healthy", "response_time_ms": "< 5000"}
    except asyncio.TimeoutError:
        return {
            "status": "unhealthy",
            "error": "Connection timeout",
            "response_time_ms": "> 5000",
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_redis_connection() -> Dict[str, str]:
    """Check Redis connection health."""
    try:
        # Test Redis connection with ping and a simple operation
        def test_redis():
            # Test ping
            redis_db.ping()

            # Test basic operations
            test_key = "healthcheck:test"
            redis_db.set(test_key, "test_value", ex_secs=60)
            result = redis_db.get(test_key)
            redis_db.delete(test_key)
            return result == "test_value"

        # Run Redis operations with timeout
        await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, test_redis),
            timeout=5.0,
        )

        return {"status": "healthy", "response_time_ms": "< 5000"}
    except asyncio.TimeoutError:
        return {
            "status": "unhealthy",
            "error": "Connection timeout",
            "response_time_ms": "> 5000",
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
