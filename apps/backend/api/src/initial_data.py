import logging

from sqlalchemy.orm import Session

from src.core.init_db import init_db
from src.core.database_sql import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    session: Session = SessionLocal()
    try:
        init_db(session)
    finally:
        session.close()


def main() -> None:
    logger.info("Creating initial information")
    init()
    logger.info("Initial information created")


if __name__ == "__main__":
    main()
