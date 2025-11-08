"""
Teste para verificar se a LLM consegue acessar dados do Supabase
"""
import requests
from datetime import datetime

SUPABASE_URL = "https://pqqrodiuuhckvdqawgeg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxcXJvZGl1dWhja3ZkcWF3Z2VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0OTI0MTIsImV4cCI6MjA3ODA2ODQxMn0.ve7NIbFcZdTGa16O3Pttmpx2mxWgklvbPwwTSCHuDFs"


def get_supabase_data(endpoint, params=None):
    """Buscar dados do Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code == 200:
        return response.json()
    return []


print("=" * 60)
print("TESTE: Acesso aos dados do Supabase pela LLM")
print("=" * 60)

# 1. Buscar dispositivos
print("\n1. Buscando dispositivos...")
devices = get_supabase_data("devices")
print(f"   ✅ Encontrados {len(devices)} dispositivos")
for d in devices:
    print(f"      - {d.get('name')} ({d.get('type')})")

# 2. Buscar leituras
print("\n2. Buscando leituras de energia...")
readings = get_supabase_data("energy_readings", params={"order": "timestamp.desc", "limit": "10"})
print(f"   ✅ Encontradas {len(readings)} leituras")

if readings:
    latest = readings[0]
    print(f"\n   Última leitura:")
    print(f"      Device ID: {latest.get('device_id')}")
    print(f"      Power: {latest.get('power_watts')}W")
    print(f"      Timestamp: {latest.get('timestamp')}")
    
    # Verificar se é recente (últimas 24h)
    last_time = datetime.fromisoformat(latest.get('timestamp').replace('Z', '+00:00'))
    now = datetime.utcnow().replace(tzinfo=last_time.tzinfo)
    diff = (now - last_time).total_seconds() / 3600
    
    if diff < 24:
        print(f"      ✅ Leitura recente ({diff:.1f}h atrás)")
    else:
        print(f"      ⚠️  Leitura antiga ({diff:.1f}h atrás)")
        print(f"      PROBLEMA: Coletor não está rodando!")
else:
    print("   ❌ Nenhuma leitura encontrada!")

# 3. Simular contexto da LLM
print("\n3. Gerando contexto para LLM...")
today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
readings_today = [
    r for r in readings
    if datetime.fromisoformat(r.get("timestamp", "").replace("Z", "+00:00")) >= today_start
]

print(f"   Leituras de hoje: {len(readings_today)}")

context_parts = []
for device in devices:
    device_id = device.get("id")
    device_name = device.get("name")
    
    device_readings = [r for r in readings if r.get("device_id") == device_id]
    
    if device_readings:
        latest_reading = device_readings[0]
        power = latest_reading.get("power_watts", 0)
        status = "🟢 Ligado" if power > 0 else "🔴 Desligado"
        context_parts.append(f"{device_name}: {status} ({power}W)")
    else:
        context_parts.append(f"{device_name}: ⚪ Sem dados")

print("\n   Contexto gerado:")
for part in context_parts:
    print(f"      {part}")

print("\n" + "=" * 60)
print("CONCLUSÃO:")
print("=" * 60)

if len(devices) > 0 and len(readings) > 0:
    print("✅ Supabase está acessível e tem dados")
    print("✅ LLM PODE acessar os dados")
    
    if len(readings_today) == 0:
        print("⚠️  PROBLEMA: Não há leituras de hoje")
        print("   Solução: Verificar se o coletor está rodando")
else:
    print("❌ PROBLEMA: Dados insuficientes no Supabase")

print("=" * 60)
