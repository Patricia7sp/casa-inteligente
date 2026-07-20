"""
Testes das funções puras de agregação/projeção/anomalia portadas de
dashboard.py para src/services/energy_service.py.

Estes testes não fazem nenhuma chamada de rede: constroem listas de dicts
simulando o retorno bruto do Supabase (`devices` e `energy_readings`) e
chamam diretamente as funções puras.
"""

from datetime import datetime, timedelta

import pytest

from src.services.energy_service import (
    classify_tapo_device,
    get_tapo_devices,
    build_energy_overview,
    build_power_history,
    aggregate_energy_by_period,
    build_daily_totals,
    build_monthly_totals,
    build_projections,
    build_device_detail,
)


RAW_DEVICES = [
    {
        "id": 1,
        "name": "Tomada Inteligente - Purificador",
        "ip_address": "192.168.1.50",
        "location": "Sala",
        "equipment_connected": "Purificador de ar",
        "is_active": True,
        "current_power_watts": 40.0,
    },
    {
        "id": 2,
        "name": "Tomada Inteligente - Notebook",
        "ip_address": "192.168.1.51",
        "location": "Escritório",
        "equipment_connected": "Notebook Dell",
        "is_active": True,
        "current_power_watts": 65.0,
    },
    {
        # Não deve ser classificado como TAPO -> deve ser ignorado
        "id": 3,
        "name": "Geladeira",
        "ip_address": None,
        "location": "Cozinha",
        "equipment_connected": "Geladeira Consul",
        "is_active": True,
        "current_power_watts": 120.0,
    },
    {
        # Inativo -> deve ser ignorado mesmo classificando
        "id": 4,
        "name": "Tomada Inteligente - Purificador",
        "ip_address": "192.168.1.52",
        "location": "Quarto",
        "equipment_connected": "Purificador",
        "is_active": False,
        "current_power_watts": 30.0,
    },
]


def _make_readings():
    """2 dispositivos, 3 dias de leituras, com um pico artificial de potência."""

    readings = []
    base_day = datetime(2026, 7, 18, 0, 0, 0)  # 3 dias antes de "hoje" (mockado)

    # Dispositivo 1 (purificador): potência estável ~40W, com um pico no dia 3
    for day in range(3):
        day_start = base_day + timedelta(days=day)
        for hour in range(0, 24, 4):
            ts = day_start + timedelta(hours=hour)
            power = 40.0
            if day == 2 and hour == 12:
                power = 500.0  # pico artificial
            energy_today = round((hour + 4) / 24 * 1.0, 3)  # contador acumulado do dia
            readings.append(
                {
                    "device_id": 1,
                    "timestamp": ts.isoformat(),
                    "power_watts": power,
                    "energy_today_kwh": energy_today,
                }
            )

    # Dispositivo 2 (notebook): potência estável ~65W
    for day in range(3):
        day_start = base_day + timedelta(days=day)
        for hour in range(0, 24, 4):
            ts = day_start + timedelta(hours=hour)
            energy_today = round((hour + 4) / 24 * 1.5, 3)
            readings.append(
                {
                    "device_id": 2,
                    "timestamp": ts.isoformat(),
                    "power_watts": 65.0,
                    "energy_today_kwh": energy_today,
                }
            )

    return readings


READINGS = _make_readings()


def test_classify_tapo_device():
    assert classify_tapo_device(RAW_DEVICES[0]) == "purificador"
    assert classify_tapo_device(RAW_DEVICES[1]) == "notebook"
    assert classify_tapo_device(RAW_DEVICES[2]) is None


def test_get_tapo_devices_filters_and_enriches():
    tapo_devices = get_tapo_devices(RAW_DEVICES)

    # Dispositivo 3 (não-TAPO) e 4 (inativo) devem ser excluídos
    ids = {d["id"] for d in tapo_devices}
    assert ids == {1, 2}

    purificador = next(d for d in tapo_devices if d["id"] == 1)
    assert purificador["profile_key"] == "purificador"
    assert purificador["icon"] == "🌬️"
    assert purificador["color"] == "#667eea"
    assert purificador["display_name"] == "🌬️ Purificador"

    notebook = next(d for d in tapo_devices if d["id"] == 2)
    assert notebook["profile_key"] == "notebook"
    assert notebook["color"] == "#764ba2"


def test_build_energy_overview_uses_latest_reading_power():
    tapo_devices = get_tapo_devices(RAW_DEVICES)
    overview = build_energy_overview(tapo_devices, READINGS, RAW_DEVICES)

    assert overview["summary"]["total_devices"] == 2
    assert overview["summary"]["active_devices"] == 2
    assert overview["summary"]["source"] == "supabase"

    device_by_id = {d["id"]: d for d in overview["devices"]}
    # Última leitura do dispositivo 1 no dia 2, hora 20 é 40W (sem pico)
    assert device_by_id[1]["current_power_watts"] == pytest.approx(40.0)
    assert device_by_id[2]["current_power_watts"] == pytest.approx(65.0)


def test_build_power_history_returns_series_per_device():
    tapo_devices = get_tapo_devices(RAW_DEVICES)
    series = build_power_history(tapo_devices, READINGS)

    assert len(series) == 2
    device1_series = next(s for s in series if s["device_id"] == 1)
    assert len(device1_series["points"]) == 18  # 6 leituras/dia * 3 dias
    assert device1_series["color"] == "#667eea"


def test_aggregate_energy_by_period_uses_max_for_energy_and_mean_for_power():
    aggregated = aggregate_energy_by_period(READINGS, freq="D")

    assert not aggregated.empty
    # Para o dispositivo 1 no primeiro dia, o máximo de energy_today_kwh
    # deve corresponder ao valor da última leitura daquele dia (hora=20).
    device1_day1 = aggregated[
        (aggregated["device_id"] == 1)
        & (aggregated["period"] == datetime(2026, 7, 18))
    ]
    assert not device1_day1.empty
    expected_max = round((20 + 4) / 24 * 1.0, 3)
    assert device1_day1.iloc[0]["energy_today_kwh"] == pytest.approx(expected_max)

    # Potência média do dispositivo 1 no dia com pico deve refletir a média
    # (não a soma) incluindo o pico de 500W.
    device1_day3 = aggregated[
        (aggregated["device_id"] == 1)
        & (aggregated["period"] == datetime(2026, 7, 20))
    ]
    powers_day3 = [40.0, 40.0, 40.0, 500.0, 40.0, 40.0]
    assert device1_day3.iloc[0]["power_watts"] == pytest.approx(
        sum(powers_day3) / len(powers_day3)
    )


def test_build_daily_totals_sums_across_devices_and_applies_tariff():
    result = build_daily_totals(READINGS, tariff=0.862)

    assert len(result["daily"]) == 3
    first_day = result["daily"][0]
    assert first_day["date"] == "2026-07-18"

    # Soma do máximo diário de energy_today_kwh entre os 2 dispositivos
    expected_energy = round((20 + 4) / 24 * 1.0, 3) + round((20 + 4) / 24 * 1.5, 3)
    assert first_day["energy_kwh"] == pytest.approx(expected_energy, rel=1e-3)
    # cost_brl é calculado a partir da energia não-arredondada e depois
    # arredondado a 2 casas, então comparamos com tolerância absoluta (evita
    # erro de arredondamento em cascata ao recomputar a partir do valor já
    # arredondado de energy_kwh).
    assert first_day["cost_brl"] == pytest.approx(expected_energy * 0.862, abs=0.01)

    totals = result["totals"]
    assert totals["avg_daily_kwh"] > 0
    assert totals["avg_daily_cost_brl"] == pytest.approx(
        totals["avg_daily_kwh"] * 0.862, abs=0.01
    )


def test_build_monthly_totals_groups_by_month():
    result = build_monthly_totals(READINGS, tariff=0.862)

    # Todas as leituras caem no mesmo mês (julho/2026)
    assert len(result["monthly"]) == 1
    month_entry = result["monthly"][0]
    assert month_entry["month"] == "2026-07"
    assert month_entry["energy_kwh"] > 0
    assert month_entry["cost_brl"] == pytest.approx(
        month_entry["energy_kwh"] * 0.862, abs=0.01
    )


def test_build_projections_uses_average_daily_energy_and_scales_correctly():
    tapo_devices = get_tapo_devices(RAW_DEVICES)
    result = build_projections(tapo_devices, READINGS, tariff=0.862)

    assert len(result["devices"]) == 2

    device1_proj = next(d for d in result["devices"] if d["device_id"] == 1)
    # weekly = daily * 7, monthly = daily * 30, custo = mensal * tarifa
    assert device1_proj["weekly_kwh"] == pytest.approx(
        device1_proj["daily_kwh"] * 7, rel=1e-3
    )
    assert device1_proj["monthly_kwh"] == pytest.approx(
        device1_proj["daily_kwh"] * 30, rel=1e-3
    )
    assert device1_proj["monthly_cost_brl"] == pytest.approx(
        device1_proj["monthly_kwh"] * 0.862, rel=1e-2
    )

    total = result["total"]
    sum_daily = sum(d["daily_kwh"] for d in result["devices"])
    assert total["daily_kwh"] == pytest.approx(sum_daily, rel=1e-3)


def test_build_device_detail_detects_spike_for_device_with_peak():
    tapo_devices = get_tapo_devices(RAW_DEVICES)
    device1 = next(d for d in tapo_devices if d["id"] == 1)

    detail = build_device_detail(device1, READINGS, days=90, tariff=0.862)

    assert detail["device_id"] == 1
    assert detail["anomaly"]["has_spike"] is True
    assert "pico" in detail["anomaly"]["message"].lower()
    assert detail["peak_power_watts"] == pytest.approx(500.0)
    assert len(detail["power_series"]) == 18
    assert len(detail["energy_series"]) == 18
    assert len(detail["cost_series"]) == 18


def test_build_device_detail_reports_stable_consumption_when_no_spike():
    tapo_devices = get_tapo_devices(RAW_DEVICES)
    device2 = next(d for d in tapo_devices if d["id"] == 2)

    detail = build_device_detail(device2, READINGS, days=90, tariff=0.862)

    assert detail["anomaly"]["has_spike"] is False
    assert "estável" in detail["anomaly"]["message"].lower()
    assert detail["avg_power_watts"] == pytest.approx(65.0)
    assert detail["peak_power_watts"] == pytest.approx(65.0)


def test_build_device_detail_handles_device_without_readings():
    fake_device = {
        "id": 999,
        "display_name": "🌬️ Purificador",
        "color": "#667eea",
        "current_power_watts": 0.0,
    }

    detail = build_device_detail(fake_device, READINGS, days=90, tariff=0.862)

    assert detail["last_reading_minutes_ago"] is None
    assert detail["energy_today_kwh"] is None
    assert detail["cost_today_brl"] is None
    assert detail["anomaly"]["has_spike"] is False
    assert detail["power_series"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
