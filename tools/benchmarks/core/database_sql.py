from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from core.config import settings


engine = create_engine(str(settings.POSTGRES_URI))
SessionLocal = sessionmaker(autoflush=True, bind=engine)

BaseModel = declarative_base()