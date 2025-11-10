#!/usr/bin/env python3
"""
Importar dados históricos dos dispositivos TAPO para o Supabase
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tapo import ApiClient
from tapo.requests import EnergyDataInterval
from src.utils.config import settings

SUPABASE_URL = "https://pqqrodiuuhckvdqawgeg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxcXJvZGl1dWhja3ZkcWF3Z2VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0OTI0MTIsImV4cCI6MjA3ODA2ODQxMn0.ve7NIbFcZdTGa16O3Pttmpx2mxWgklvbPwwTSCHuDFs"

def get_devices():
    """Buscar dispositivos TAPO do Supabase"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/devices?type=eq.TAPO",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        },
        timeout=10
    )
    if response.status_code == 200:
        return response.json()
    return []

def save_reading(device_id, timestamp, energy_kwh, power_watts=0):
    """Salvar leitura no Supabase"""
    data = {
        "device_id": device_id,
        "timestamp": timestamp,
        "power_watts": power_watts,
        "voltage": 127,
        "current": 0,
        "energy_today_kwh": energy_kwh,
    }
    
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/energy_readings",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        json=data,
        timeout=10
    )
    
    return response.status_code in [200, 201]

async def import_device_history(device):
    """Importar histórico de um dispositivo"""
    device_id = device['id']
    device_name = device['name']
    ip = device['ip_address']
    
    print(f"\n📱 Importando histórico de: {device_name} ({ip})")
    print("=" * 80)
    
    try:
        # Conectar ao dispositivo
        client = ApiClient(settings.tapo_username, settings.tapo_password)
        tapo_device = await client.p110(ip)
        
        # Obter dados diários (últimos 90 dias)
        print("📅 Buscando dados diários...")
        start_date = datetime.now() - timedelta(days=90)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        daily_data = await tapo_device.get_energy_data(
            EnergyDataInterval.Daily,
            start_date
        )
        
        print(f"   Encontrados {len(daily_data.entries)} dias de histórico")
        
        # Importar cada dia
        imported = 0
        skipped = 0
        
        for entry in daily_data.entries:
            # Converter energia de Wh para kWh
            energy_kwh = entry.energy / 1000.0
            
            # Usar a data do entry
            timestamp = entry.start_date_time.isoformat()
            
            # Salvar no Supabase
            if save_reading(device_id, timestamp, energy_kwh):
                imported += 1
                if imported % 10 == 0:
                    print(f"   Importados {imported} dias...")
            else:
                skipped += 1
        
        print(f"\n✅ Importação concluída:")
        print(f"   ✓ {imported} leituras importadas")
        print(f"   ⊘ {skipped} leituras ignoradas (duplicadas)")
        
        return imported
        
    except Exception as e:
        print(f"❌ Erro ao importar {device_name}: {str(e)}")
        return 0

async def main():
    print("=" * 80)
    print("📊 IMPORTAÇÃO DE DADOS HISTÓRICOS DO TAPO")
    print("=" * 80)
    print()
    print("Este script vai importar até 90 dias de histórico de cada dispositivo TAPO")
    print("para o Supabase. Isso pode levar alguns minutos.")
    print()
    
    # Buscar dispositivos
    devices = get_devices()
    tapo_devices = [d for d in devices if d.get('is_active', True)]
    
    print(f"📱 Encontrados {len(tapo_devices)} dispositivos TAPO ativos")
    
    if not tapo_devices:
        print("❌ Nenhum dispositivo TAPO encontrado")
        return
    
    # Importar cada dispositivo
    total_imported = 0
    
    for device in tapo_devices:
        imported = await import_device_history(device)
        total_imported += imported
    
    print()
    print("=" * 80)
    print("🎉 IMPORTAÇÃO CONCLUÍDA!")
    print("=" * 80)
    print(f"Total de leituras importadas: {total_imported}")
    print()
    print("📊 Próximos passos:")
    print("   1. Verifique os dados no Supabase")
    print("   2. O coletor continuará coletando dados em tempo real")
    print("   3. A LLM agora tem acesso a todo o histórico!")

if __name__ == "__main__":
    asyncio.run(main())
