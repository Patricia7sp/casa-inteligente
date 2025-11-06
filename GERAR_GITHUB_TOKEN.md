# 🔑 GERAR GITHUB PERSONAL ACCESS TOKEN

## 📋 PASSO A PASSO:

### 1. Acesse o GitHub
```
https://github.com/settings/tokens
```

### 2. Clique em "Generate new token"
- Clique em "Generate new token (classic)"

### 3. Configure o token:
- **Note:** `CI/CD Casa Inteligente`
- **Expiration:** 90 days (ou No expiration)
- **Select scopes:**
  - ✅ `repo` (Full control of private repositories)
    - ✅ repo:status
    - ✅ repo_deployment
    - ✅ public_repo
    - ✅ repo:invite
    - ✅ security_events

### 4. Gerar e copiar
- Clique em "Generate token"
- **COPIE O TOKEN IMEDIATAMENTE** (só aparece uma vez!)
- Formato: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 🚀 EXECUTAR SCRIPT:

Após gerar o token, execute:

```bash
cd /Users/patriciamenezes/anaconda3/casa_inteligente

python setup_github_secrets.py
```

O script vai pedir:
1. Seu GitHub Personal Access Token
2. Se quer configurar secrets opcionais

---

## ✅ O QUE SERÁ CONFIGURADO AUTOMATICAMENTE:

### **Obrigatórios:**
- ✅ GCP_PROJECT_ID
- ✅ GCP_SA_KEY (do arquivo config/gcp-sa-key.json)
- ✅ DATABASE_URL
- ✅ REDIS_URL

### **Opcionais (você escolhe):**
- ⏳ TAPO_USERNAME
- ⏳ TAPO_PASSWORD
- ⏳ TELEGRAM_BOT_TOKEN
- ⏳ TELEGRAM_CHAT_ID
- ⏳ EMAIL_USERNAME
- ⏳ EMAIL_PASSWORD
- ⏳ OPENAI_API_KEY

---

## 🔒 SEGURANÇA:

- ✅ Token é usado apenas localmente
- ✅ Secrets são criptografados antes de enviar
- ✅ Token pode ser revogado depois
- ✅ Secrets ficam seguros no GitHub

---

**PRONTO! Gere o token e execute o script!**
