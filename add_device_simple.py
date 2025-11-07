"""
Script simples para adicionar dispositivo TAPO usando SQL direto
"""
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conectar ao PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="casa_inteligente",
    user="postgres",
    password="postgres"
)

cur = conn.cursor()

# IP do dispositivo TAPO real
ip_address = "192.168.68.108"
device_name = "Tomada TAPO Real"

logger.info(f"🔌 Adicionando dispositivo TAPO: {device_name} ({ip_address})")

# Verificar se já existe
cur.execute("SELECT id, name, type, ip_address, is_active FROM devices WHERE ip_address = %s", (ip_address,))
existing = cur.fetchone()

if existing:
    device_id = existing[0]
    logger.info(f"⚠️  Dispositivo já existe no banco (ID: {device_id})")
    logger.info(f"   Atualizando informações...")
    
    cur.execute("""
        UPDATE devices 
        SET name = %s, type = %s, is_active = %s, updated_at = NOW()
        WHERE ip_address = %s
    """, (device_name, "TAPO", True, ip_address))
    
    conn.commit()
    logger.info("✅ Dispositivo atualizado!")
else:
    # Criar novo dispositivo
    cur.execute("""
        INSERT INTO devices (name, type, ip_address, location, equipment_connected, is_active, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id
    """, (device_name, "TAPO", ip_address, "Casa", "Dispositivo Real", True))
    
    device_id = cur.fetchone()[0]
    conn.commit()
    
    logger.info(f"✅ Dispositivo adicionado ao banco! ID: {device_id}")

# Listar todos os dispositivos
logger.info("\n📋 Dispositivos cadastrados:")
cur.execute("SELECT id, name, type, ip_address, is_active FROM devices ORDER BY id")
devices = cur.fetchall()
for dev in devices:
    logger.info(f"  - ID: {dev[0]} | Nome: {dev[1]} | Tipo: {dev[2]} | IP: {dev[3]} | Ativo: {dev[4]}")

cur.close()
conn.close()

print("\n🎉 Dispositivo TAPO configurado no banco!")
print("   O coletor tentará conectar automaticamente.")
print(f"   Verifique se o dispositivo está acessível em {ip_address}")
