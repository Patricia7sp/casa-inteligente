"""
Modelos de dados do sistema Casa Inteligente
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from src.utils.config import settings

Base = declarative_base()


class Device(Base):
    """Modelo para dispositivos inteligentes"""
    
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # "TAPO", "NOVA", etc.
    ip_address = Column(String(15), nullable=False)
    mac_address = Column(String(17), unique=True)
    model = Column(String(100))
    location = Column(String(100))  # Ex: "Cozinha", "Quarto", etc.
    equipment_connected = Column(String(100))  # Ex: "Geladeira", "Notebook"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    energy_readings = relationship("EnergyReading", back_populates="device")
    daily_reports = relationship("DailyReport", back_populates="device")


class EnergyReading(Base):
    """Modelo para leituras de consumo de energia"""
    
    __tablename__ = "energy_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    power_watts = Column(Float, nullable=False)  # Consumo instantâneo em watts
    voltage = Column(Float)  # Voltagem
    current = Column(Float)  # Corrente em amperes
    energy_today_kwh = Column(Float)  # Energia consumida hoje em kWh
    energy_total_kwh = Column(Float)  # Energia total consumida em kWh
    
    # Relacionamentos
    device = relationship("Device", back_populates="energy_readings")


class DailyReport(Base):
    """Modelo para relatórios diários de consumo"""
    
    __tablename__ = "daily_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    total_energy_kwh = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    peak_power_watts = Column(Float)
    average_power_watts = Column(Float)
    min_power_watts = Column(Float)
    runtime_hours = Column(Float)
    is_anomaly_detected = Column(Boolean, default=False)
    anomaly_description = Column(Text)
    
    # Relacionamentos
    device = relationship("Device", back_populates="daily_reports")


class Alert(Base):
    """Modelo para alertas do sistema"""
    
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    alert_type = Column(String(50), nullable=False)  # "ANOMALY", "HIGH_COST", "DEVICE_OFFLINE"
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="MEDIUM")  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Relacionamentos
    device = relationship("Device")


# Configuração do banco de dados
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Função para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Criar todas as tabelas no banco de dados"""
    Base.metadata.create_all(bind=engine)
