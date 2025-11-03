# 🚀 Quick Start - Casa Inteligente

Guia rápido para colocar o sistema Casa Inteligente funcionando em minutos.

## 📋 Pré-requisitos

- Python 3.10+
- Docker e Docker Compose (recomendado)
- Contas nas APIs (opcional para testes)

## ⚡ Setup Rápido (5 minutos)

### 1. Clonar e Configurar
```bash
git clone https://github.com/Patricia7sp/casa-inteligente.git
cd casa-inteligente
```

### 2. Configurar Ambiente
```bash
# Copiar arquivo de ambiente
cp .env.example .env

# Editar configurações básicas
nano .env
```

**Configurações mínimas no `.env`:**
```bash
# TAPO (essencial para coleta de dados)
TAPO_USERNAME=seu_email_tapo
TAPO_PASSWORD=sua_senha_tapo

# Custo da energia (ajuste para sua região)
ENERGY_COST_PER_KWH=0.85

# Telegram para notificações (opcional)
TELEGRAM_BOT_TOKEN=seu_bot_token
TELEGRAM_CHAT_ID=seu_chat_id
```

### 3. Iniciar com Docker
```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar status
docker-compose ps
```

### 4. Acessar o Sistema

**API Documentation:** http://localhost:8000/docs
**Streamlit Dashboard:** http://localhost:8501
**Grafana:** http://localhost:3000 (admin/admin)
**Prometheus:** http://localhost:9090

## 📱 Adicionar Primeiro Dispositivo

### Via API (curl)
```bash
curl -X POST http://localhost:8000/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Geladeira",
    "type": "TAPO",
    "ip_address": "192.168.1.100",
    "location": "Cozinha",
    "equipment_connected": "Geladeira Consul"
  }'
```

### Via Python
```python
import requests

device_data = {
    "name": "Geladeira",
    "type": "TAPO", 
    "ip_address": "192.168.1.100",
    "location": "Cozinha",
    "equipment_connected": "Geladeira Consul"
}

response = requests.post("http://localhost:8000/devices", json=device_data)
print(response.json())
```

## 🔍 Verificar Funcionamento

### 1. Status em Tempo Real
```bash
curl http://localhost:8000/status/realtime
```

### 2. Gerar Relatório Diário
```bash
curl http://localhost:8000/reports/daily
```

### 3. Testar Notificações
```bash
curl -X POST http://localhost:8000/notifications/test
```

## 🤖 Testar Assistente IA

```bash
curl -X POST http://localhost:8000/ai/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qual equipamento está consumindo mais energia agora?",
    "provider": "auto"
  }'
```

## 📊 Monitoramento

### Logs do Sistema
```bash
# Ver logs da aplicação
docker-compose logs -f app

# Ver logs do banco
docker-compose logs -f db

# Ver todos os logs
docker-compose logs -f
```

### Banco de Dados
```bash
# Acessar PostgreSQL
docker-compose exec db psql -U postgres -d casa_inteligente

# Ver dispositivos
SELECT * FROM devices;

# Ver leituras recentes
SELECT * FROM energy_readings ORDER BY timestamp DESC LIMIT 10;
```

## 🔧 Configurar Telegram Bot (Opcional)

1. **Criar Bot:**
   - Fale com [@BotFather](https://t.me/BotFather)
   - `/newbot` → Nome do bot → Username
   - Copie o token

2. **Obter Chat ID:**
   - Fale com [@userinfobot](https://t.me/userinfobot)
   - Copie seu chat ID

3. **Configurar no .env:**
   ```bash
   TELEGRAM_BOT_TOKEN=seu_token_aqui
   TELEGRAM_CHAT_ID=seu_chat_id_aqui
   ```

4. **Testar:**
   ```bash
   curl -X POST http://localhost:8000/notifications/test
   ```

## 🌐 Deploy em Produção

### Google Cloud Run
```bash
# Configurar GCP
gcloud auth login
gcloud config set project seu-projeto-id

# Deploy automático
./scripts/deploy_gcp.sh production
```

### Variáveis de Produção
Configure no Google Cloud Run:
- `DATABASE_URL`: PostgreSQL Cloud SQL
- `REDIS_URL`: Redis Memorystore
- `TAPO_USERNAME/TAPO_PASSWORD`: Credenciais TAPO
- `TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID`: Telegram
- `OPENAI_API_KEY`: Para assistente IA (opcional)

## 🧪 Testes

```bash
# Executar testes locais
pytest tests/ -v

# Testar com Docker
docker-compose exec app pytest tests/ -v

# Ver cobertura
docker-compose exec app pytest tests/ --cov=src
```

## 📈 Escalando o Sistema

### Para Mais Dispositivos
- Aumente `COLLECTION_INTERVAL_MINUTES` para reduzir carga
- Configure Redis cluster para cache distribuído
- Use PostgreSQL com TimescaleDB para séries temporais

### Para Alta Disponibilidade
- Configure múltiplas instâncias no Cloud Run
- Use load balancer do Cloud Run
- Configure backups automáticos do PostgreSQL

## 🔥 Exemplos de Uso

### Automatizar Relatórios
```bash
# Script para relatório diário automático
#!/bin/bash
curl -X POST http://localhost:8000/reports/daily/send | logger -t casa-inteligente
```

### Integração com Home Assistant
```yaml
# configuration.yaml
sensor:
  - platform: rest
    resource: http://localhost:8000/status/realtime
    name: "Casa Inteligente Consumo"
    value_template: "{{ value_json.total_current_power_watts }}"
    unit_of_measurement: "W"
```

### Alertas Customizados
```python
# Script Python para alertas personalizados
import requests

status = requests.get("http://localhost:8000/status/realtime").json()
total_power = status.get("total_current_power_watts", 0)

if total_power > 2000:  # 2kW threshold
    requests.post("http://localhost:8000/ai/ask", json={
        "question": f"Consumo muito alto detectado: {total_power}W. O que fazer?"
    })
```

## 🆘 Problemas Comuns

### **Dispositivo não conecta**
- Verifique IP e credenciais TAPO
- Confirme se dispositivo está na mesma rede
- Teste com app TAPO oficial primeiro

### **Notificações não funcionam**
- Verifique token e chat ID do Telegram
- Confirme configurações SMTP para email
- Teste com endpoint `/notifications/test`

### **Dashboard não atualiza**
- Verifique se API está respondendo: `curl http://localhost:8000/health`
- Confirme se coletor está funcionando nos logs
- Reinicie serviços: `docker-compose restart`

### **Erro no banco de dados**
- Verifique se PostgreSQL está rodando
- Confirme string de conexão no .env
- Recrie containers: `docker-compose down && docker-compose up -d`

## 📞 Suporte

- 📖 [Documentação completa](README.md)
- 🐛 [Issues no GitHub](https://github.com/Patricia7sp/casa-inteligente/issues)
- 💬 [Telegram](https://t.me/patricia_menezes)

---

**Parabéns! 🎉 Seu sistema Casa Inteligente está funcionando!**

Agora você pode:
- Monitorar consumo em tempo real
- Receber alertas inteligentes  
- Gerar relatórios automáticos
- Conversar com o assistente IA
- Visualizar dados nos dashboards
