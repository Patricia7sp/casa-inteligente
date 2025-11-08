"""
Serviço de análise e processamento de dados de consumo de energia
NOTA: Temporariamente simplificado durante migração para Supabase
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.utils.config import settings

logger = logging.getLogger(__name__)


def get_device_weekly_consumption(device_id: int, weeks: int = 1) -> List[Dict]:
    """Obter consumo semanal de um dispositivo - TEMPORARIAMENTE DESABILITADO"""
    logger.warning(
        "get_device_weekly_consumption temporariamente desabilitado durante migração"
    )
    return []


def get_device_monthly_stats(device_id: int) -> Dict:
    """Obter estatísticas mensais de um dispositivo - TEMPORARIAMENTE DESABILITADO"""
    logger.warning(
        "get_device_monthly_stats temporariamente desabilitado durante migração"
    )
    return {}


def get_devices_ranking(period_days: int = 30) -> List[Dict]:
    """Obter ranking de dispositivos por consumo - TEMPORARIAMENTE DESABILITADO"""
    logger.warning("get_devices_ranking temporariamente desabilitado durante migração")
    return []


class EnergyAnalysisService:
    """Serviço responsável por analisar dados de consumo de energia"""

    def __init__(self):
        self.cost_per_kwh = settings.energy_cost_per_kwh

    def calculate_daily_consumption(
        self, device_id: int, date: datetime
    ) -> Optional[Dict]:
        """Calcular consumo diário de um dispositivo - TEMPORARIAMENTE DESABILITADO"""
        logger.warning(
            "calculate_daily_consumption temporariamente desabilitado durante migração"
        )
        return None

    def detect_anomalies(
        self, device_id: int, threshold: float = 1.5
    ) -> Optional[Dict]:
        """Detectar anomalias no consumo - TEMPORARIAMENTE DESABILITADO"""
        logger.warning("detect_anomalies temporariamente desabilitado durante migração")
        return None

    def generate_daily_report(self, date: datetime = None) -> Dict:
        """Gerar relatório diário - TEMPORARIAMENTE DESABILITADO"""
        logger.warning(
            "generate_daily_report temporariamente desabilitado durante migração"
        )
        if date is None:
            date = datetime.utcnow()
        return {
            "date": date.strftime("%Y-%m-%d"),
            "devices": [],
            "total_consumption_kwh": 0.0,
            "total_cost_brl": 0.0,
            "message": "Relatório temporariamente desabilitado durante migração para Supabase",
        }

    def get_consumption_trends(self, device_id: int, days: int = 30) -> Optional[Dict]:
        """Obter tendências de consumo - TEMPORARIAMENTE DESABILITADO"""
        logger.warning(
            "get_consumption_trends temporariamente desabilitado durante migração"
        )
        return None

    def get_realtime_status(self) -> Dict:
        """Obter status em tempo real - TEMPORARIAMENTE DESABILITADO"""
        logger.warning(
            "get_realtime_status temporariamente desabilitado durante migração"
        )
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "devices": [],
            "total_power_watts": 0.0,
            "message": "Status temporariamente desabilitado durante migração para Supabase",
        }


# Instância global do serviço
energy_service = EnergyAnalysisService()
