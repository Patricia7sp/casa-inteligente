"""
Script para configurar Supabase usando SQL via API REST
"""
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Credenciais Supabase
SUPABASE_URL = "https://pqqrodiuuhckvdqawgeg.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxcXJvZGl1dWhja3ZkcWF3Z2VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0OTI0MTIsImV4cCI6MjA3ODA2ODQxMn0.ve7NIbFcZdTGa16O3Pttmpx2mxWgklvbPwwTSCHuDFs"
SUPABASE_SERVICE_KEY = "sbp_6301f1416db7f937c4d1094b2507af1af3224d2c"

logger.info("🔍 Verificando status do projeto Supabase...")

# Testar se a API está respondendo
try:
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/",
        headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}"
        },
        timeout=10
    )
    
    if response.status_code == 200:
        logger.info("✅ API Supabase está online!")
    else:
        logger.error(f"❌ API retornou status {response.status_code}")
        exit(1)
except Exception as e:
    logger.error(f"❌ Erro ao conectar à API: {e}")
    logger.info("\n⚠️  O projeto Supabase pode estar PAUSADO.")
    logger.info("   Acesse: https://supabase.com/dashboard/project/pqqrodiuuhckvdqawgeg")
    logger.info("   E clique em 'Resume project' se estiver pausado.")
    exit(1)

logger.info("\n🏗️  Criando tabelas via SQL...")

# SQL para criar tabelas
sql_commands = [
    # Tabela de dispositivos
    """
    CREATE TABLE IF NOT EXISTS devices (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        type VARCHAR(50) NOT NULL,
        ip_address VARCHAR(15) NOT NULL,
        model VARCHAR(100),
        location VARCHAR(100),
        equipment_connected VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        device_id VARCHAR(255)
    );
    """,
    
    # Tabela de leituras de energia
    """
    CREATE TABLE IF NOT EXISTS energy_readings (
        id SERIAL PRIMARY KEY,
        device_id INTEGER REFERENCES devices(id),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        power_watts FLOAT NOT NULL,
        voltage FLOAT,
        current FLOAT,
        energy_today_kwh FLOAT,
        energy_total_kwh FLOAT,
        device_on BOOLEAN,
        data_source VARCHAR(50),
        reading_at TIMESTAMP
    );
    """,
    
    # Índices
    "CREATE INDEX IF NOT EXISTS idx_energy_readings_device_id ON energy_readings(device_id);",
    "CREATE INDEX IF NOT EXISTS idx_energy_readings_timestamp ON energy_readings(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_devices_ip_address ON devices(ip_address);",
]

# Executar SQL via API (se disponível)
logger.info("⚠️  Nota: A API REST do Supabase não permite executar SQL DDL diretamente.")
logger.info("   Você precisará executar o SQL manualmente no SQL Editor do Supabase.")
logger.info("\n📋 Copie e execute este SQL no Supabase SQL Editor:")
logger.info("   https://supabase.com/dashboard/project/pqqrodiuuhckvdqawgeg/sql/new")
logger.info("\n" + "="*80)

full_sql = "\n\n".join(sql_commands)
print(full_sql)

logger.info("="*80)
logger.info("\n💡 Após executar o SQL acima, adicione os dispositivos via API REST:")

# Adicionar dispositivos via API REST
devices_to_add = [
    {
        "name": "Tomada NovaDigital",
        "type": "TUYA_CLOUD",
        "ip_address": "192.168.68.100",
        "location": "Casa",
        "equipment_connected": "NovaDigital",
        "is_active": True
    },
    {
        "name": "Dispositivo Teste",
        "type": "TAPO",
        "ip_address": "192.168.68.101",
        "location": "Teste",
        "equipment_connected": "Teste",
        "is_active": True
    },
    {
        "name": "Tomada TAPO Real",
        "type": "TAPO",
        "ip_address": "192.168.68.108",
        "location": "Casa",
        "equipment_connected": "Dispositivo Real",
        "is_active": True
    }
]

logger.info("\n📱 Tentando adicionar dispositivos via API REST...")

for device in devices_to_add:
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/devices",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=device,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            logger.info(f"✅ Dispositivo '{device['name']}' adicionado")
        else:
            logger.warning(f"⚠️  Erro ao adicionar '{device['name']}': {response.status_code} - {response.text[:100]}")
    except Exception as e:
        logger.warning(f"⚠️  Erro ao adicionar '{device['name']}': {e}")

logger.info("\n🎉 Configuração concluída!")
logger.info(f"\n📝 DATABASE_URL para usar:")
logger.info(f"   postgresql://postgres:hafbuf-6vomdo-bucsUq@db.pqqrodiuuhckvdqawgeg.supabase.co:5432/postgres")
