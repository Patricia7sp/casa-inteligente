#!/usr/bin/env python3
"""
Explorar estrutura dos dados históricos
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
    
    # Dados por hora
    print("=" * 80)
    print("📊 DADOS POR HORA (Hoje)")
    print("=" * 80)
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    hourly = await device.get_energy_data(EnergyDataInterval.Hourly, start_date)
    
    print(f"Tipo: {type(hourly)}")
    print(f"Atributos: {[x for x in dir(hourly) if not x.startswith('_')]}")
    print()
    
    for attr in dir(hourly):
        if not attr.startswith('_'):
            try:
                value = getattr(hourly, attr)
                if not callable(value):
                    print(f"{attr}: {value}")
            except:
                pass
    
    print()
    print("=" * 80)
    print("📊 DADOS POR DIA (Último mês)")
    print("=" * 80)
    start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    daily = await device.get_energy_data(EnergyDataInterval.Daily, start_date)
    
    print(f"Tipo: {type(daily)}")
    print()
    
    for attr in dir(daily):
        if not attr.startswith('_'):
            try:
                value = getattr(daily, attr)
                if not callable(value):
                    print(f"{attr}: {value}")
                    if attr == 'data' and isinstance(value, list):
                        print(f"  Total de registros: {len(value)}")
                        if len(value) > 0:
                            print(f"  Primeiro registro: {value[0]}")
                            print(f"  Último registro: {value[-1]}")
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())
