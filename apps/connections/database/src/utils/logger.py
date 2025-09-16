import logging

logging.basicConfig(level=logging.INFO)


logger = logging.getLogger("DatabaseConnectionServer")
handler = logging.StreamHandler()
formatter = logging.Formatter("[server] [Database] %(message)s")
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.propagate = False
