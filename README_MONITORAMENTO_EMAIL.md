# 🎯 Sistema de Monitoramento de Energia via Email

## 📋 Visão Geral

Sistema inteligente que monitora o consumo de energia da sua geladeira através dos **relatórios HTML** enviados pelo SmartLife por email.

**Solução definitiva** que não depende de Local Key ou API Tuya!

---

## ✨ Funcionalidades

### 🔍 Análise Automática
- ✅ Busca relatórios no Gmail automaticamente
- ✅ Extrai dados de consumo do HTML
- ✅ Calcula médias, projeções e custos
- ✅ Detecta anomalias no consumo
- ✅ Identifica horários de pico
- ✅ Analisa tendências (aumentando/diminuindo)

### 💡 Insights Inteligentes
- ✅ Compara com consumo normal de geladeiras
- ✅ Detecta consumo anormal
- ✅ Gera recomendações personalizadas
- ✅ Alerta sobre problemas críticos
- ✅ Sugere ações de economia

### 🤖 Automação
- ✅ Execução semanal automática (sextas 18:00)
- ✅ Logs detalhados de todas operações
- ✅ Salva histórico de análises
- ✅ Notificações de alertas críticos

---

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Gmail API

#### a) Criar Projeto Google Cloud

1. Acesse: https://console.cloud.google.com/
2. Crie projeto: "Casa Inteligente Monitor"
3. Ative Gmail API

#### b) Criar Credenciais OAuth

1. APIs & Services > Credentials
2. Create Credentials > OAuth client ID
3. Application type: Desktop app
4. Download JSON
5. Salvar como: `config/gmail_credentials.json`

### 3. Autenticar

```bash
python src/integrations/gmail_client.py
```

Autorize o acesso ao Gmail no navegador.

### 4. Executar Primeira Análise

```bash
python src/agents/weekly_energy_agent.py --now
```

---

## 📊 Como Funciona

```
┌─────────────────────────────────────────────────────────┐
│  1. SmartLife envia relatório semanal por email         │
│     ↓                                                    │
│  2. Agente busca email no Gmail                         │
│     ↓                                                    │
│  3. Extrai dados de consumo do HTML                     │
│     ↓                                                    │
│  4. Analisa consumo e detecta anomalias                 │
│     ↓                                                    │
│  5. Gera insights e recomendações                       │
│     ↓                                                    │
│  6. Salva análise e logs                                │
└─────────────────────────────────────────────────────────┘
```

---

## 📧 Configuração do Email

**Informações do remetente SmartLife:**
- Email: `notice.2.ismartlife.me`
- Domínio: `us-west-2.amazonses.com`
- Assunto: "Verifique o relatório de consumo de energia..."

**No app SmartLife:**
1. Configure para receber relatórios semanais
2. Verifique que emails estão chegando
3. Não precisa fazer mais nada!

---

## 🎯 Uso

### Executar Manualmente

```bash
# Análise completa imediata
python src/agents/weekly_energy_agent.py --now
```

### Agendar Execução Semanal

```bash
# Roda toda sexta-feira às 18:00
python src/agents/weekly_energy_agent.py --schedule
```

### Executar Componentes Individuais

```bash
# Apenas buscar emails
python src/integrations/gmail_client.py

# Apenas parsear HTML
python src/integrations/smartlife_parser.py

# Apenas analisar dados
python src/agents/energy_analyzer.py
```

---

## 📊 Exemplo de Saída

```
🔍 ANALISANDO CONSUMO DE ENERGIA
============================================================
📱 Dispositivo: Geladeira
💰 Tarifa: R$ 0.85/kWh

============================================================
📊 RESUMO DA ANÁLISE
============================================================

⚡ CONSUMO:
   Média diária: 1.8 kWh
   Projeção mensal: 54 kWh
   Status: normal

💰 CUSTOS:
   Diário: R$ 1.53
   Mensal: R$ 45.90
   Anual: R$ 550.80

⚠️ ANOMALIAS:
   Detectadas: 2
   - Consumo muito alto: 3.5 kWh (10/11/2025)
   - Consumo muito alto: 3.2 kWh (12/11/2025)

📈 TENDÊNCIA:
   Consumo aumentando (8.5%)

💡 RECOMENDAÇÕES:

   [HIGH] Consumo acima do normal
   Geladeira consumindo 1.8 kWh/dia (normal: 0.8-2.5 kWh)
   
   Ações sugeridas:
   - Verificar vedação da porta
   - Limpar serpentinas
   - Verificar temperatura configurada
   - Considerar manutenção técnica
```

---

## 📁 Estrutura de Dados

### Dados Salvos

```
data/
├── reports/           # Relatórios HTML originais
│   └── smartlife_report_20251105_180000.html
├── parsed/            # Dados extraídos (JSON)
│   └── parsed_report_20251105_180100.json
└── analysis/          # Análises completas (JSON)
    └── energy_analysis_20251105_180200.json
```

### Logs

```
logs/
└── weekly_agent.log   # Log de todas as execuções
```

---

## ⚙️ Configurações

### Tarifa de Energia

Edite `src/agents/energy_analyzer.py`:

```python
analyzer = EnergyAnalyzer(tariff_kwh=0.85)  # Sua tarifa
```

### Consumo Normal (Geladeira)

Edite `src/agents/energy_analyzer.py`:

```python
self.normal_daily_range = (0.8, 2.5)   # kWh/dia
self.normal_monthly_range = (24, 75)   # kWh/mês
```

### Horário de Execução

Edite `src/agents/weekly_energy_agent.py`:

```python
schedule.every().friday.at("18:00").do(...)
```

---

## 🔧 Troubleshooting

### Erro: "Credenciais não encontradas"

```bash
# Verifique se o arquivo existe
ls config/gmail_credentials.json

# Se não existir, baixe do Google Cloud Console
```

### Erro: "Nenhum relatório encontrado"

```bash
# Verifique se emails estão chegando
# Verifique período de busca (padrão: 7 dias)
# Configure SmartLife para enviar relatórios
```

### Erro: "Token expirado"

```bash
# Delete o token e autentique novamente
rm config/gmail_token.pickle
python src/integrations/gmail_client.py
```

---

## 🎉 Vantagens

✅ **Sem Local Key necessária**
✅ **Usa dados oficiais do SmartLife**
✅ **Totalmente automatizado**
✅ **Análise inteligente**
✅ **Detecção de anomalias**
✅ **Recomendações personalizadas**
✅ **Fácil configuração**
✅ **100% confiável**

---

## 📚 Documentação Adicional

- [Guia Completo](GUIA_SISTEMA_EMAIL.md)
- [Configuração Gmail API](https://developers.google.com/gmail/api/quickstart/python)
- [Análise de Consumo](docs/ANALISE_CONSUMO.md)

---

## 🤝 Suporte

Se tiver problemas:
1. Verifique os logs: `logs/weekly_agent.log`
2. Execute com `--now` para testar
3. Verifique configurações do Gmail API

---

## 📝 Licença

MIT License - Veja [LICENSE](LICENSE)

---

**Desenvolvido com ❤️ para monitoramento inteligente de energia!**
