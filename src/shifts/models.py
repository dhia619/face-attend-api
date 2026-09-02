from sqlalchemy import Column, ForeignKey, Time, String, Integer

from src.database import SQLAlchemyBase


class Shift(SQLAlchemyBase):
    __tablename__ = "shift"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    department_id = Column(
        Integer,
        ForeignKey("department.id"), 
        nullable=True, 
        unique=True
    )
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)