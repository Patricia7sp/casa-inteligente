"""
Serviço de análise e processamento de dados de consumo de energia
NOTA: Temporariamente simplificado durante migração para Supabase

Este módulo também concentra a lógica de agregação, projeção e detecção de
anomalias que originalmente vivia em `dashboard.py` (Streamlit), agora
portada como funções puras para ser consumida pelos endpoints `/energy/*`
e `/smartlife/latest` de `src/main.py`.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from src.services.supabase_client import get_supabase_data
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


# ---------------------------------------------------------------------------
# Identidade visual / classificação de dispositivos TAPO
#
# Portado de dashboard.py (TAPO_DEVICE_PROFILES, classify_tapo_device,
# get_profile_color, get_profile_label, get_profile_icon, build_color_map).
# ---------------------------------------------------------------------------

TAPO_DEVICE_PROFILES = {
    "purificador": {
        "label": "Purificador",
        "aliases": ["tomada inteligente - purificador"],
        "keywords": ["purificador"],
        "icon": "🌬️",
        "color": "#667eea",
    },
    "notebook": {
        "label": "Notebook",
        "aliases": ["tomada inteligente - notebook"],
        "keywords": ["notebook"],
        "icon": "💻",
        "color": "#764ba2",
    },
}

TAPO_COLOR_FALLBACK = "#f093fb"


def classify_tapo_device(device: dict) -> Optional[str]:
    """Classificar dispositivo TAPO com base em nome/equipamento."""

    name = (device.get("name") or "").lower()
    equipment = (device.get("equipment_connected") or "").lower()

    for profile_key, profile in TAPO_DEVICE_PROFILES.items():
        # Verificar aliases exatos
        if any(alias in name for alias in profile.get("aliases", [])):
            return profile_key

        # Verificar palavras-chave em nome ou equipamento
        if any(keyword in name for keyword in profile.get("keywords", [])):
            return profile_key
        if any(keyword in equipment for keyword in profile.get("keywords", [])):
            return profile_key

    return None


def get_profile_color(profile_key: Optional[str]) -> str:
    """Obter cor padrão para o perfil TAPO informado."""

    return TAPO_DEVICE_PROFILES.get(profile_key, {}).get("color", TAPO_COLOR_FALLBACK)


def get_profile_label(profile_key: Optional[str], default: str) -> str:
    """Obter rótulo amigável para o perfil TAPO."""

    return TAPO_DEVICE_PROFILES.get(profile_key, {}).get("label", default)


def get_profile_icon(profile_key: Optional[str]) -> str:
    """Obter ícone representativo do perfil TAPO."""

    return TAPO_DEVICE_PROFILES.get(profile_key, {}).get("icon", "🔌")


def build_color_map(devices: List[dict]) -> Dict[str, str]:
    """Construir mapa nome -> cor para gráficos."""

    color_map: Dict[str, str] = {}
    for device in devices:
        name = (
            device.get("device_name")
            or device.get("display_name")
            or device.get("name")
        )
        profile_key = device.get("profile_key")
        if not name:
            continue
        color_map[name] = get_profile_color(profile_key)
    return color_map


def get_tapo_devices(raw_devices: List[Dict]) -> List[Dict]:
    """Filtrar e enriquecer dispositivos TAPO reconhecidos a partir da lista bruta do Supabase.

    Replica o filtro usado em dashboard.py:render_tapo_dashboard: descarta
    dispositivos explicitamente inativos (is_active is False) e mantém apenas
    os que batem em `classify_tapo_device`. Cada dispositivo retornado ganha
    profile_key/profile_label/icon/color/display_name.
    """

    tapo_devices: List[Dict] = []
    for raw_device in raw_devices or []:
        is_active = raw_device.get("is_active")
        if is_active is False:
            continue

        profile_key = classify_tapo_device(raw_device)
        if not profile_key:
            continue

        device = dict(raw_device)
        profile_label = get_profile_label(
            profile_key, device.get("name", "Dispositivo TAPO")
        )
        icon = get_profile_icon(profile_key)

        device["profile_key"] = profile_key
        device["profile_label"] = profile_label
        device["icon"] = icon
        device["color"] = get_profile_color(profile_key)
        device["display_name"] = f"{icon} {profile_label}"
        # Garantir que is_active seja True para compatibilidade (is_active None -> ativo)
        if device.get("is_active") is None:
            device["is_active"] = True

        tapo_devices.append(device)

    return tapo_devices


# ---------------------------------------------------------------------------
# Busca de dados no Supabase (única camada com efeito de rede deste módulo)
# ---------------------------------------------------------------------------


def fetch_tapo_devices_and_readings(
    days: int = 90,
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Buscar dispositivos e leituras de energia do Supabase.

    Replica o fluxo de render_tapo_dashboard: busca todos os `devices`,
    filtra os reconhecidos como TAPO, busca `energy_readings` dos últimos
    `days` dias (order=timestamp.desc, limit=10000) e mantém apenas as
    leituras pertencentes a dispositivos TAPO.

    Returns:
        Tupla (tapo_devices, tapo_readings, raw_devices). `raw_devices` é a
        lista bruta de dispositivos retornada pelo Supabase (útil para
        distinguir "sem dispositivos cadastrados" de "Supabase indisponível"
        nos endpoints que expõem esse status).
    """

    raw_devices = get_supabase_data("devices")
    tapo_devices = get_tapo_devices(raw_devices)
    tapo_ids = {device["id"] for device in tapo_devices}

    from_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
    raw_readings = get_supabase_data(
        "energy_readings",
        params={
            "order": "timestamp.desc",
            "timestamp": f"gte.{from_date}",
            "limit": "10000",
        },
    )

    tapo_readings = [
        reading for reading in raw_readings if reading.get("device_id") in tapo_ids
    ]

    return tapo_devices, tapo_readings, raw_devices


# ---------------------------------------------------------------------------
# Helpers internos de DataFrame
# ---------------------------------------------------------------------------


def _now_naive() -> datetime:
    """Momento atual sem timezone, para comparação com timestamps do Supabase.

    Replica o uso de `datetime.now()` em dashboard.py (sem normalização para
    UTC), mantendo o mesmo comportamento observável do dashboard original.
    """

    return datetime.now()


def _readings_dataframe(readings: List[Dict]) -> pd.DataFrame:
    """Converter lista de leituras em DataFrame com timestamp parseado (sem timezone)."""

    if not readings:
        return pd.DataFrame()

    df = pd.DataFrame(readings)
    if "timestamp" not in df.columns:
        return pd.DataFrame()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    if isinstance(df["timestamp"].dtype, pd.DatetimeTZDtype):
        df["timestamp"] = df["timestamp"].dt.tz_localize(None)
    df = df.dropna(subset=["timestamp"])

    return df


def _latest_power_by_device(readings: List[Dict]) -> Dict[int, float]:
    """Obter a potência da leitura mais recente por device_id."""

    df = _readings_dataframe(readings)
    if df.empty or "device_id" not in df.columns or "power_watts" not in df.columns:
        return {}

    df = df.sort_values("timestamp").drop_duplicates("device_id", keep="last")
    powers = pd.to_numeric(df["power_watts"], errors="coerce").fillna(0.0)
    return dict(zip(df["device_id"], powers))


# ---------------------------------------------------------------------------
# GET /energy/overview
# ---------------------------------------------------------------------------


def build_energy_overview(
    tapo_devices: List[Dict],
    tapo_readings: List[Dict],
    raw_devices: Optional[List[Dict]] = None,
) -> Dict:
    """Construir o payload de /energy/overview a partir de dados já buscados."""

    latest_power = _latest_power_by_device(tapo_readings)

    device_payloads = []
    total_power = 0.0
    active_count = 0

    for device in tapo_devices:
        current_power = latest_power.get(device["id"])
        if current_power is None:
            current_power = float(device.get("current_power_watts") or 0.0)
        current_power = float(current_power)

        is_active = bool(device.get("is_active"))
        if is_active:
            total_power += current_power
            active_count += 1

        device_payloads.append(
            {
                "id": device["id"],
                "name": device.get("name"),
                "display_name": device["display_name"],
                "profile_key": device["profile_key"],
                "icon": device["icon"],
                "color": device["color"],
                "location": device.get("location"),
                "equipment_connected": device.get("equipment_connected"),
                "ip_address": device.get("ip_address"),
                "is_active": is_active,
                "current_power_watts": round(current_power, 2),
            }
        )

    last_reading_minutes_ago = None
    df = _readings_dataframe(tapo_readings)
    if not df.empty:
        last_timestamp = df["timestamp"].max()
        if pd.notna(last_timestamp):
            last_reading_minutes_ago = max(
                int((_now_naive() - last_timestamp).total_seconds() // 60), 0
            )

    # NOTA (decisão de design): get_supabase_data retorna [] tanto para "sem
    # linhas" quanto para erro de rede/HTTP, então não há como distinguir os
    # dois casos com certeza aqui. Usamos como heurística: se a busca de
    # dispositivos brutos não retornou nada, tratamos como Supabase
    # indisponível (no contexto deste sistema sempre há dispositivos
    # cadastrados).
    source = "supabase" if raw_devices else "unavailable"

    return {
        "summary": {
            "total_power_watts": round(total_power, 2),
            "active_devices": active_count,
            "total_devices": len(tapo_devices),
            "last_reading_minutes_ago": last_reading_minutes_ago,
            "source": source,
        },
        "devices": device_payloads,
    }


# ---------------------------------------------------------------------------
# GET /energy/history
# ---------------------------------------------------------------------------


def build_power_history(
    tapo_devices: List[Dict], tapo_readings: List[Dict]
) -> List[Dict]:
    """Construir séries de potência instantânea por dispositivo para /energy/history."""

    df = _readings_dataframe(tapo_readings)

    series = []
    for device in tapo_devices:
        device_id = device["id"]
        points: List[Dict] = []

        if not df.empty and "device_id" in df.columns:
            device_df = df[df["device_id"] == device_id].sort_values("timestamp")
            if not device_df.empty:
                powers = pd.to_numeric(
                    device_df["power_watts"], errors="coerce"
                ).fillna(0.0)
                points = [
                    {"timestamp": ts.isoformat(), "power_watts": round(float(p), 2)}
                    for ts, p in zip(device_df["timestamp"], powers)
                ]

        series.append(
            {
                "device_id": device_id,
                "display_name": device["display_name"],
                "color": device["color"],
                "points": points,
            }
        )

    return series


# ---------------------------------------------------------------------------
# Agregação por período (portado de dashboard.py:aggregate_energy_data)
# ---------------------------------------------------------------------------


def aggregate_energy_by_period(readings: List[Dict], freq: str = "D") -> pd.DataFrame:
    """Agregar leituras de energia por período (dia='D' ou mês='M') e dispositivo.

    Réplica de dashboard.py:aggregate_energy_data. Quando a coluna
    `energy_today_kwh` está presente (contador acumulado do dia, resetado à
    meia-noite), usa o MÁXIMO por período/dispositivo. Caso contrário,
    estima a energia a partir da potência média (kWh = W * horas / 1000) e
    soma por período/dispositivo.
    """

    if not readings:
        return pd.DataFrame()

    df = pd.DataFrame(readings)
    if "timestamp" not in df.columns:
        return pd.DataFrame()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    if isinstance(df["timestamp"].dtype, pd.DatetimeTZDtype):
        df["timestamp"] = df["timestamp"].dt.tz_localize(None)
    df = df.dropna(subset=["timestamp"])

    if df.empty:
        return pd.DataFrame()

    df["period"] = df["timestamp"].dt.to_period(freq)

    if "energy_today_kwh" in df.columns:
        df["energy_today_kwh"] = pd.to_numeric(df["energy_today_kwh"], errors="coerce")
        aggregated = (
            df.groupby(["period", "device_id"])
            .agg(
                energy_today_kwh=("energy_today_kwh", "max"),
                power_watts=("power_watts", "mean"),
            )
            .reset_index()
        )
    else:
        hours_in_period = {"H": 1, "D": 24, "M": 720}
        df["energy_kwh"] = (
            pd.to_numeric(df["power_watts"], errors="coerce")
            * hours_in_period.get(freq, 24)
            / 1000
        )
        aggregated = (
            df.groupby(["period", "device_id"])
            .agg(
                energy_kwh=("energy_kwh", "sum"),
                power_watts=("power_watts", "mean"),
            )
            .reset_index()
        )

    aggregated["period"] = aggregated["period"].dt.to_timestamp()
    return aggregated


# ---------------------------------------------------------------------------
# GET /energy/daily
# ---------------------------------------------------------------------------


def build_daily_totals(readings: List[Dict], tariff: Optional[float] = None) -> Dict:
    """Construir o payload de /energy/daily: totais diários somados entre dispositivos.

    Portado de dashboard.py:create_daily_consumption_timeline / bloco de
    "Resumo de Totais Agregados" em render_tapo_dashboard.
    """

    tariff_value = settings.energy_cost_per_kwh if tariff is None else tariff

    daily_agg = aggregate_energy_by_period(readings, freq="D")
    if daily_agg.empty:
        return {
            "daily": [],
            "totals": {
                "avg_daily_kwh": 0.0,
                "avg_daily_cost_brl": 0.0,
                "last7_kwh": 0.0,
                "last7_cost_brl": 0.0,
                "last30_kwh": 0.0,
                "last30_cost_brl": 0.0,
            },
        }

    energy_col = (
        "energy_today_kwh" if "energy_today_kwh" in daily_agg.columns else "energy_kwh"
    )

    daily_totals = (
        daily_agg.groupby("period")[energy_col]
        .sum()
        .reset_index()
        .sort_values("period")
    )
    daily_totals["cost"] = daily_totals[energy_col] * tariff_value

    daily_list = [
        {
            "date": row["period"].strftime("%Y-%m-%d"),
            "energy_kwh": round(float(row[energy_col]), 3),
            "cost_brl": round(float(row["cost"]), 2),
        }
        for _, row in daily_totals.iterrows()
    ]

    avg_daily_kwh = float(daily_totals[energy_col].mean())
    avg_daily_cost = avg_daily_kwh * tariff_value

    now = _now_naive()
    last7 = daily_totals[daily_totals["period"] >= (now - timedelta(days=7))]
    last30 = daily_totals[daily_totals["period"] >= (now - timedelta(days=30))]

    last7_kwh = float(last7[energy_col].sum())
    last30_kwh = float(last30[energy_col].sum())

    return {
        "daily": daily_list,
        "totals": {
            "avg_daily_kwh": round(avg_daily_kwh, 3),
            "avg_daily_cost_brl": round(avg_daily_cost, 2),
            "last7_kwh": round(last7_kwh, 3),
            "last7_cost_brl": round(last7_kwh * tariff_value, 2),
            "last30_kwh": round(last30_kwh, 3),
            "last30_cost_brl": round(last30_kwh * tariff_value, 2),
        },
    }


# ---------------------------------------------------------------------------
# GET /energy/monthly
# ---------------------------------------------------------------------------


def build_monthly_totals(readings: List[Dict], tariff: Optional[float] = None) -> Dict:
    """Construir o payload de /energy/monthly: totais mensais somados entre dispositivos.

    Portado de dashboard.py:create_monthly_totals_chart.
    """

    tariff_value = settings.energy_cost_per_kwh if tariff is None else tariff

    monthly_agg = aggregate_energy_by_period(readings, freq="M")
    if monthly_agg.empty:
        return {"monthly": []}

    energy_col = (
        "energy_today_kwh"
        if "energy_today_kwh" in monthly_agg.columns
        else "energy_kwh"
    )

    monthly_totals = (
        monthly_agg.groupby("period")[energy_col]
        .sum()
        .reset_index()
        .sort_values("period")
    )
    monthly_totals["cost"] = monthly_totals[energy_col] * tariff_value

    monthly_list = []
    for _, row in monthly_totals.iterrows():
        period = row["period"]
        monthly_list.append(
            {
                "month": period.strftime("%Y-%m"),
                # Mesmo formato usado em dashboard.py (strftime('%b/%Y')),
                # abreviação de mês no locale padrão do processo.
                "label": period.strftime("%b/%Y"),
                "energy_kwh": round(float(row[energy_col]), 3),
                "cost_brl": round(float(row["cost"]), 2),
            }
        )

    return {"monthly": monthly_list}


# ---------------------------------------------------------------------------
# GET /energy/projections
# ---------------------------------------------------------------------------


def _estimate_daily_energy_kwh(
    readings_df: pd.DataFrame, device_id, current_power_watts: float, now: datetime
) -> float:
    """Estimar energia diária (kWh) de um dispositivo.

    Réplica da cadeia de fallback usada em render_tapo_dashboard para as
    projeções: média diária de energy_today_kwh dos últimos 7 dias -> média
    de todos os dias disponíveis -> potência atual * 24 / 1000.
    """

    if (
        readings_df is not None
        and not readings_df.empty
        and "energy_today_kwh" in readings_df.columns
    ):
        device_readings = readings_df[readings_df["device_id"] == device_id]
        if not device_readings.empty:
            last_7_days = device_readings[
                device_readings["timestamp"] >= (now - timedelta(days=7))
            ]
            if not last_7_days.empty:
                value = last_7_days["energy_today_kwh"].mean()
                if pd.notna(value):
                    return float(value)

            value = device_readings["energy_today_kwh"].mean()
            if pd.notna(value):
                return float(value)

    current_power = float(current_power_watts or 0.0)
    return current_power * 24 / 1000


def build_projections(
    tapo_devices: List[Dict], tapo_readings: List[Dict], tariff: Optional[float] = None
) -> Dict:
    """Construir o payload de /energy/projections: projeções diária/semanal/mensal por dispositivo.

    Portado do bloco "Projeções de Consumo e Custo" em
    dashboard.py:render_tapo_dashboard.
    """

    tariff_value = settings.energy_cost_per_kwh if tariff is None else tariff
    now = _now_naive()

    readings_df = _readings_dataframe(tapo_readings)
    if not readings_df.empty and "energy_today_kwh" in readings_df.columns:
        readings_df["energy_today_kwh"] = pd.to_numeric(
            readings_df["energy_today_kwh"], errors="coerce"
        )

    device_results = []
    total_daily = total_weekly = total_monthly = total_cost = 0.0

    for device in tapo_devices:
        device_id = device["id"]
        daily_energy = _estimate_daily_energy_kwh(
            readings_df, device_id, device.get("current_power_watts", 0.0), now
        )
        weekly_energy = daily_energy * 7
        monthly_energy = daily_energy * 30
        monthly_cost = monthly_energy * tariff_value

        device_results.append(
            {
                "device_id": device_id,
                "display_name": device["display_name"],
                "color": device["color"],
                "daily_kwh": round(daily_energy, 3),
                "weekly_kwh": round(weekly_energy, 3),
                "monthly_kwh": round(monthly_energy, 3),
                "monthly_cost_brl": round(monthly_cost, 2),
            }
        )

        total_daily += daily_energy
        total_weekly += weekly_energy
        total_monthly += monthly_energy
        total_cost += monthly_cost

    return {
        "devices": device_results,
        "total": {
            "daily_kwh": round(total_daily, 3),
            "weekly_kwh": round(total_weekly, 3),
            "monthly_kwh": round(total_monthly, 3),
            "monthly_cost_brl": round(total_cost, 2),
        },
    }


# ---------------------------------------------------------------------------
# GET /energy/devices/{device_id}
# ---------------------------------------------------------------------------


def build_device_detail(
    device: Dict, tapo_readings: List[Dict], days: int, tariff: Optional[float] = None
) -> Dict:
    """Construir o payload de /energy/devices/{device_id}.

    Portado do bloco "Monitoramento Individual por Dispositivo" em
    dashboard.py:render_tapo_dashboard, incluindo a detecção de anomalia por
    threshold (média + 2 desvios-padrão, ou média*1.5 se desvio-padrão for
    zero/indisponível).
    """

    tariff_value = settings.energy_cost_per_kwh if tariff is None else tariff
    device_id = device["id"]
    display_name = device["display_name"]
    color = device["color"]
    current_power = float(device.get("current_power_watts") or 0.0)

    now = _now_naive()
    cutoff = now - timedelta(days=days)

    device_readings = [r for r in tapo_readings if r.get("device_id") == device_id]
    df = _readings_dataframe(device_readings)
    if not df.empty:
        df = df[df["timestamp"] >= cutoff]

    if df.empty:
        return {
            "device_id": device_id,
            "display_name": display_name,
            "color": color,
            "current_power_watts": round(current_power, 2),
            "last_reading_minutes_ago": None,
            "energy_today_kwh": None,
            "cost_today_brl": None,
            "avg_power_watts": 0.0,
            "peak_power_watts": 0.0,
            "anomaly": {
                "has_spike": False,
                "message": f"{display_name}: ainda sem leituras recentes.",
            },
            "power_series": [],
            "energy_series": [],
            "cost_series": [],
        }

    df = df.sort_values("timestamp").reset_index(drop=True)
    df["power_watts"] = (
        pd.to_numeric(df["power_watts"], errors="coerce").ffill().fillna(0.0)
    )

    has_energy = "energy_today_kwh" in df.columns
    if has_energy:
        df["energy_today_kwh"] = (
            pd.to_numeric(df["energy_today_kwh"], errors="coerce").ffill().fillna(0.0)
        )
        df["custo_estimado"] = df["energy_today_kwh"] * tariff_value

    last_timestamp = df["timestamp"].iloc[-1]
    minutes_ago = max(int((now - last_timestamp).total_seconds() // 60), 0)

    energy_today = float(df["energy_today_kwh"].iloc[-1]) if has_energy else None
    cost_today = float(df["custo_estimado"].iloc[-1]) if has_energy else None

    power_series_vals = df["power_watts"]
    avg_power = float(power_series_vals.mean())
    std_power_raw = power_series_vals.std()
    std_power = float(std_power_raw) if pd.notna(std_power_raw) else 0.0
    peak_power = float(power_series_vals.max())
    threshold = avg_power + (std_power * 2 if std_power else avg_power * 0.5)

    spike_mask = power_series_vals > threshold
    spike_points = df[spike_mask]

    if not spike_points.empty:
        peak_time = spike_points["timestamp"].iloc[-1].strftime("%d/%m %H:%M")
        message = (
            f"{display_name}: {len(spike_points)} pico(s) acima de {threshold:.1f} W "
            f"(máximo {peak_power:.1f} W às {peak_time})."
        )
        has_spike = True
    else:
        message = (
            f"{display_name}: consumo estável (média {avg_power:.1f} W, "
            f"pico {peak_power:.1f} W)."
        )
        has_spike = False

    power_series = [
        {"timestamp": ts.isoformat(), "power_watts": round(float(p), 2)}
        for ts, p in zip(df["timestamp"], df["power_watts"])
    ]

    energy_series: List[Dict] = []
    cost_series: List[Dict] = []
    if has_energy:
        energy_series = [
            {"timestamp": ts.isoformat(), "energy_today_kwh": round(float(e), 3)}
            for ts, e in zip(df["timestamp"], df["energy_today_kwh"])
        ]
        cost_series = [
            {"timestamp": ts.isoformat(), "cost_estimado": round(float(c), 2)}
            for ts, c in zip(df["timestamp"], df["custo_estimado"])
        ]

    return {
        "device_id": device_id,
        "display_name": display_name,
        "color": color,
        "current_power_watts": round(current_power, 2),
        "last_reading_minutes_ago": minutes_ago,
        "energy_today_kwh": (
            round(energy_today, 3) if energy_today is not None else None
        ),
        "cost_today_brl": round(cost_today, 2) if cost_today is not None else None,
        "avg_power_watts": round(avg_power, 2),
        "peak_power_watts": round(peak_power, 2),
        "anomaly": {"has_spike": has_spike, "message": message},
        "power_series": power_series,
        "energy_series": energy_series,
        "cost_series": cost_series,
    }


# ---------------------------------------------------------------------------
# GET /smartlife/latest
# ---------------------------------------------------------------------------


def load_smartlife_snapshot() -> Dict:
    """Carregar o snapshot mais recente de dados SmartLife.

    Portado de dashboard.py:load_smartlife_data. O caminho de
    `data/smartlife/latest.json` é resolvido a partir da raiz do projeto
    usando a posição deste arquivo (não depende do diretório de trabalho do
    processo). Retorna {} se o arquivo não existir ou estiver corrompido.
    """

    project_root = Path(__file__).resolve().parent.parent.parent
    smartlife_file = project_root / "data" / "smartlife" / "latest.json"

    if not smartlife_file.exists():
        return {}

    try:
        with open(smartlife_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error("Arquivo SmartLife inválido: %s", smartlife_file)
        return {}
