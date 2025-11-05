# 🏠 Casa Inteligente - Sistema de Monitoramento de Energia

Sistema inteligente para monitoramento de consumo de energia residencial usando tomadas inteligentes TP-Link TAPO e outras marcas.

## 📋 Visão Geral

O Casa Inteligente é um sistema completo que permite:
- **Monitoramento em tempo real** do consumo de energia de equipamentos domésticos
- **Análise inteligente** para detectar anomalias e padrões de consumo
- **Relatórios automáticos** diários via Email e Telegram
- **Dashboards interativos** para visualização de dados
- **Alertas inteligentes** para consumo anômalo
- **Assistente virtual** com LLM para consultas

## 🚀 Features

### ⚡ Monitoramento
- Coleta automática de dados das tomadas inteligentes
- Suporte para TP-Link TAPO e outras marcas
- **Monitoramento via email** - Relatórios SmartLife (Geladeira Nova Digital)
- Monitoramento em tempo real via API REST
- Histórico completo de consumo

### 📊 Análise
- Cálculo automático de custos diários
- Detecção de anomalias e picos de consumo
- Análise de tendências e padrões
- Comparação com médias históricas

### 📱 Notificações
- Relatórios diários automáticos
- Alertas de consumo anômalo
- Suporte para Telegram e Email
- Notificações do sistema

### 🎯 Dashboards
- Interface web responsiva (Streamlit)
- Gráficos interativos com Grafana
- Visualização em tempo real
- Relatórios personalizáveis
- **Dashboard SmartLife** - Geladeira Nova Digital com métricas de consumo

### 🤖 Assistente IA
- Consultas em tempo real com LLM
- Análise preditiva de consumo
- Recomendações de economia
- Conversação natural

## 🛠️ Tecnologias

- **Backend**: Python 3.10, FastAPI, SQLAlchemy
- **Banco de Dados**: PostgreSQL, Redis
- **Monitoramento**: Prometheus, Grafana, Streamlit
- **Email Integration**: Gmail API, OAuth 2.0
- **Containerização**: Docker, Docker Compose
- **Deploy**: Google Cloud Run
- **CI/CD**: GitHub Actions
- **IA**: OpenAI API, Google Gemini

## 📦 Instalação

### Pré-requisitos
- Python 3.10+
- Docker e Docker Compose
- PostgreSQL (se não usar Docker)
- Redis (se não usar Docker)

### 1. Clonar o repositório
```bash
git clone https://github.com/Patricia7sp/casa-inteligente.git
cd casa-inteligente
```

### 2. Configurar ambiente virtual
```bash
python -m venv casa
source casa/bin/activate  # Linux/Mac
# ou
casa\Scripts\activate     # Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Editar .env com suas configurações
```

### 5. Iniciar com Docker Compose (Recomendado)
```bash
docker-compose up -d
```

### 6. Ou iniciar manualmente
```bash
# Iniciar PostgreSQL e Redis
# Configurar banco de dados

# Iniciar aplicação
uvicorn src.main:app --reload
```

## ⚙️ Configuração

### Variáveis de Ambiente Principais

```bash
# Banco de Dados
DATABASE_URL=postgresql://user:password@localhost/casa_inteligente
REDIS_URL=redis://localhost:6379

# TAPO
TAPO_USERNAME=seu_email_tapo
TAPO_PASSWORD=sua_senha_tapo

# Notificações
TELEGRAM_BOT_TOKEN=seu_bot_token
TELEGRAM_CHAT_ID=seu_chat_id
EMAIL_USERNAME=seu_email@gmail.com
EMAIL_PASSWORD=sua_app_password

# Energia
ENERGY_COST_PER_KWH=0.85
COLLECTION_INTERVAL_MINUTES=15
```

### Configurar Telegram Bot
1. Fale com [@BotFather](https://t.me/BotFather) no Telegram
2. Crie um novo bot com `/newbot`
3. Copie o token do bot
4. Obtenha seu chat ID com [@userinfobot](https://t.me/userinfobot)
5. Configure as variáveis `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`

### Configurar Email
1. Para Gmail, crie uma App Password
2. Configure `EMAIL_USERNAME` e `EMAIL_PASSWORD`
3. Adicione destinatários em `EMAIL_RECIPIENTS`

### Configurar Gmail API (SmartLife)
1. Crie projeto no Google Cloud Console
2. Ative Gmail API
3. Configure OAuth 2.0 credentials
4. Baixe credenciais para `config/gmail_credentials.json`
5. Execute autenticação: `python src/integrations/gmail_client.py`
6. Inicie polling: `python scripts/gmail_polling.py`

## 📡 Uso da API

### Endpoints Principais

#### Obter status em tempo real
```bash
curl http://localhost:8000/status/realtime
```

#### Adicionar dispositivo
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

#### Gerar relatório diário
```bash
curl http://localhost:8000/reports/daily
```

#### Enviar relatório via notificações
```bash
curl -X POST http://localhost:8000/reports/daily/send
```

#### Controlar dispositivo
```bash
curl -X POST http://localhost:8000/devices/1/control \
  -H "Content-Type: application/json" \
  -d '{"action": "off"}'
```

## 📊 Dashboards

### Streamlit Dashboard
Acesse `http://localhost:8501`
```bash
streamlit run dashboard.py
```

**Seções disponíveis:**
- Dispositivos TAPO/TP-Link em tempo real
- **Geladeira Nova Digital (SmartLife)** - Consumo, projeção e custos
- Gráficos interativos e recomendações
- Controle de dispositivos

### Grafana
Acesse `http://localhost:3000`
- Usuário: admin
- Senha: admin

**Dashboards disponíveis:**
- Consumo em tempo real
- Histórico diário/semanal/mensal
- Comparação entre dispositivos
- Alertas e anomalias
- **SmartLife Dashboard** - Métricas da geladeira

**Importar dashboard SmartLife:**
```bash
# Importar em Grafana: config/grafana_dashboard_smartlife.json
```

### Prometheus Metrics
Acesse `http://localhost:9090/metrics`
```bash
# Iniciar exporter SmartLife
python src/services/prometheus_exporter.py
```

## 🚀 Deploy no Google Cloud

### 1. Configurar gcloud CLI
```bash
gcloud auth login
gcloud config set project seu-projeto-id
```

### 2. Build e Push da imagem
```bash
gcloud builds submit --tag gcr.io/seu-projeto-id/casa-inteligente
```

### 3. Deploy no Cloud Run
```bash
gcloud run deploy casa-inteligente \
  --image gcr.io/seu-projeto-id/casa-inteligente \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=sua_db_url
```

## 🧪 Testes

### Executar testes
```bash
pytest tests/ -v --cov=src
```

### Testar notificações
```bash
curl -X POST http://localhost:8000/notifications/test
```

## 🔄 CI/CD

O projeto usa GitHub Actions para:
- Testes automáticos em cada push
- Build e deploy automático para produção
- Verificação de qualidade de código

## 📁 Estrutura do Projeto

```
casa_inteligente/
├── src/
│   ├── agents/          # Agentes de monitoramento
│   │   ├── collector.py           # Coleta de dados TAPO
│   │   ├── energy_analyzer.py     # Análise de consumo
│   │   └── weekly_energy_agent.py # Agente semanal SmartLife
│   ├── api/            # Endpoints FastAPI
│   ├── integrations/   # Clientes das APIs
│   │   ├── tapo_client.py         # Cliente TAPO/TP-Link
│   │   ├── gmail_client.py        # Cliente Gmail API
│   │   └── smartlife_parser.py    # Parser relatórios SmartLife
│   ├── models/         # Models de dados
│   ├── services/       # Lógica de negócio
│   │   └── prometheus_exporter.py # Exporter Prometheus
│   ├── utils/          # Utilitários
│   └── main.py         # Aplicação principal
├── tests/              # Testes automatizados
├── scripts/            # Scripts utilitários
│   ├── gmail_polling.py           # Polling emails SmartLife
│   └── add_my_devices.py          # Adicionar dispositivos
├── config/             # Configurações
│   ├── prometheus.yml             # Config Prometheus
│   └── grafana_dashboard_smartlife.json  # Dashboard Grafana
├── data/               # Dados de runtime
│   └── smartlife/                 # Dados SmartLife
├── docs/               # Documentação
├── dashboard.py        # Dashboard Streamlit
└── .github/workflows/  # CI/CD
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- 📧 Email: patricia@example.com
- 💬 Telegram: @patricia_menezes
- 🐛 Issues: [GitHub Issues](https://github.com/Patricia7sp/casa-inteligente/issues)

## 🎯 Roadmap

- [x] Suporte para TP-Link TAPO
- [x] Integração com SmartLife via email
- [x] Dashboard Streamlit interativo
- [x] Monitoramento Prometheus/Grafana
- [x] Gmail API para relatórios automáticos
- [ ] Suporte para mais marcas de tomadas
- [ ] Aplicativo mobile
- [ ] Integração com assistentes de voz
- [ ] Análise preditiva avançada
- [ ] Dashboard público compartilhável
- [ ] Integração com sistemas de energia solar

## 📧 SmartLife Email Integration

O sistema monitora automaticamente emails do SmartLife (Geladeira Nova Digital) e processa relatórios de consumo.

### Como funciona:
1. **Polling automático** verifica Gmail a cada 5 minutos
2. **Detecta novos relatórios** SmartLife
3. **Baixa e processa** dados de consumo
4. **Salva métricas** em JSON e Prometheus
5. **Atualiza dashboards** automaticamente

### Executar sistema completo:
```bash
# 1. Polling de emails (background)
python scripts/gmail_polling.py &

# 2. Prometheus exporter (background)
python src/services/prometheus_exporter.py &

# 3. Dashboard Streamlit
streamlit run dashboard.py
```

### Métricas disponíveis:
- Consumo diário (kWh)
- Projeção mensal (kWh)
- Custo estimado (R$)
- Status (normal/alert)
- Alertas inteligentes

### Arquivos importantes:
- `data/smartlife/latest.json` - Dados mais recentes
- `config/gmail_credentials.json` - Credenciais OAuth
- `config/gmail_token.pickle` - Token de autenticação

---

**Feito com ❤️ por Patricia Menezes**
