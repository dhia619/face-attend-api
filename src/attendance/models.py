from src.database import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, String, Float, ForeignKey, func
from sqlalchemy.orm import relationship

class AttendanceRecord(SQLAlchemyBase):

    __tablename__ = "attendance_record"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=False)
    check_type = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    confidence = Column(Float, nullable=False)
    device_id = Column(Integer, ForeignKey("device.id"), nullable=False)

    employee = relationship("Employee")
    device = relationship("Device")