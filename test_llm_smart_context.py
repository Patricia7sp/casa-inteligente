"""
Demonstração: Como a LLM agora responde de forma mais inteligente e contextual
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


print("=" * 80)
print("DEMONSTRAÇÃO: LLM INTELIGENTE E CONTEXTUAL")
print("=" * 80)

# Buscar dados
devices = get_supabase_data("devices")
readings = get_supabase_data("energy_readings", params={"order": "timestamp.desc", "limit": "10"})

now = datetime.utcnow()
today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
readings_today = [
    r for r in readings
    if datetime.fromisoformat(r.get("timestamp", "").replace("Z", "+00:00")) >= today_start
]

# Calcular status
if readings:
    latest_time = datetime.fromisoformat(readings[0].get("timestamp").replace("Z", "+00:00"))
    time_diff = (now.replace(tzinfo=latest_time.tzinfo) - latest_time).total_seconds()
    hours_ago = time_diff / 3600
else:
    latest_time = None
    hours_ago = 999

print("\n📊 CONTEXTO QUE A LLM RECEBE:")
print("-" * 80)
print(f"Data/Hora Atual: {now.strftime('%d/%m/%Y %H:%M:%S UTC')}")
print(f"Dispositivos Monitorados: {len(devices)}")
print(f"Total de Leituras no Banco: {len(readings)}")
print(f"Leituras de Hoje: {len(readings_today)}")

if latest_time:
    print(f"Última Leitura: {latest_time.strftime('%d/%m/%Y %H:%M:%S')} ({hours_ago:.1f}h atrás)")
    
    if hours_ago < 0.25:  # < 15 min
        status = "✅ Dados atualizados (sistema coletando normalmente)"
    elif hours_ago < 1:
        status = "⚠️ Possível atraso na coleta"
    elif hours_ago < 24:
        status = "⚠️ Sistema de coleta pode estar parado"
    else:
        status = "❌ Sistema de coleta NÃO está funcionando"
    
    print(f"Status da Coleta: {status}")
else:
    print("Última Leitura: Nenhuma")
    print("Status da Coleta: ❌ Sistema ainda não coletou dados")

print("\n" + "=" * 80)
print("🤖 COMO A LLM RESPONDERÁ AGORA (EXEMPLOS)")
print("=" * 80)

print("\n📝 Pergunta: 'Como está meu consumo hoje?'")
print("-" * 80)

if len(readings_today) > 0:
    print("✅ RESPOSTA INTELIGENTE:")
    print(f"   'Até o momento, estou monitorando {len(devices)} dispositivos.")
    print(f"    Tenho {len(readings_today)} leituras de hoje.")
    print(f"    Última atualização há {int(time_diff / 60)} minutos.'")
    print(f"    [+ detalhes de consumo...]")
else:
    print("✅ RESPOSTA INTELIGENTE:")
    print(f"   'Tenho acesso ao sistema e estou monitorando {len(devices)} dispositivos,")
    print(f"    mas ainda não tenho leituras de hoje.")
    print(f"    A última atualização foi em {latest_time.strftime('%d/%m/%Y às %H:%M')}.")
    if hours_ago > 24:
        print(f"    Isso foi há {int(hours_ago / 24)} dia(s), o que indica que o sistema")
        print(f"    de coleta automática (a cada 15 minutos) não está funcionando.")
    else:
        print(f"    Isso foi há {int(hours_ago)} hora(s).")
    print(f"    Posso te mostrar os dados da última leitura disponível.'")

print("\n📝 Pergunta: 'Qual dispositivo gasta mais?'")
print("-" * 80)

if len(readings_today) > 0:
    print("✅ RESPOSTA INTELIGENTE:")
    print("   'Com base nos dados de hoje, o dispositivo que mais consome é...'")
    print("   [+ ranking com valores reais]")
else:
    print("✅ RESPOSTA INTELIGENTE:")
    print(f"   'Não tenho dados de hoje ainda (última atualização:")
    print(f"    {latest_time.strftime('%d/%m/%Y às %H:%M')}),")
    print(f"    mas posso te mostrar o consumo da última leitura disponível:")
    print("   [+ dados da última leitura com disclaimer sobre atualidade]")

print("\n📝 Pergunta: 'Você tem acesso aos dados?'")
print("-" * 80)
print("✅ RESPOSTA INTELIGENTE:")
print(f"   'Sim! Tenho acesso ao banco de dados Supabase e estou monitorando")
print(f"    {len(devices)} dispositivos. Tenho {len(readings)} leituras no total.")
if len(readings_today) == 0:
    print(f"    Porém, não há leituras de hoje ainda. A última atualização foi")
    print(f"    em {latest_time.strftime('%d/%m/%Y às %H:%M')} ({int(hours_ago)}h atrás).")
    print(f"    O sistema de coleta automática parece estar parado.'")
else:
    print(f"    Tenho {len(readings_today)} leituras de hoje e o sistema está")
    print(f"    coletando normalmente (última atualização há {int(time_diff / 60)} min).'")

print("\n" + "=" * 80)
print("💡 DIFERENÇA PRINCIPAL")
print("=" * 80)
print("\n❌ ANTES (Resposta Genérica):")
print("   'Infelizmente, não tenho acesso aos dados de consumo de dias anteriores...'")
print("\n✅ AGORA (Resposta Contextual e Inteligente):")
print("   'Tenho acesso ao sistema! Estou monitorando X dispositivos.")
print("    A última atualização foi em [DATA/HORA específica].")
print("    [Explica o MOTIVO: sistema parado, sem dados de hoje, etc.]")
print("    Posso te mostrar os dados disponíveis...'")

print("\n" + "=" * 80)
print("🎯 BENEFÍCIOS")
print("=" * 80)
print("✅ Transparência total sobre o estado dos dados")
print("✅ Usuário entende se é problema de acesso ou de coleta")
print("✅ LLM sempre oferece alternativas (dados da última leitura)")
print("✅ Contexto rico: datas, horas, quantidade de leituras")
print("✅ Diagnóstico automático do sistema de coleta")
print("=" * 80)
