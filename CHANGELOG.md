# Changelog

## [1.1.0] - 2025-11-05

### ✨ Adicionado
- **Integração SmartLife via Gmail API**
  - Cliente Gmail API com autenticação OAuth 2.0
  - Parser de relatórios HTML do SmartLife
  - Analisador de consumo de energia com detecção de anomalias
  - Agente semanal automatizado para processamento de relatórios
  - Sistema de polling inteligente (verifica emails a cada 5 minutos)

- **Dashboard Streamlit Atualizado**
  - Nova seção "Geladeira Nova Digital (SmartLife)"
  - Métricas de consumo diário, projeção mensal e custos
  - Gráficos comparativos e de projeção
  - Recomendações inteligentes baseadas em consumo
  - Visualização de dados brutos

- **Monitoramento Prometheus/Grafana**
  - Prometheus Exporter para métricas SmartLife
  - 7 métricas exportadas (consumo, custo, status, etc)
  - Dashboard Grafana customizado para SmartLife
  - Configuração Prometheus atualizada com job SmartLife

- **Scripts Utilitários**
  - `gmail_polling.py` - Polling automático de emails
  - `prometheus_exporter.py` - Exportador de métricas
  - Scripts de integração e teste

### 🔧 Modificado
- `dashboard.py` - Adicionada seção SmartLife
- `config/prometheus.yml` - Adicionado job SmartLife
- `README.md` - Documentação completa da integração SmartLife
- `.gitignore` - Adicionados arquivos de teste e dados sensíveis

### 📚 Documentação
- Consolidação de guias no README principal
- Seção SmartLife Email Integration
- Instruções de configuração Gmail API
- Guia de execução do sistema completo

### 🔒 Segurança
- Credenciais OAuth no .gitignore
- Tokens de autenticação protegidos
- Dados sensíveis não versionados

## [1.0.0] - 2025-10-XX

### ✨ Inicial
- Sistema de monitoramento TAPO/TP-Link
- API REST com FastAPI
- Banco de dados PostgreSQL
- Dashboard Grafana
- Notificações Telegram/Email
- CI/CD com GitHub Actions
