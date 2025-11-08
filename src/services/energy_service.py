"""
Serviço de análise e processamento de dados de consumo de energia
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import pandas as pd
import numpy as np

from src.models.database import Device, EnergyReading, DailyReport, Alert, get_db
from src.utils.config import settings

logger = logging.getLogger(__name__)


def get_device_weekly_consumption(device_id: int, weeks: int = 1) -> List[Dict]:
    """Obter consumo semanal de um dispositivo"""
    try:
        db = next(get_db())
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks)

        readings = (
            db.query(
                func.date(EnergyReading.timestamp).label("date"),
                func.sum(EnergyReading.power_watts).label("total_power"),
            )
            .filter(
                and_(
                    EnergyReading.device_id == device_id,
                    EnergyReading.timestamp >= start_date,
                    EnergyReading.timestamp <= end_date,
                )
            )
            .group_by(func.date(EnergyReading.timestamp))
            .order_by(func.date(EnergyReading.timestamp))
            .all()
        )

        result = []
        for date, total_power in readings:
            energy_kwh = (total_power / 1000) / 60  # Converter para kWh
            result.append(
                {
                    "date": str(date),
                    "consumption_kwh": round(energy_kwh, 3),
                    "cost_brl": round(energy_kwh * settings.energy_cost_per_kwh, 2),
                }
            )

        db.close()
        return result
    except Exception as e:
        logger.error(f"Erro ao obter consumo semanal: {e}")
        return []


def get_device_monthly_stats(device_id: int) -> Dict:
    """Obter estatísticas mensais de um dispositivo"""
    try:
        db = next(get_db())
        end_date = datetime.now()
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        readings = (
            db.query(EnergyReading)
            .filter(
                and_(
                    EnergyReading.device_id == device_id,
                    EnergyReading.timestamp >= start_date,
                    EnergyReading.timestamp <= end_date,
                )
            )
            .all()
        )

        if not readings:
            db.close()
            return {}

        df = pd.DataFrame(
            [{"timestamp": r.timestamp, "power_watts": r.power_watts} for r in readings]
        )

        total_energy_kwh = (df["power_watts"].sum() / 1000) / 60
        runtime_hours = len(df[df["power_watts"] > 0]) / 60

        db.close()
        return {
            "device_id": device_id,
            "month": start_date.strftime("%Y-%m"),
            "total_energy_kwh": round(total_energy_kwh, 3),
            "total_cost_brl": round(total_energy_kwh * settings.energy_cost_per_kwh, 2),
            "runtime_hours": round(runtime_hours, 1),
            "avg_daily_kwh": round(total_energy_kwh / end_date.day, 3),
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas mensais: {e}")
        return {}


def get_devices_ranking(period_days: int = 30) -> List[Dict]:
    """Obter ranking de dispositivos por consumo"""
    try:
        db = next(get_db())
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        rankings = (
            db.query(
                Device.id,
                Device.name,
                Device.location,
                func.sum(EnergyReading.power_watts).label("total_power"),
            )
            .join(EnergyReading, Device.id == EnergyReading.device_id)
            .filter(
                and_(
                    EnergyReading.timestamp >= start_date,
                    EnergyReading.timestamp <= end_date,
                )
            )
            .group_by(Device.id, Device.name, Device.location)
            .order_by(func.sum(EnergyReading.power_watts).desc())
            .all()
        )

        result = []
        for rank, (device_id, name, location, total_power) in enumerate(rankings, 1):
            energy_kwh = (total_power / 1000) / 60
            result.append(
                {
                    "rank": rank,
                    "device_id": device_id,
                    "device_name": name,
                    "location": location,
                    "consumption_kwh": round(energy_kwh, 3),
                    "cost_brl": round(energy_kwh * settings.energy_cost_per_kwh, 2),
                }
            )

        db.close()
        return result
    except Exception as e:
        logger.error(f"Erro ao obter ranking: {e}")
        return []


class EnergyAnalysisService:
    """Serviço responsável por analisar dados de consumo de energia"""

    def __init__(self):
        self.cost_per_kwh = settings.energy_cost_per_kwh

    def calculate_daily_consumption(
        self, device_id: int, date: datetime
    ) -> Optional[Dict]:
        """
        Calcular consumo diário de um dispositivo

        Args:
            device_id: ID do dispositivo
            date: Data para análise

        Returns:
            Dict com estatísticas do consumo diário
        """
        try:
            db = next(get_db())

            # Obter leituras do dia
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)

            readings = (
                db.query(EnergyReading)
                .filter(
                    and_(
                        EnergyReading.device_id == device_id,
                        EnergyReading.timestamp >= start_date,
                        EnergyReading.timestamp < end_date,
                    )
                )
                .all()
            )

            if not readings:
                logger.warning(
                    f"Nenhuma leitura encontrada para o dispositivo {device_id} na data {date}"
                )
                return None

            # Converter para DataFrame para análise
            df = pd.DataFrame(
                [
                    {
                        "timestamp": r.timestamp,
                        "power_watts": r.power_watts,
                        "voltage": r.voltage,
                        "current": r.current,
                    }
                    for r in readings
                ]
            )

            # Calcular estatísticas
            total_energy_kwh = (
                df["power_watts"].sum() / 1000 / 60
            )  # Converter para kWh (assumindo leituras por minuto)
            total_cost = total_energy_kwh * self.cost_per_kwh
            peak_power = df["power_watts"].max()
            avg_power = df["power_watts"].mean()
            min_power = df["power_watts"].min()

            # Calcular tempo de funcionamento (horas com consumo > 0)
            runtime_hours = (
                len(df[df["power_watts"] > 0]) / 60
            )  # Assumindo leituras por minuto

            result = {
                "device_id": device_id,
                "date": date,
                "total_energy_kwh": total_energy_kwh,
                "total_cost": total_cost,
                "peak_power_watts": peak_power,
                "average_power_watts": avg_power,
                "min_power_watts": min_power,
                "runtime_hours": runtime_hours,
                "readings_count": len(readings),
            }

            db.close()
            return result

        except Exception as e:
            logger.error(f"Erro ao calcular consumo diário: {str(e)}")
            return None

    def detect_anomalies(
        self, device_id: int, current_consumption: float
    ) -> Optional[Dict]:
        """
        Detectar anomalias no consumo de energia

        Args:
            device_id: ID do dispositivo
            current_consumption: Consumo atual em watts

        Returns:
            Dict com informações da anomalia ou None
        """
        try:
            db = next(get_db())

            # Obter média dos últimos 7 dias
            seven_days_ago = datetime.utcnow() - timedelta(days=7)

            avg_consumption = (
                db.query(func.avg(EnergyReading.power_watts))
                .filter(
                    and_(
                        EnergyReading.device_id == device_id,
                        EnergyReading.timestamp >= seven_days_ago,
                    )
                )
                .scalar()
            )

            if avg_consumption is None:
                return None

            # Verificar se consumo atual é significativamente maior que a média
            threshold_multiplier = settings.anomaly_threshold

            if current_consumption > avg_consumption * threshold_multiplier:
                anomaly = {
                    "device_id": device_id,
                    "current_consumption": current_consumption,
                    "average_consumption": avg_consumption,
                    "threshold": avg_consumption * threshold_multiplier,
                    "anomaly_factor": current_consumption / avg_consumption,
                    "description": f"Consumo {current_consumption:.2f}W é {current_consumption/avg_consumption:.1f}x maior que a média de {avg_consumption:.2f}W",
                }

                logger.warning(
                    f"Anomalia detectada no dispositivo {device_id}: {anomaly['description']}"
                )
                return anomaly

            db.close()
            return None

        except Exception as e:
            logger.error(f"Erro ao detectar anomalias: {str(e)}")
            return None

    def generate_daily_report(self, date: datetime = None) -> Dict:
        """
        Gerar relatório diário completo

        Args:
            date: Data do relatório (padrão: hoje)

        Returns:
            Dict com relatório completo
        """
        if date is None:
            date = datetime.utcnow()

        try:
            db = next(get_db())

            # Obter todos os dispositivos ativos
            devices = db.query(Device).filter(Device.is_active == True).all()

            report = {
                "date": date,
                "devices": [],
                "total_energy_kwh": 0,
                "total_cost": 0,
                "anomalies": [],
            }

            for device in devices:
                # Calcular consumo do dispositivo
                device_stats = self.calculate_daily_consumption(device.id, date)

                if device_stats:
                    # Detectar anomalias
                    anomaly = self.detect_anomalies(
                        device.id, device_stats["average_power_watts"]
                    )

                    device_report = {
                        "device_name": device.name,
                        "device_type": device.type,
                        "location": device.location,
                        "equipment": device.equipment_connected,
                        **device_stats,
                    }

                    if anomaly:
                        device_report["anomaly"] = anomaly
                        report["anomalies"].append(anomaly)

                    report["devices"].append(device_report)
                    report["total_energy_kwh"] += device_stats["total_energy_kwh"]
                    report["total_cost"] += device_stats["total_cost"]

            # Salvar relatório no banco
            for device_report in report["devices"]:
                daily_report = DailyReport(
                    device_id=device_report["device_id"],
                    date=date,
                    total_energy_kwh=device_report["total_energy_kwh"],
                    total_cost=device_report["total_cost"],
                    peak_power_watts=device_report["peak_power_watts"],
                    average_power_watts=device_report["average_power_watts"],
                    min_power_watts=device_report["min_power_watts"],
                    runtime_hours=device_report["runtime_hours"],
                    is_anomaly_detected="anomaly" in device_report,
                    anomaly_description=device_report.get("anomaly", {}).get(
                        "description"
                    ),
                )
                db.add(daily_report)

            db.commit()
            db.close()

            logger.info(
                f"Relatório diário gerado para {date}: {report['total_energy_kwh']:.3f} kWh, R$ {report['total_cost']:.2f}"
            )
            return report

        except Exception as e:
            logger.error(f"Erro ao gerar relatório diário: {str(e)}")
            return {"error": str(e)}

    def get_consumption_trends(self, device_id: int, days: int = 30) -> Optional[Dict]:
        """
        Obter tendências de consumo de um dispositivo

        Args:
            device_id: ID do dispositivo
            days: Número de dias para análise

        Returns:
            Dict com tendências de consumo
        """
        try:
            db = next(get_db())

            # Obter relatórios diários
            start_date = datetime.utcnow() - timedelta(days=days)

            reports = (
                db.query(DailyReport)
                .filter(
                    and_(
                        DailyReport.device_id == device_id,
                        DailyReport.date >= start_date,
                    )
                )
                .order_by(DailyReport.date.desc())
                .all()
            )

            if not reports:
                return None

            # Converter para DataFrame
            df = pd.DataFrame(
                [
                    {
                        "date": r.date,
                        "energy_kwh": r.total_energy_kwh,
                        "cost": r.total_cost,
                        "peak_power": r.peak_power_watts,
                    }
                    for r in reports
                ]
            )

            # Calcular tendências
            trends = {
                "period_days": days,
                "total_energy_kwh": df["energy_kwh"].sum(),
                "total_cost": df["cost"].sum(),
                "average_daily_energy_kwh": df["energy_kwh"].mean(),
                "average_daily_cost": df["cost"].mean(),
                "max_daily_energy_kwh": df["energy_kwh"].max(),
                "min_daily_energy_kwh": df["energy_kwh"].min(),
                "trend_direction": "stable",  # TODO: Implementar cálculo de tendência
            }

            db.close()
            return trends

        except Exception as e:
            logger.error(f"Erro ao obter tendências de consumo: {str(e)}")
            return None

    def get_realtime_status(self) -> Dict:
        """
        Obter status em tempo real de todos os dispositivos

        Returns:
            Dict com status atual
        """
        try:
            db = next(get_db())

            # Obter última leitura de cada dispositivo (incluir is_active=None para TAPO)
            devices = (
                db.query(Device)
                .filter((Device.is_active == True) | (Device.is_active == None))
                .all()
            )

            status = {
                "timestamp": datetime.utcnow(),
                "devices": [],
                "total_current_power_watts": 0,
                "active_devices": 0,
            }

            for device in devices:
                # Obter última leitura
                latest_reading = (
                    db.query(EnergyReading)
                    .filter(EnergyReading.device_id == device.id)
                    .order_by(EnergyReading.timestamp.desc())
                    .first()
                )

                # Calcular energia de hoje
                today_start = datetime.utcnow().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                energy_today = (
                    db.query(EnergyReading)
                    .filter(
                        EnergyReading.device_id == device.id,
                        EnergyReading.timestamp >= today_start,
                    )
                    .with_entities(db.func.sum(EnergyReading.energy_kwh).label("total"))
                    .scalar()
                    or 0
                )

                if latest_reading:
                    device_status = {
                        "device_id": device.id,
                        "device_name": device.name,
                        "location": device.location,
                        "equipment": device.equipment_connected,
                        "current_power_watts": latest_reading.power_watts,
                        "energy_today_kwh": float(energy_today),
                        "last_reading": latest_reading.timestamp,
                        "is_active": latest_reading.power_watts > 0,
                    }

                    status["devices"].append(device_status)
                    status["total_current_power_watts"] += latest_reading.power_watts

                    if latest_reading.power_watts > 0:
                        status["active_devices"] += 1

            db.close()
            return status

        except Exception as e:
            logger.error(f"Erro ao obter status em tempo real: {str(e)}")
            return {"error": str(e)}


# Instância global do serviço
energy_service = EnergyAnalysisService()
