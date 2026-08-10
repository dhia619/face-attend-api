from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.database import SQLAlchemyBase

class Role(SQLAlchemyBase):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

class Permission(SQLAlchemyBase):
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True)

class RolePermission(SQLAlchemyBase):
    __tablename__ = "role_permission"

    role_id = Column(Integer, ForeignKey("role.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permission.id"), primary_key=True)

    role = relationship("Role")
    permission = relationship("Permission")