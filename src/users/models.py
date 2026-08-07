from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Boolean

from src.database import SQLAlchemyBase

class User(SQLAlchemyBase):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime)
    last_login_at = Column(DateTime)
    is_active = Column(Boolean, default=True)