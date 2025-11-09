#!/usr/bin/env python3
"""
Teste manual de coleta para validar integração com TAPO e Supabase
"""
import asyncio
import sys
import os
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.integrations.tapo_client import TapoClient
from src.utils.config import settings
import requests

SUPABASE_URL = "https://pqqrodiuuhckvdqawgeg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxcXJvZGl1dWhja3ZkcWF3Z2VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0OTI0MTIsImV4cCI6MjA3ODA2ODQxMn0.ve7NIbFcZdTGa16O3Pttmpx2mxWgklvbPwwTSCHuDFs"

async def test_tapo_connection():
    """Testar conexão com dispositivos TAPO"""
    print("=== TESTE DE CONEXÃO TAPO ===")
    
    # Buscar dispositivos TAPO do Supabase
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/devices",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
            },
            timeout=10
        )
        if response.status_code != 200:
            print(f"❌ Erro ao buscar dispositivos: {response.status_code}")
            return []
        
        devices = response.json()
        tapo_devices = [d for d in devices if d.get("type", "").upper() == "TAPO"]
        print(f"✅ Encontrados {len(tapo_devices)} dispositivos TAPO")
        
        return tapo_devices
        
    except Exception as e:
        print(f"❌ Erro ao conectar Supabase: {str(e)}")
        return []

async def test_energy_collection():
    """Testar coleta de energia de um dispositivo"""
    print("\n=== TESTE DE COLETA DE ENERGIA ===")
    
    devices = await test_tapo_connection()
    if not devices:
        print("❌ Nenhum dispositivo TAPO encontrado")
        return False
    
    # Inicializar cliente TAPO
    client = TapoClient(settings.tapo_username, settings.tapo_password)
    
    for device in devices[:1]:  # Testar apenas o primeiro
        ip = device.get("ip_address")
        name = device.get("name")
        device_id = device.get("id")
        
        print(f"\n🔌 Testando dispositivo: {name} ({ip})")
        
        # Adicionar dispositivo
        try:
            success = await client.add_device(ip, name)
            if not success:
                print(f"❌ Falha ao adicionar dispositivo {name}")
                continue
                
            # Coletar dados de energia
            data = await client.get_energy_usage(name)
            if not data:
                print(f"❌ Falha ao coletar dados de energia de {name}")
                continue
                
            print(f"✅ Dados coletados de {name}:")
            print(f"   Potência: {data['power_watts']:.2f}W")
            print(f"   Energia hoje: {data['energy_today_kwh']:.3f}kWh")
            print(f"   Timestamp: {data['timestamp']}")
            
            # Salvar no Supabase
            reading_data = {
                "device_id": device_id,
                "timestamp": data["timestamp"].isoformat() if isinstance(data["timestamp"], datetime) else data["timestamp"],
                "power_watts": float(data["power_watts"]),
                "voltage": float(data.get("voltage", 0)),
                "current": float(data.get("current", 0)),
                "energy_kwh": float(data.get("energy_today_kwh", 0)),
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/energy_readings",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal",
                },
                json=reading_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Dados salvos no Supabase com sucesso!")
                return True
            else:
                print(f"❌ Erro ao salvar no Supabase: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste com {name}: {str(e)}")
            continue
    
    return False

if __name__ == "__main__":
    print("🚀 Iniciando teste manual de coleta...")
    print(f"Usuário TAPO: {settings.tapo_username}")
    
    success = asyncio.run(test_energy_collection())
    
    if success:
        print("\n🎉 Teste concluído com sucesso! Coleta funcionando.")
    else:
        print("\n❌ Teste falhou. Verifique os logs acima.")
    
    print("\n📊 Verificando leituras no Supabase...")
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/energy_readings?order=timestamp.desc&limit=3",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        },
        timeout=10
    )
    
    if response.status_code == 200:
        readings = response.json()
        print(f"Total de leituras: {len(readings)}")
        for reading in readings[:3]:
            print(f"  - {reading.get('timestamp')} | Device {reading.get('device_id')} | {reading.get('power_watts')}W")
    else:
        print(f"❌ Erro ao buscar leituras: {response.status_code}")
