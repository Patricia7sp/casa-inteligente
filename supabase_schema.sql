-- Schema para Casa Inteligente no Supabase
-- Execute este SQL no Supabase SQL Editor: https://supabase.com/dashboard/project/pqqrodiuuhckvdqawgeg/sql/new

-- Tabela de dispositivos
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

-- Tabela de leituras de energia
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

-- Tabela de alertas
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    alert_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de relatórios
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL,
    report_date DATE NOT NULL,
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_energy_readings_device_id ON energy_readings(device_id);
CREATE INDEX IF NOT EXISTS idx_energy_readings_timestamp ON energy_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_device_id ON alerts(device_id);
CREATE INDEX IF NOT EXISTS idx_devices_ip_address ON devices(ip_address);

-- Inserir dispositivos iniciais
INSERT INTO devices (name, type, ip_address, location, equipment_connected, is_active)
VALUES 
    ('Tomada NovaDigital', 'TUYA_CLOUD', '192.168.68.100', 'Casa', 'NovaDigital', TRUE),
    ('Dispositivo Teste', 'TAPO', '192.168.68.101', 'Teste', 'Teste', TRUE),
    ('Tomada TAPO Real', 'TAPO', '192.168.68.108', 'Casa', 'Dispositivo Real', TRUE)
ON CONFLICT DO NOTHING;

-- Habilitar Row Level Security (RLS) - Opcional, mas recomendado
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE energy_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Criar políticas para permitir acesso via service role
CREATE POLICY "Enable all access for service role" ON devices FOR ALL USING (true);
CREATE POLICY "Enable all access for service role" ON energy_readings FOR ALL USING (true);
CREATE POLICY "Enable all access for service role" ON alerts FOR ALL USING (true);
CREATE POLICY "Enable all access for service role" ON reports FOR ALL USING (true);
CREATE POLICY "Enable all access for service role" ON users FOR ALL USING (true);
