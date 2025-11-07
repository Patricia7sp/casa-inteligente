# 🛠️ GUIA DE CORREÇÃO DOS PROBLEMAS IDENTIFICADOS

## 📋 RESUMO DO DIAGNÓSTICO

### ✅ O que está funcionando:
- **Rede Local**: Dispositivos TAPO respondem ao ping (192.168.68.110 e 192.168.68.108)
- **Estrutura do Projeto**: Código bem organizado e funcional

### ❌ Problemas identificados:
1. **Credenciais TAPO**: Não configuradas no arquivo `.env`
2. **Banco PostgreSQL**: Autenticação falhando

---

## 🔧 PASSO 1: CONFIGURAR CREDENCIAIS TAPO

### 1.1 Abra o arquivo `.env`:
```bash
nano .env
```

### 1.2 Preencha com suas credenciais reais:
```env
# Substitua com seus dados reais
TAPO_USERNAME=seu_email_real@exemplo.com
TAPO_PASSWORD=sua_senha_real_tapo
```

### 1.3 Onde encontrar suas credenciais TAPO:
1. Abra o aplicativo **TAPO** no seu celular
2. Faça login com sua conta TP-Link
3. Vá em **Configurações > Conta TP-Link**
4. Use o mesmo email e senha do app

---

## 🗄️ PASSO 2: CONFIGURAR BANCO POSTGRESQL

### 2.1 Verificar se PostgreSQL está rodando:
```bash
# Verificar status
brew services list | grep postgresql

# Iniciar PostgreSQL se não estiver rodando
brew services start postgresql
```

### 2.2 Criar banco e usuário:
```bash
# Conectar ao PostgreSQL
psql postgres

# Criar usuário e banco
CREATE USER postgres WITH PASSWORD 'casa_inteligente_2024';
CREATE DATABASE casa_inteligente OWNER postgres;
GRANT ALL PRIVILEGES ON DATABASE casa_inteligente TO postgres;
\q
```

### 2.3 Verificar string de conexão no `.env`:
```env
DATABASE_URL=postgresql://postgres:casa_inteligente_2024@localhost/casa_inteligente
```

---

## 🧪 PASSO 3: TESTAR CORREÇÕES

### 3.1 Executar diagnóstico completo:
```bash
python diagnostico_simples.py
```

### 3.2 Resultado esperado após correções:
```
✅ Rede Local: OK
✅ Banco de Dados: OK  
✅ TAPO Cloud: OK
```

---

## 📱 PASSO 4: CONFIGURAR DISPOSITIVOS

### 4.1 Se TAPO Cloud funcionou:
```bash
# Descobrir dispositivos automaticamente
python test_tapo_discovery.py
```

### 4.2 Adicionar dispositivos ao sistema:
```bash
python scripts/add_my_devices.py
```

### 4.3 Verificar dispositivos cadastrados:
```bash
curl http://localhost:8000/devices
```

---

## 🚀 PASSO 5: INICIAR SISTEMA COMPLETO

### 5.1 Via Docker (Recomendado):
```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Verificar logs
docker-compose logs -f app
```

### 5.2 Manualmente:
```bash
# Terminal 1 - API
uvicorn src.main:app --reload

# Terminal 2 - Coletor de dados
python -m asyncio src.agents.collector

# Terminal 3 - Dashboard
streamlit run dashboard.py
```

---

## 📊 PASSO 6: VERIFICAR FUNCIONAMENTO

### 6.1 Acessar interfaces:
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501
- **Health Check**: http://localhost:8000/health

### 6.2 Testar endpoints:
```bash
# Status em tempo real
curl http://localhost:8000/status/realtime

# Gerar relatório
curl http://localhost:8000/reports/daily
```

---

## 🔌 PASSO 7: SOLUÇÃO ALTERNATIVA (se Cloud não funcionar)

### 7.1 Usar conexão local direta:
Se a TP-Link Cloud não funcionar, podemos usar conexão local:

```python
# Exemplo de configuração local
devices = [
    {
        "name": "Tomada Inteligente - Purificador",
        "type": "TAPO", 
        "ip_address": "192.168.68.110",
        "location": "Quarto",
        "equipment": "Purificador de Ar"
    },
    {
        "name": "Tomada Inteligente - Notebook",
        "type": "TAPO",
        "ip_address": "192.168.68.108", 
        "location": "Escritório",
        "equipment": "Notebook Dell"
    }
]
```

### 7.2 Script para teste local:
```bash
python scripts/test_local_connection.py
```

---

## 🔄 PASSO 8: SINCRONIZAÇÃO COM SUPABASE

### 8.1 Configurar Supabase:
```env
# Adicionar ao .env
SUPABASE_URL=https://sua-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon
SUPABASE_SERVICE_KEY=sua_chave_service
```

### 8.2 Testar sincronização:
```bash
python sync_local_db.py
```

---

## 📱 PASSO 9: CONFIGURAR NOTIFICAÇÕES (Opcional)

### 9.1 Telegram:
```env
TELEGRAM_BOT_TOKEN=seu_bot_token
TELEGRAM_CHAT_ID=seu_chat_id
```

### 9.2 Email:
```env
EMAIL_USERNAME=seu_email@gmail.com
EMAIL_PASSWORD=sua_app_password
```

---

## 🎯 CHECKLIST FINAL

- [ ] Credenciais TAPO configuradas no `.env`
- [ ] PostgreSQL rodando e acessível  
- [ ] Dispositivos TAPO conectados via cloud ou local
- [ ] Dispositivos cadastrados no banco
- [ ] Sistema iniciado (docker-compose up -d)
- [ ] Dashboard acessível em http://localhost:8501
- [ ] Coleta de dados funcionando
- [ ] Sincronização com Supabase ativa

---

## 🆘 AJUDA ADICIONAL

### Se precisar de ajuda:
1. **Logs completos**: `docker-compose logs -f`
2. **Diagnóstico**: `python diagnostico_simples.py`
3. **Teste de API**: `python scripts/test_apis.py`
4. **Documentação**: `docs/API_RESUMO.md`

### Contato:
- 📧 Email: patricia@example.com
- 💬 Telegram: @patricia_menezes
- 🐛 Issues: GitHub Issues

---

## 📈 PRÓXIMOS MELHORIAS

Após corrigir os problemas básicos:
1. **Monitoramento avançado**: Configurar Prometheus/Grafana
2. **Alertas inteligentes**: Detecção de anomalias
3. **Dashboard mobile**: Versão para celular
4. **IA integrada**: Assistente virtual para consultas
5. **Relatórios automáticos**: Email/Telegram diários

---

**Feito com ❤️ por Patricia Menezes**
