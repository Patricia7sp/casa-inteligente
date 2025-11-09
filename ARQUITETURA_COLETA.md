# 🏗️ Arquitetura de Coleta de Dados

## 📊 Visão Geral

O sistema Casa Inteligente possui uma arquitetura **híbrida** que separa a coleta de dados (local) da API e dashboard (cloud):

```
┌─────────────────────────────────────────────────────────────────┐
│                     SUA REDE LOCAL                              │
│                                                                 │
│  ┌──────────────┐      ┌──────────────────────────────────┐   │
│  │ Dispositivos │◄─────┤  Coletor Local                   │   │
│  │ TAPO         │      │  (run_collector_local.py)        │   │
│  │              │      │                                  │   │
│  │ - Tomadas    │      │  - Coleta a cada 15 min         │   │
│  │ - Sensores   │      │  - Salva no Supabase            │   │
│  └──────────────┘      └──────────────────────────────────┘   │
│                                    │                            │
└────────────────────────────────────┼────────────────────────────┘
                                     │
                                     │ HTTPS
                                     ▼
                        ┌─────────────────────────┐
                        │   SUPABASE (Cloud)      │
                        │                         │
                        │  - PostgreSQL           │
                        │  - REST API             │
                        │  - Realtime             │
                        └─────────────────────────┘
                                     ▲
                                     │ HTTPS
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        │                            │                            │
   ┌────▼─────┐              ┌──────▼──────┐          ┌─────────▼────┐
   │   API    │              │  Dashboard  │          │   Usuários   │
   │ FastAPI  │              │  Streamlit  │          │   (Mobile/   │
   │          │              │             │          │    Web)      │
   │ Cloud    │              │  Cloud Run  │          │              │
   │ Run      │              │             │          │              │
   └──────────┘              └─────────────┘          └──────────────┘
```

## 🔑 Por Que Esta Arquitetura?

### ❌ Problema Original
- Dispositivos TAPO estão na **rede local** (192.168.x.x)
- Cloud Run **não tem acesso** à sua rede doméstica
- Deploy falhava ao tentar conectar aos dispositivos

### ✅ Solução Implementada
1. **Coletor Local** (`run_collector_local.py`)
   - Roda na sua máquina (tem acesso aos dispositivos TAPO)
   - Coleta dados a cada 15 minutos
   - Envia para Supabase via HTTPS (público)

2. **API no Cloud Run**
   - Não tenta conectar aos dispositivos
   - Lê dados do Supabase
   - Serve endpoints REST
   - Processa consultas da LLM

3. **Supabase como Ponte**
   - Recebe dados do coletor local
   - Disponibiliza via REST API
   - Acessível de qualquer lugar

## 🚀 Como Usar

### 1️⃣ Iniciar o Coletor Local (NA SUA MÁQUINA)

```bash
# Ativar ambiente virtual (se usar)
source venv/bin/activate

# Executar coletor
python run_collector_local.py
```

**O coletor vai:**
- ✅ Conectar aos dispositivos TAPO
- ✅ Coletar dados a cada 15 minutos
- ✅ Salvar no Supabase automaticamente
- ✅ Rodar continuamente (deixe rodando!)

### 2️⃣ API e Dashboard (CLOUD RUN - Automático)

A API e o dashboard já estão rodando no Cloud Run:
- **API**: https://casa-inteligente-858582953113.us-central1.run.app
- **Dashboard**: (URL do Streamlit)

Eles **não coletam dados**, apenas **leem do Supabase**.

## 📝 Configuração

### Variáveis de Ambiente Necessárias

**Para o Coletor Local** (arquivo `.env`):
```bash
# Supabase
SUPABASE_URL=https://pqqrodiuuhckvdqawgeg.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...

# TAPO
TAPO_USERNAME=seu_email@gmail.com
TAPO_PASSWORD=sua_senha

# Coleta
ENABLE_COLLECTOR=true
COLLECTION_INTERVAL_MINUTES=15
```

**Para o Cloud Run** (GitHub Secrets):
```bash
ENABLE_COLLECTOR=false  # ❌ Desabilitado no cloud
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
```

## 🔄 Fluxo de Dados

1. **A cada 15 minutos:**
   ```
   Coletor Local → Dispositivos TAPO → Obtém dados de energia
   ```

2. **Salvamento:**
   ```
   Coletor Local → Supabase REST API → Salva leituras
   ```

3. **Consulta (API/Dashboard):**
   ```
   Usuário → Cloud Run → Supabase REST API → Retorna dados
   ```

4. **LLM:**
   ```
   Pergunta → API → Supabase → Contexto → LLM → Resposta
   ```

## 🛠️ Manutenção

### Verificar se o Coletor está Rodando

```bash
# Ver últimas leituras no Supabase
curl -s "https://pqqrodiuuhckvdqawgeg.supabase.co/rest/v1/energy_readings?order=timestamp.desc&limit=5" \
  -H "apikey: SEU_KEY" \
  -H "Authorization: Bearer SEU_KEY" | jq
```

### Reiniciar Coletor

```bash
# Parar: Ctrl+C
# Iniciar novamente:
python run_collector_local.py
```

### Rodar como Serviço (Opcional)

Para que o coletor rode automaticamente ao ligar o computador:

**macOS (launchd):**
```bash
# Criar arquivo: ~/Library/LaunchAgents/com.casainteligente.collector.plist
# (Exemplo fornecido em scripts/launchd.plist)
```

**Linux (systemd):**
```bash
# Criar arquivo: /etc/systemd/system/casa-inteligente-collector.service
# (Exemplo fornecido em scripts/systemd.service)
```

## 🎯 Benefícios

✅ **Deploy no Cloud Run funciona** (não precisa de rede local)  
✅ **Coleta contínua** (coletor local sempre ativo)  
✅ **Dados em tempo real** (Supabase como ponte)  
✅ **Escalável** (API pode escalar independentemente)  
✅ **Confiável** (falha no coletor não derruba a API)  

## 🐛 Troubleshooting

### Problema: Coletor não conecta aos dispositivos
- ✅ Verifique se está na mesma rede WiFi dos dispositivos
- ✅ Confirme usuário/senha TAPO no `.env`
- ✅ Teste conexão: `ping 192.168.x.x`

### Problema: Dados não aparecem no Supabase
- ✅ Verifique logs do coletor
- ✅ Confirme SUPABASE_URL e SUPABASE_ANON_KEY
- ✅ Teste manualmente: `python test_coleta_manual.py`

### Problema: API retorna dados vazios
- ✅ Verifique se coletor está rodando
- ✅ Confirme que há leituras recentes no Supabase
- ✅ Verifique logs da API no Cloud Run

## 📚 Arquivos Importantes

- `run_collector_local.py` - Coletor para rodar localmente
- `src/agents/collector.py` - Lógica de coleta
- `src/main.py` - API FastAPI (Cloud Run)
- `.github/workflows/ci-cd.yml` - Deploy automático
- `ARQUITETURA_COLETA.md` - Este documento
