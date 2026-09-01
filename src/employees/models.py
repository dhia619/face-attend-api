from sqlalchemy import Column, DateTime, Date, ForeignKey, Integer, String, Boolean, func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from src.config import get_settings
from src.database import SQLAlchemyBase

settings = get_settings()

class Employee(SQLAlchemyBase):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("department.id"), nullable=True)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, unique=True)
    hire_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, nullable=False, default=True)

    face_embedding = relationship("FaceEmbedding", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    department = relationship("Department")

class FaceEmbedding(SQLAlchemyBase):
    __tablename__ = "face_embedding"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employee.id", ondelete="CASCADE"), nullable=False)
    embeddings = Column(Vector(settings.FACE_EMBEDDING_DIMENSION), nullable=False)

    employee = relationship("Employee", back_populates="face_embedding")