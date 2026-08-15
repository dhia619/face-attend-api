from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Boolean, func

from src.database import SQLAlchemyBase

class User(SQLAlchemyBase):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    refresh_token_hash = Column(String, unique=True)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())
    last_login_at = Column(DateTime)
    is_active = Column(Boolean, default=True)