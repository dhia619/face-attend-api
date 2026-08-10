from sqlalchemy import Column, Integer, String

from src.database import SQLAlchemyBase
from src.config import get_settings

settings = get_settings()

class Department(SQLAlchemyBase):

    __tablename__ = "department"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)