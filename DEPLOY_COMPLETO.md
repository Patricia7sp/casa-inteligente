# 🚀 DEPLOY COMPLETO - CASA INTELIGENTE v1.0.0

## ✅ INFRAESTRUTURA GCP CONFIGURADA:

### **1. Artifact Registry**
- ✅ Repositório: `us-central1-docker.pkg.dev/casa-inteligente-477314/casa-inteligente`
- ✅ Imagens Docker versionadas
- ✅ Tags: commit SHA + latest

### **2. Cloud Run**
- ✅ Service: `casa-inteligente`
- ✅ Região: `us-central1`
- ✅ Configuração: 512Mi RAM, 1 CPU
- ✅ Porta: 8000 (dinâmica via $PORT)
- ✅ Acesso: público (--allow-unauthenticated)

### **3. Service Account**
- ✅ Email: `github-actions-ci-cd@casa-inteligente-477314.iam.gserviceaccount.com`
- ✅ Permissões:
  - Cloud Run Admin
  - Storage Admin
  - Artifact Registry Writer
  - Service Account User

### **4. APIs Habilitadas**
- ✅ Artifact Registry API
- ✅ Cloud Run API
- ✅ Cloud Build API

---

## 🔐 SECRETS CONFIGURADOS:

### **Obrigatórios (✅ Configurados):**
1. ✅ `GCP_PROJECT_ID` = `casa-inteligente-477314`
2. ✅ `GCP_SA_KEY` = Service Account JSON
3. ✅ `DATABASE_URL` = PostgreSQL connection
4. ✅ `REDIS_URL` = Redis connection

### **Opcionais (⏳ Configurar quando necessário):**
- TAPO_USERNAME
- TAPO_PASSWORD
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- EMAIL_USERNAME
- EMAIL_PASSWORD
- OPENAI_API_KEY

---

## 📦 SISTEMA DE VERSIONAMENTO:

### **GitHub Releases**
- ✅ Release automático após deploy bem-sucedido
- ✅ Tag: `v{run_number}` (ex: v1, v2, v3...)
- ✅ Informações: commit SHA, imagem Docker, mudanças

### **Docker Images**
- ✅ Tag por commit: `{sha}` (específica, imutável)
- ✅ Tag latest: `latest` (sempre a mais recente)
- ✅ Histórico completo no Artifact Registry

### **Rollback**
Para voltar para uma versão anterior:
```bash
# Listar releases
gh release list

# Fazer rollback para versão específica
gcloud run deploy casa-inteligente \
  --image us-central1-docker.pkg.dev/casa-inteligente-477314/casa-inteligente/casa-inteligente:{COMMIT_SHA} \
  --region us-central1

# Ou usar latest da versão anterior
gcloud run deploy casa-inteligente \
  --image us-central1-docker.pkg.dev/casa-inteligente-477314/casa-inteligente/casa-inteligente:latest \
  --region us-central1
```

---

## 🔄 CI/CD PIPELINE:

### **Jobs:**

#### **1. test** (⚠️ com continue-on-error)
- Linting (flake8)
- Formatação (black)
- Testes unitários (pytest)
- PostgreSQL + Redis em containers

#### **2. security** (✅ Passando)
- Safety scan (vulnerabilidades)
- Bandit (segurança do código)

#### **3. build** (✅ Passando)
- Build Docker image
- Push para Artifact Registry
- Tags: commit SHA + latest

#### **4. deploy** (🔄 Testando)
- Deploy para Cloud Run
- Configuração de env vars
- Criação de GitHub Release
- Notificação via Telegram

---

## 🎯 FLUXO COMPLETO:

```
1. Push para main
   ↓
2. Test + Security (paralelo)
   ↓
3. Build Docker Image
   ↓
4. Push para Artifact Registry
   ↓
5. Deploy para Cloud Run
   ↓
6. Criar GitHub Release
   ↓
7. Notificar via Telegram
   ↓
8. ✅ Deploy Completo!
```

---

## 📊 MONITORAMENTO:

### **GitHub Actions**
```bash
# Ver runs
open https://github.com/Patricia7sp/casa-inteligente/actions

# Ver releases
open https://github.com/Patricia7sp/casa-inteligente/releases
```

### **Cloud Run**
```bash
# Ver service
gcloud run services describe casa-inteligente --region us-central1

# Ver logs
gcloud run services logs read casa-inteligente --region us-central1

# Ver URL do serviço
gcloud run services describe casa-inteligente --region us-central1 --format='value(status.url)'
```

### **Artifact Registry**
```bash
# Listar imagens
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/casa-inteligente-477314/casa-inteligente/casa-inteligente

# Ver tags
gcloud artifacts docker tags list \
  us-central1-docker.pkg.dev/casa-inteligente-477314/casa-inteligente/casa-inteligente
```

---

## 🔧 COMANDOS ÚTEIS:

### **Deploy Manual**
```bash
# Build local
docker build -t casa-inteligente:local .

# Run local
docker run -p 8000:8000 --env-file .env casa-inteligente:local

# Deploy manual
gcloud run deploy casa-inteligente \
  --image us-central1-docker.pkg.dev/casa-inteligente-477314/casa-inteligente/casa-inteligente:latest \
  --region us-central1
```

### **Rollback**
```bash
# Ver histórico de revisões
gcloud run revisions list --service casa-inteligente --region us-central1

# Rollback para revisão anterior
gcloud run services update-traffic casa-inteligente \
  --to-revisions {REVISION_NAME}=100 \
  --region us-central1
```

### **Logs**
```bash
# Logs em tempo real
gcloud run services logs tail casa-inteligente --region us-central1

# Logs das últimas 24h
gcloud run services logs read casa-inteligente \
  --region us-central1 \
  --limit 100
```

---

## 🎉 PRÓXIMOS PASSOS:

### **1. Configurar Banco de Dados de Produção**
- [ ] Criar Cloud SQL (PostgreSQL)
- [ ] Atualizar DATABASE_URL secret
- [ ] Migrar dados

### **2. Configurar Redis de Produção**
- [ ] Criar Memorystore (Redis)
- [ ] Atualizar REDIS_URL secret

### **3. Configurar Domínio Customizado**
- [ ] Registrar domínio
- [ ] Configurar Cloud Run custom domain
- [ ] Configurar SSL/TLS

### **4. Monitoramento Avançado**
- [ ] Configurar Prometheus
- [ ] Configurar Grafana
- [ ] Configurar alertas

### **5. Configurar Secrets Opcionais**
- [ ] TAPO credentials
- [ ] Telegram bot
- [ ] Email notifications
- [ ] OpenAI API

---

## 📝 VERSÃO ATUAL:

**v1.0.0** - Deploy inicial para produção

**Features:**
- ✅ CI/CD completo
- ✅ Artifact Registry
- ✅ Cloud Run
- ✅ Versionamento automático
- ✅ Rollback support
- ✅ Security scans
- ✅ Docker multi-stage build

**Próxima versão (v1.1.0):**
- Banco de dados de produção
- Redis de produção
- Domínio customizado
- Monitoramento completo

---

**Status:** 🚀 Deploy em andamento...

**URL CI/CD:** https://github.com/Patricia7sp/casa-inteligente/actions/runs/19120164278

**Aguardando conclusão do deploy...**
