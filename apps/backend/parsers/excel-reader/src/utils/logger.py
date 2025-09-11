import logging

logger = logging.getLogger("DDLGeneratorServer")
handler = logging.StreamHandler()
formatter = logging.Formatter("[server] [excel-reader] %(message)s")
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.propagate = False

if __name__ == "__main__":
    pass
