#!/bin/bash

# Script de Deploy para Google Cloud Run - Casa Inteligente
# Uso: ./scripts/deploy_gcp.sh [ambiente]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função de log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Variáveis de ambiente
ENVIRONMENT=${1:-production}
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"casa-inteligente-$(whoami)"}
REGION=${GOOGLE_CLOUD_REGION:-"us-central1"}
SERVICE_NAME="casa-inteligente"
IMAGE_NAME="casa-inteligente"
REGISTRY="gcr.io"

log "Iniciando deploy do Casa Inteligente para ambiente: $ENVIRONMENT"

# Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    error "gcloud CLI não encontrado. Instale o Google Cloud SDK primeiro."
fi

# Verificar autenticação
log "Verificando autenticação com Google Cloud..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    error "Você não está autenticado. Execute 'gcloud auth login' primeiro."
fi

# Configurar projeto
log "Configurando projeto: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Habilitar APIs necessárias
log "Habilitando APIs do Google Cloud..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable sql-component.googleapis.com

# Verificar variáveis de ambiente obrigatórias
if [[ -z "$DATABASE_URL" ]]; then
    error "DATABASE_URL não configurado. Configure a variável de ambiente."
fi

if [[ -z "$TAPO_USERNAME" ]] || [[ -z "$TAPO_PASSWORD" ]]; then
    warning "Credenciais TAPO não configuradas. O sistema não funcionará corretamente."
fi

# Build da imagem Docker
log "Fazendo build da imagem Docker..."
docker build -t $REGISTRY/$PROJECT_ID/$IMAGE_NAME:$ENVIRONMENT .

# Push da imagem para o registry
log "Enviando imagem para Google Container Registry..."
docker push $REGISTRY/$PROJECT_ID/$IMAGE_NAME:$ENVIRONMENT

# Deploy para Cloud Run
log "Fazendo deploy para Cloud Run..."

# Preparar variáveis de ambiente para o Cloud Run
ENV_VARS=""
ENV_VARS="$ENV_VARS,ENVIRONMENT=$ENVIRONMENT"
ENV_VARS="$ENV_VARS,DATABASE_URL=$DATABASE_URL"
ENV_VARS="$ENV_VARS,REDIS_URL=${REDIS_URL:-redis://localhost:6379}"
ENV_VARS="$ENV_VARS,TAPO_USERNAME=$TAPO_USERNAME"
ENV_VARS="$ENV_VARS,TAPO_PASSWORD=$TAPO_PASSWORD"
ENV_VARS="$ENV_VARS,ENERGY_COST_PER_KWH=${ENERGY_COST_PER_KWH:-0.85}"
ENV_VARS="$ENV_VARS,TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN"
ENV_VARS="$ENV_VARS,TELEGRAM_CHAT_ID=$TELEGRAM_CHAT_ID"
ENV_VARS="$ENV_VARS,EMAIL_USERNAME=$EMAIL_USERNAME"
ENV_VARS="$ENV_VARS,EMAIL_PASSWORD=$EMAIL_PASSWORD"
ENV_VARS="$ENV_VARS,OPENAI_API_KEY=$OPENAI_API_KEY"
ENV_VARS="$ENV_VARS,COLLECTION_INTERVAL_MINUTES=${COLLECTION_INTERVAL_MINUTES:-15}"

# Comando de deploy
gcloud run deploy $SERVICE_NAME \
    --image $REGISTRY/$PROJECT_ID/$IMAGE_NAME:$ENVIRONMENT \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --set-env-vars "$ENV_VARS"

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format="value(status.url)")

log "✅ Deploy concluído com sucesso!"
log "🌐 URL do serviço: $SERVICE_URL"
log "📊 Dashboard: $SERVICE_URL/docs"
log "📱 Streamlit Dashboard: $SERVICE_URL" # Se configurado

# Testar se o serviço está online
log "Verificando se o serviço está online..."
sleep 10

if curl -f -s "$SERVICE_URL/health" > /dev/null; then
    log "🟢 Serviço está online e respondendo!"
else
    warning "🔴 Serviço pode não estar respondendo corretamente. Verifique os logs:"
    gcloud logs read "resource.type=cloud_run_revision resource.labels.service_name=$SERVICE_NAME" --limit 10 --format="table(timestamp,textPayload)"
fi

# Configurar monitoramento (opcional)
if command -v kubectl &> /dev/null; then
    log "Configurando monitoramento..."
    # Adicionar configurações de monitoramento aqui se necessário
fi

# Informações úteis
log ""
log "📋 Informações úteis:"
log "• Para ver os logs: gcloud logs tail resource.type=cloud_run_revision resource.labels.service_name=$SERVICE_NAME"
log "• Para atualizar: gcloud run services update $SERVICE_NAME --region $REGION --image $REGISTRY/$PROJECT_ID/$IMAGE_NAME:$ENVIRONMENT"
log "• Para deletar: gcloud run services delete $SERVICE_NAME --region $REGION"
log ""

# Notificação de sucesso (se Telegram configurado)
if [[ -n "$TELEGRAM_BOT_TOKEN" ]] && [[ -n "$TELEGRAM_CHAT_ID" ]]; then
    log "Enviando notificação de deploy para Telegram..."
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d "chat_id=$TELEGRAM_CHAT_ID" \
        -d "text=🚀 Casa Inteligente deployado com sucesso!
Ambiente: $ENVIRONMENT
URL: $SERVICE_URL
Horário: $(date)" > /dev/null
fi

log "Deploy finalizado! 🎉"
