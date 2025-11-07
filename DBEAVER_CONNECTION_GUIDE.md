# 🐘 GUIA DE CONEXÃO POSTGRESQL - DBEAVER

## 📋 CONFIGURAÇÕES DE CONEXÃO

### 🏠 PostgreSQL Local
```
Host: localhost
Port: 5432
Database: casa_inteligente
Username: postgres
Password: casa_inteligente_2024
```

### ☁️ Supabase (Produção)
```
Host: db.pqqrodiuuhckvdqawgeg.supabase.co
Port: 5432
Database: postgres
Username: postgres.pqqrodiuuhckvdqawgeg
Password: [Sua senha do Supabase]
```

## 🔧 PASSO A PASSO - DBEAVER

### 1. Abrir Nova Conexão
1. Abra o DBeaver
2. Clique em **Database > New Database Connection**
3. Selecione **PostgreSQL**

### 2. Configurar PostgreSQL Local
- **Host**: localhost
- **Port**: 5432
- **Database**: casa_inteligente
- **Username**: postgres
- **Password**: casa_inteligente_2024
- Clique em **Test Connection**

### 3. Configurar Supabase (Produção)
- **Host**: db.pqqrodiuuhckvdqawgeg.supabase.co
- **Port**: 5432
- **Database**: postgres
- **Username**: postgres.pqqrodiuuhckvdqawgeg
- **Password**: [Obter do painel Supabase]
- Clique em **Test Connection**

## 🗄️ ESTRUTURA DO BANCO

### Tabelas Principais
```sql
-- Dispositivos
SELECT * FROM devices;

-- Leituras de Energia
SELECT * FROM energy_readings;

-- Relatórios Diários
SELECT * FROM daily_reports;

-- Alertas
SELECT * FROM alerts;
```

### Views Úteis
```sql
-- Últimas leituras
SELECT d.name, e.power_watts, e.timestamp 
FROM energy_readings e 
JOIN devices d ON e.device_id = d.id 
ORDER BY e.timestamp DESC LIMIT 10;

-- Consumo por dispositivo
SELECT d.name, COUNT(e.id) as total_readings, AVG(e.power_watts) as avg_power
FROM energy_readings e 
JOIN devices d ON e.device_id = d.id 
GROUP BY d.id, d.name;
```

## 🚨 SOLUÇÃO DE PROBLEMAS

### Erro: "Connection refused"
```bash
# Verificar se PostgreSQL está rodando
brew services list | grep postgres

# Iniciar PostgreSQL
brew services start postgresql@15

# Reiniciar se necessário
brew services restart postgresql@15
```

### Erro: "Authentication failed"
```bash
# Conectar ao PostgreSQL e criar/atualizar usuário
psql postgres -c "ALTER USER postgres PASSWORD 'casa_inteligente_2024';"

# Criar banco se não existir
psql postgres -c "CREATE DATABASE casa_inteligente OWNER postgres;"
```

### Erro: "Database does not exist"
```bash
# Criar banco de dados
createdb -U postgres casa_inteligente
```

## 🔄 VERIFICAR CONEXÃO VIA TERMINAL

### PostgreSQL Local
```bash
# Testar conexão
psql -h localhost -U postgres -d casa_inteligente

# Comandos úteis
\l  -- Listar bancos
\dt -- Listar tabelas
\q  -- Sair
```

### Supabase via psql
```bash
# Instalar cliente PostgreSQL se necessário
brew install postgresql

# Conectar ao Supabase
psql "postgresql://postgres.pqqrodiuuhckvdqawgeg:[senha]@db.pqqrodiuuhckvdqawgeg.supabase.co:5432/postgres"
```

## 📊 DADOS ATUAIS DO SISTEMA

### Dispositivos Configurados
- Tomada Inteligente - Purificador (192.168.68.110)
- Tomada Inteligente - Notebook (192.168.68.108)
- Outros dispositivos de teste

### Leituras Recentes
- Purificador: ~15-20W
- Notebook: ~60-70W
- Timestamps atualizados em tempo real

## 🌐 ACESSO PRODUÇÃO (Cloud Run)

### URLs do Sistema
- **API Produção**: https://sua-api-cloudrun-url.run.app
- **Dashboard Produção**: https://seu-dashboard-cloudrun-url.run.app
- **API Docs**: https://sua-api-cloudrun-url.run.app/docs

### Monitoramento
- **Logs Cloud Run**: Console Google Cloud
- **Métricas**: Cloud Monitoring
- **Banco Produção**: Supabase Dashboard

## 📱 SCRIPTS DE VERIFICAÇÃO

### Verificar PostgreSQL Local
```bash
#!/bin/bash
echo "🔍 Verificando PostgreSQL..."
brew services list | grep postgres
echo "📊 Status de conexão:"
pg_isready -h localhost -p 5432
```

### Verificar Supabase
```bash
#!/bin/bash
echo "🔍 Verificando Supabase..."
curl -s https://pqqrodiuuhckvdqawgeg.supabase.co/rest/v1/devices \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🎯 PRÓXIMOS PASSOS

1. **Conectar ao PostgreSQL Local** via DBeaver
2. **Verificar dados em tempo real** no Supabase
3. **Monitorar sistema em produção** no Cloud Run
4. **Configurar alertas** se necessário

---

**Se o PostgreSQL local continuar com erro, você pode usar apenas o Supabase que já está funcionando!**
