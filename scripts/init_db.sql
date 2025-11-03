-- Script de inicialização do banco de dados Casa Inteligente
-- Este script é executado automaticamente quando o container PostgreSQL inicia

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Criar banco de dados se não existir
-- (Este comando é executado no template database durante a inicialização)

-- Configurar permissões
GRANT ALL PRIVILEGES ON DATABASE casa_inteligente TO postgres;

-- Criar índices para performance (serão criados pela aplicação SQLAlchemy)
-- Mas podemos criar alguns índices adicionais aqui

-- Índices para tabelas de leituras
CREATE INDEX IF NOT EXISTS idx_energy_readings_timestamp 
ON energy_readings(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_energy_readings_device_timestamp 
ON energy_readings(device_id, timestamp DESC);

-- Índices para relatórios diários
CREATE INDEX IF NOT EXISTS idx_daily_reports_date 
ON daily_reports(date DESC);

CREATE INDEX IF NOT EXISTS idx_daily_reports_device_date 
ON daily_reports(device_id, date DESC);

-- Índices para alerts
CREATE INDEX IF NOT EXISTS idx_alerts_created_at 
ON alerts(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_device_resolved 
ON alerts(device_id, is_resolved);

-- Configurar timezone
SET timezone = 'America/Sao_Paulo';

-- Inserir dados de configuração inicial
INSERT INTO devices (name, type, ip_address, location, equipment_connected, is_active, created_at, updated_at)
VALUES 
    ('Geladeira', 'TAPO', '192.168.1.100', 'Cozinha', 'Geladeira Consul', true, NOW(), NOW()),
    ('Notebook', 'TAPO', '192.168.1.101', 'Escritório', 'Notebook Dell', true, NOW(), NOW()),
    ('Purificador', 'TAPO', '192.168.1.102', 'Cozinha', 'Purificador de Água', true, NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Log de inicialização
DO $$
BEGIN
    RAISE NOTICE 'Banco de dados Casa Inteligente inicializado com sucesso';
    RAISE NOTICE 'Timezone configurado para %', current_setting('timezone');
END $$;
