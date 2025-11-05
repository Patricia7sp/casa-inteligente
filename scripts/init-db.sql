-- Inicialização do banco Casa Inteligente
-- Script executado automaticamente quando o container PostgreSQL inicia

-- Criar usuário específico para a aplicação
CREATE USER casa_user WITH PASSWORD 'casa_user_2024';

-- Conceder permissões no banco principal
GRANT ALL PRIVILEGES ON DATABASE casa_inteligente TO casa_user;

-- Conectar ao banco casa_inteligente para criar tabelas
\c casa_inteligente;

-- Conceder permissões no schema public
GRANT ALL ON SCHEMA public TO casa_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO casa_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO casa_user;

-- Configurar permissões padrão para tabelas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO casa_user;

-- Tabela de dispositivos
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    device_id VARCHAR(100),
    location VARCHAR(100),
    equipment_connected VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabela de leituras de energia
CREATE TABLE IF NOT EXISTS energy_readings (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    power_watts DECIMAL(10,2),
    voltage DECIMAL(10,2),
    current DECIMAL(10,2),
    energy_today_kwh DECIMAL(10,4),
    energy_total_kwh DECIMAL(10,4),
    device_on BOOLEAN,
    data_source VARCHAR(50),
    reading_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de alertas
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    alert_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de relatórios
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    content TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(500)
);

-- Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_energy_readings_device_time ON energy_readings(device_id, reading_time);
CREATE INDEX IF NOT EXISTS idx_alerts_device_created ON alerts(device_id, created_at);
CREATE INDEX IF NOT EXISTS idx_devices_type_active ON devices(type, is_active);

-- Inserir dados de exemplo (opcional)
INSERT INTO devices (name, type, ip_address, device_id, location, equipment_connected) VALUES
('Tomada NovaDigital', 'TUYA_CLOUD', '192.168.68.100', 'eb0254d3ac39b4d2740fwq', 'Sala', 'Tomada Inteligente'),
('Dispositivo Teste', 'TAPO', '192.168.68.101', 'test_device_001', 'Quarto', 'Lâmpada Inteligente')
ON CONFLICT DO NOTHING;

-- Confirmar criação
SELECT 'Banco Casa Inteligente inicializado com sucesso!' AS status;
