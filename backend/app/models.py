from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="department")
    computer_records = relationship("ComputerRecord", back_populates="department")
    printer_records = relationship("PrinterRecord", back_populates="department")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True, default="-")
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(150), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="lectura")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    department = relationship("Department", back_populates="users")


class ComputerRecord(Base):
    __tablename__ = "computer_records"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String(100), nullable=False)
    owner_identifier = Column(String(100), nullable=True)
    brand = Column(String(120), nullable=True)
    device_type = Column(String(20), nullable=False, default="PC")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    ip_address = Column(String(45), nullable=True)
    is_operational = Column(Boolean, nullable=False, default=True)
    ethernet_port = Column(String(120), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    department = relationship("Department", back_populates="computer_records")


class PrinterRecord(Base):
    __tablename__ = "printer_records"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(150), nullable=True)
    brand = Column(String(120), nullable=True)
    serial_number = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    ethernet_port = Column(String(120), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    is_operational = Column(Boolean, nullable=False, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    department = relationship("Department", back_populates="printer_records")


class FloorPlan(Base):
    __tablename__ = "floor_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, default="Plano del edificio")
    grid_width = Column(Integer, nullable=False, default=8)
    grid_height = Column(Integer, nullable=False, default=6)
    data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
