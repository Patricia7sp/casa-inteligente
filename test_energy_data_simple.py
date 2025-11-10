#!/usr/bin/env python3
"""
Testar get_energy_data com strings simples
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tapo import ApiClient
from src.utils.config import settings

async def main():
    print("📊 Testando get_energy_data()...")
    print()
    
    client = ApiClient(settings.tapo_username, settings.tapo_password)
    device = await client.p110("192.168.68.108")
    
    # Testar com diferentes parâmetros
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    print("🧪 Teste 1: Hourly")
    try:
        data = await device.get_energy_data("Hourly", start_date)
        print(f"✅ Sucesso! Tipo: {type(data)}")
        print(f"   Dados: {data}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    print("🧪 Teste 2: Daily")
    try:
        data = await device.get_energy_data("Daily", start_date)
        print(f"✅ Sucesso! Tipo: {type(data)}")
        print(f"   Dados: {data}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    print("🧪 Teste 3: Monthly")
    try:
        data = await device.get_energy_data("Monthly", start_date)
        print(f"✅ Sucesso! Tipo: {type(data)}")
        print(f"   Dados: {data}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    print("🧪 Teste 4: Verificar assinatura do método")
    import inspect
    sig = inspect.signature(device.get_energy_data)
    print(f"   Assinatura: {sig}")

if __name__ == "__main__":
    asyncio.run(main())
