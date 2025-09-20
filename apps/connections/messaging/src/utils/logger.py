import logging

logging.basicConfig(level=logging.INFO)


logger = logging.getLogger("Messaging Server")
handler = logging.StreamHandler()
formatter = logging.Formatter("[server] [Messaging] %(message)s")
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.propagate = False
