#!/usr/bin/env python3
"""
Mostrar conteúdo dos entries históricos
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tapo import ApiClient
from tapo.requests import EnergyDataInterval
from src.utils.config import settings

async def main():
    client = ApiClient(settings.tapo_username, settings.tapo_password)
    device = await client.p110("192.168.68.108")
    
    # Dados por dia (último mês)
    print("=" * 80)
    print("📊 DADOS DIÁRIOS DO ÚLTIMO MÊS")
    print("=" * 80)
    print()
    
    start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    daily = await device.get_energy_data(EnergyDataInterval.Daily, start_date)
    
    print(f"Total de dias: {len(daily.entries)}")
    print(f"Intervalo: {daily.interval_length} minutos")
    print(f"Data início: {daily.start_date_time}")
    print()
    
    # Mostrar primeiros 5 dias
    print("📅 Primeiros 5 dias:")
    for i, entry in enumerate(daily.entries[:5]):
        print(f"\nDia {i+1}:")
        for attr in dir(entry):
            if not attr.startswith('_'):
                try:
                    value = getattr(entry, attr)
                    if not callable(value):
                        print(f"  {attr}: {value}")
                except:
                    pass
    
    print()
    print("=" * 80)
    print("📊 DADOS POR HORA (Hoje)")
    print("=" * 80)
    print()
    
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    hourly = await device.get_energy_data(EnergyDataInterval.Hourly, start_date)
    
    print(f"Total de horas: {len(hourly.entries)}")
    print()
    
    # Mostrar todas as horas de hoje
    print("🕐 Horas de hoje:")
    for i, entry in enumerate(hourly.entries):
        for attr in dir(entry):
            if not attr.startswith('_'):
                try:
                    value = getattr(entry, attr)
                    if not callable(value):
                        if attr == 'energy_wh':
                            print(f"Hora {i}: {value}Wh")
                except:
                    pass

if __name__ == "__main__":
    asyncio.run(main())
