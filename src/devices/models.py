from sqlalchemy import Column, String, Integer, DateTime, func

from src.database import SQLAlchemyBase

class Device(SQLAlchemyBase):

    __tablename__ = "device"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    refresh_token_hash = Column(String, unique=True, nullable=True)
    activation_code = Column(String, unique=True, nullable=True)
    activation_expires_at = Column(DateTime(timezone=True), nullable=True)

    rtsp_url = Column(String, nullable=True)