"""
Script para sincronizar PostgreSQL local com Supabase
"""
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conectar ao PostgreSQL local
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="casa_inteligente",
    user="postgres",
    password="postgres"
)

cur = conn.cursor()

logger.info("🏗️  Criando tabelas faltantes no PostgreSQL local...")

# Criar tabelas que estavam faltando
create_tables_sql = """
-- Tabela de alertas (já existe, mas garantir)
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    alert_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de relatórios diários
CREATE TABLE IF NOT EXISTS daily_reports (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL UNIQUE,
    total_consumption_kwh FLOAT,
    total_cost FLOAT,
    peak_power_watts FLOAT,
    peak_time TIMESTAMP,
    devices_active INTEGER,
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de relatórios (já existe, mas garantir)
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL,
    report_date DATE NOT NULL,
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de usuários (já existe, mas garantir)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_alerts_device_id ON alerts(device_id);
CREATE INDEX IF NOT EXISTS idx_daily_reports_date ON daily_reports(report_date);
"""

try:
    cur.execute(create_tables_sql)
    conn.commit()
    logger.info("✅ Tabelas criadas/verificadas")
except Exception as e:
    logger.error(f"❌ Erro ao criar tabelas: {e}")
    conn.rollback()

# Adicionar os 2 dispositivos TAPO reais
logger.info("\n📱 Adicionando dispositivos TAPO reais...")

devices_to_add = [
    {
        "name": "Tomada TAPO Real",
        "type": "TAPO",
        "ip": "192.168.68.108",
        "location": "Notebook",
        "equipment": "Dispositivo Real"
    },
    {
        "name": "Tomada TAPO Real",
        "type": "TAPO",
        "ip": "192.168.68.110",
        "location": "Purificador",
        "equipment": "Dispositivo Real"
    }
]

for device in devices_to_add:
    try:
        # Verificar se já existe
        cur.execute("SELECT id FROM devices WHERE ip_address = %s", (device["ip"],))
        existing = cur.fetchone()
        
        if existing:
            logger.info(f"⚠️  Dispositivo {device['ip']} já existe (ID: {existing[0]})")
            # Atualizar
            cur.execute("""
                UPDATE devices 
                SET name = %s, type = %s, location = %s, equipment_connected = %s, is_active = TRUE, updated_at = NOW()
                WHERE ip_address = %s
            """, (device["name"], device["type"], device["location"], device["equipment"], device["ip"]))
            logger.info(f"✅ Dispositivo {device['ip']} atualizado")
        else:
            # Inserir novo
            cur.execute("""
                INSERT INTO devices (name, type, ip_address, location, equipment_connected, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, TRUE, NOW(), NOW())
                RETURNING id
            """, (device["name"], device["type"], device["ip"], device["location"], device["equipment"]))
            
            device_id = cur.fetchone()[0]
            logger.info(f"✅ Dispositivo {device['ip']} adicionado (ID: {device_id})")
        
        conn.commit()
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar dispositivo {device['ip']}: {e}")
        conn.rollback()

# Listar todos os dispositivos
logger.info("\n📋 Dispositivos cadastrados no PostgreSQL local:")
cur.execute("SELECT id, name, type, ip_address, location, is_active FROM devices ORDER BY id")
devices = cur.fetchall()

for dev in devices:
    logger.info(f"  - ID: {dev[0]} | Nome: {dev[1]} | Tipo: {dev[2]} | IP: {dev[3]} | Local: {dev[4]} | Ativo: {dev[5]}")

# Listar tabelas
logger.info("\n📊 Tabelas no PostgreSQL local:")
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
""")
tables = cur.fetchall()
for table in tables:
    logger.info(f"  - {table[0]}")

cur.close()
conn.close()

logger.info("\n🎉 Sincronização concluída!")
logger.info("\n💡 Próximos passos:")
logger.info("   1. Os dispositivos TAPO estão cadastrados no PostgreSQL local")
logger.info("   2. Quando o deploy no Cloud Run acontecer, ele usará o Supabase")
logger.info("   3. O coletor tentará conectar aos dispositivos TAPO nos IPs:")
logger.info("      - 192.168.68.108 (Notebook)")
logger.info("      - 192.168.68.110 (Purificador)")
