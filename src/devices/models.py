from sqlalchemy import Column, String, Integer, DateTime

from src.database import SQLAlchemyBase

class Device(SQLAlchemyBase):

    __tablename__ = "device"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    activation_code_hash = Column(String, unique=True)
    activation_expires_at = Column(DateTime(timezone=True))