import logging

logging.basicConfig(level=logging.INFO)


logger = logging.getLogger("Typechecking")
handler = logging.StreamHandler()
formatter = logging.Formatter("[server] [typechecking] %(message)s")
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.propagate = False
