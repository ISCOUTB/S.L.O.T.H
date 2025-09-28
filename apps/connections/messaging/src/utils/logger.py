import logging

from src.core.config import settings

logging.basicConfig(level=logging.INFO)


logger = logging.getLogger("Messaging Server")
logger.setLevel(logging.ERROR)

if settings.MESSAGING_CONNECTION_DEBUG:
    logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] [server] [Messaging] %(message)s")
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.propagate = False
