import asyncio
from typing import Any, Dict

import aio_pika
from messaging_utils.core.config import settings as mq_settings

from src.core.database_client import DatabaseClient


async def check_rabbitmq_connection() -> Dict[str, str]:
    """Check RabbitMQ connection health."""
    try:
        rabbitmq_url = str(mq_settings.RABBITMQ_URI)

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


def check_database_client_connection(
    db_client: DatabaseClient,
) -> Dict[str, str]:
    """Check overall database client connection health."""
    try:
        redis_health = db_client.redis_ping()["pong"]
    except Exception:
        redis_health = False

    try:
        mongo_health = db_client.mongo_ping()["pong"]
    except Exception:
        mongo_health = False

    overall_status = "healthy" if mongo_health and redis_health else "unhealthy"
    return {
        "status": overall_status,
        "mongodb": mongo_health,
        "redis": redis_health,
    }


async def check_databases_connection(
    db_client: DatabaseClient,
) -> Dict[str, Dict[str, Any]]:
    """Check overall database connection health."""
    rabbitmq_health = await check_rabbitmq_connection()
    database_health = check_database_client_connection(db_client)

    overall_status = (
        "healthy"
        if database_health["status"] == "healthy"
        and rabbitmq_health["status"] == "healthy"
        else "unhealthy"
    )
    return {
        "status": overall_status,
        "database": database_health,
        "rabbitmq": rabbitmq_health,
    }
