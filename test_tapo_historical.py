#!/usr/bin/env python3
"""
Testar se há métodos para obter dados históricos do TAPO
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tapo import ApiClient
from src.utils.config import settings

async def main():
    print("🔍 Procurando métodos de dados históricos no TAPO P110...")
    print()
    
    client = ApiClient(settings.tapo_username, settings.tapo_password)
    device = await client.p110("192.168.68.108")
    
    # Listar todos os métodos disponíveis
    print("📱 Métodos disponíveis:")
    methods = [m for m in dir(device) if not m.startswith('_') and callable(getattr(device, m))]
    for method in methods:
        print(f"   - {method}")
    
    print()
    print("🧪 Testando métodos de dados de energia...")
    print()
    
    # get_energy_data
    if hasattr(device, 'get_energy_data'):
        try:
            print("📊 get_energy_data():")
            data = await device.get_energy_data()
            print(f"   Tipo: {type(data)}")
            print(f"   Dados: {data}")
            print()
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            print()
    
    # get_power_data  
    if hasattr(device, 'get_power_data'):
        try:
            print("⚡ get_power_data():")
            data = await device.get_power_data()
            print(f"   Tipo: {type(data)}")
            print(f"   Dados: {data}")
            print()
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            print()
    
    # get_device_usage
    if hasattr(device, 'get_device_usage'):
        try:
            print("📈 get_device_usage():")
            data = await device.get_device_usage()
            print(f"   Tipo: {type(data)}")
            print(f"   Atributos: {dir(data)}")
            print()
            for attr in dir(data):
                if not attr.startswith('_'):
                    try:
                        value = getattr(data, attr)
                        if not callable(value):
                            print(f"   {attr}: {value}")
                    except:
                        pass
            print()
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            print()
    
    # get_energy_usage (já conhecemos)
    print("📊 get_energy_usage():")
    energy = await device.get_energy_usage()
    print(f"   today_energy: {energy.today_energy}Wh")
    print(f"   month_energy: {energy.month_energy}Wh")
    print(f"   today_runtime: {energy.today_runtime}s")
    print(f"   month_runtime: {energy.month_runtime}s")
    print()
    
    print("💡 Conclusão:")
    print("   - P110 armazena dados de HOJE e do MÊS ATUAL")
    print("   - NÃO há histórico de dias/meses anteriores no dispositivo")
    print("   - Dados históricos devem ser coletados e armazenados externamente (Supabase)")

if __name__ == "__main__":
    asyncio.run(main())
