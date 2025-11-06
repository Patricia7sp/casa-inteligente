# 🔐 CONFIGURAÇÃO DE SECRETS - GITHUB ACTIONS

## 📋 LISTA COMPLETA DE SECRETS NECESSÁRIOS:

### **1. GCP (Google Cloud Platform) - OBRIGATÓRIOS PARA DEPLOY**

#### `GCP_PROJECT_ID`
- **Descrição:** ID do projeto no Google Cloud
- **Valor atual:** `casa-inteligente-477314`
- **Onde encontrar:** Google Cloud Console → Project Info
- **Exemplo:** `casa-inteligente-477314`

#### `GCP_SA_KEY`
- **Descrição:** JSON da Service Account Key do GCP
- **Formato:** JSON completo (várias linhas)
- **Como obter:** Vou criar automaticamente
- **Exemplo:**
```json
{
  "type": "service_account",
  "project_id": "casa-inteligente-477314",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

---

### **2. BANCO DE DADOS - OBRIGATÓRIOS**

#### `DATABASE_URL`
- **Descrição:** URL de conexão PostgreSQL
- **Valor atual:** `postgresql://postgres:casa_inteligente_2024@localhost:5432/casa_inteligente`
- **Formato:** `postgresql://user:password@host:port/database`
- **Para produção:** Usar Cloud SQL ou PostgreSQL gerenciado

#### `REDIS_URL`
- **Descrição:** URL de conexão Redis
- **Valor atual:** `redis://localhost:6379`
- **Formato:** `redis://host:port`
- **Para produção:** Usar Redis Cloud ou Memorystore

---

### **3. DISPOSITIVOS TAPO - OPCIONAIS**

#### `TAPO_USERNAME`
- **Descrição:** Email da conta TP-Link/TAPO
- **Valor:** Seu email cadastrado no app TAPO
- **Exemplo:** `paty7sp@gmail.com`

#### `TAPO_PASSWORD`
- **Descrição:** Senha da conta TP-Link/TAPO
- **Valor:** Sua senha do app TAPO
- **Segurança:** Nunca commitar no código

---

### **4. NOTIFICAÇÕES - OPCIONAIS**

#### `TELEGRAM_BOT_TOKEN`
- **Descrição:** Token do bot do Telegram
- **Como obter:** Falar com @BotFather no Telegram
- **Formato:** `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
- **Exemplo:** `5678901234:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`

#### `TELEGRAM_CHAT_ID`
- **Descrição:** ID do chat para receber notificações
- **Como obter:** Falar com @userinfobot no Telegram
- **Formato:** Número (pode ser negativo)
- **Exemplo:** `123456789` ou `-987654321`

#### `EMAIL_USERNAME`
- **Descrição:** Email para enviar notificações
- **Valor:** Email Gmail
- **Exemplo:** `paty7sp@gmail.com`

#### `EMAIL_PASSWORD`
- **Descrição:** App Password do Gmail
- **Como obter:** Google Account → Security → 2-Step Verification → App passwords
- **Formato:** 16 caracteres sem espaços
- **Exemplo:** `abcd efgh ijkl mnop` (remover espaços)

---

### **5. IA/LLM - OPCIONAL**

#### `OPENAI_API_KEY`
- **Descrição:** API Key da OpenAI para GPT
- **Como obter:** https://platform.openai.com/api-keys
- **Formato:** `sk-...`
- **Exemplo:** `sk-proj-abc123def456...`

---

## 🎯 PRIORIDADE DE CONFIGURAÇÃO:

### **CRÍTICOS (Deploy não funciona sem):**
1. ✅ `GCP_PROJECT_ID` - Já temos: `casa-inteligente-477314`
2. ⏳ `GCP_SA_KEY` - Vou criar agora
3. ⏳ `DATABASE_URL` - Configurar para produção
4. ⏳ `REDIS_URL` - Configurar para produção

### **IMPORTANTES (Funcionalidades principais):**
5. ⏳ `TAPO_USERNAME` - Para dispositivos TAPO
6. ⏳ `TAPO_PASSWORD` - Para dispositivos TAPO

### **OPCIONAIS (Notificações e extras):**
7. ⏳ `TELEGRAM_BOT_TOKEN` - Para notificações
8. ⏳ `TELEGRAM_CHAT_ID` - Para notificações
9. ⏳ `EMAIL_USERNAME` - Para emails
10. ⏳ `EMAIL_PASSWORD` - Para emails
11. ⏳ `OPENAI_API_KEY` - Para IA/LLM

---

## 📝 VALORES ATUAIS (do .env local):

```bash
# GCP
GCP_PROJECT_ID=casa-inteligente-477314

# Database (local)
DATABASE_URL=postgresql://postgres:casa_inteligente_2024@localhost:5432/casa_inteligente
REDIS_URL=redis://localhost:6379

# TAPO (você precisa fornecer)
TAPO_USERNAME=seu_email@gmail.com
TAPO_PASSWORD=sua_senha

# Telegram (você precisa fornecer)
TELEGRAM_BOT_TOKEN=seu_token
TELEGRAM_CHAT_ID=seu_chat_id

# Email (você precisa fornecer)
EMAIL_USERNAME=seu_email@gmail.com
EMAIL_PASSWORD=sua_app_password

# OpenAI (opcional)
OPENAI_API_KEY=sk-...
```

---

## 🚀 PRÓXIMOS PASSOS:

### **1. Criar Service Account no GCP**
Vou executar automaticamente:
- Criar service account
- Gerar chave JSON
- Configurar permissões necessárias

### **2. Configurar Secrets no GitHub**
Você precisará:
- Ir para GitHub → Settings → Secrets and variables → Actions
- Adicionar cada secret manualmente
- Ou eu posso fazer via GitHub CLI

### **3. Atualizar pytest/pytest-cov**
Vou corrigir o requirements.txt

### **4. Testar CI/CD**
Fazer commit e verificar se passa

---

## 🔒 SEGURANÇA:

- ✅ Secrets ficam **APENAS** no GitHub Actions
- ✅ **NÃO** precisam estar no Secret Manager do GCP
- ✅ **NÃO** são expostos nos logs
- ✅ **NÃO** são commitados no código
- ✅ Acessíveis apenas durante execução do workflow

---

**Pronto para começar?**

1. Vou criar a Service Account no GCP
2. Vou gerar a chave JSON
3. Vou configurar os secrets no GitHub
4. Vou atualizar pytest/pytest-cov
5. Vou fazer commit e testar

**Confirme para eu prosseguir!**
