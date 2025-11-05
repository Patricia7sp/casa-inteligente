"""
Configurações do sistema Casa Inteligente
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Configurações principais da aplicação"""
    
    # Informações da Aplicação
    app_name: str = "Casa Inteligente"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Banco de Dados PostgreSQL
    database_url: str = "postgresql://postgres:casa_inteligente_2024@localhost:5432/casa_inteligente"
    redis_url: str = "redis://localhost:6379"
    
    # APIs de Tomadas
    tapo_username: str = ""
    tapo_password: str = ""
    tapo_devices: List[str] = []
    
    # Tuya Cloud (NovaDigital usa plataforma Tuya)
    tuya_access_id: str = ""
    tuya_access_key: str = ""
    tuya_region: str = "us"
    
    # Tuya Local (opcional - para controle local)
    tuya_device_id: str = ""
    tuya_local_key: str = ""
    tuya_ip_address: str = ""
    
    # Configuração de Energia
    energy_cost_per_kwh: float = 0.85  # R$ por kWh
    
    # Notificações
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    email_smtp_server: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_recipients: List[str] = []
    
    # LLM
    openai_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None
    
    # Monitoramento
    collection_interval_minutes: int = 15
    report_time: str = "20:00"  # Horário dos relatórios diários
    
    # Alertas
    anomaly_threshold: float = 2.0  # Multiplicador da média para detectar anomalias
    max_daily_cost: float = 50.0  # Alerta se o custo diário passar deste valor
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instância global de configurações
settings = Settings()
