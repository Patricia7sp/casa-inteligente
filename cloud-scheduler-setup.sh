#!/bin/bash
# Script para configurar Cloud Scheduler para manter o coletor TAPO ativo

PROJECT_ID="casa-inteligente-858582953113"
REGION="us-central1"
SERVICE_NAME="casa-inteligente-api"
SCHEDULER_JOB_NAME="keep-collector-alive"
SCHEDULE="*/5 * * * *"  # A cada 5 minutos

echo "🔧 Configurando Cloud Scheduler para manter o coletor ativo..."
echo "📦 Projeto: $PROJECT_ID"
echo "🌎 Região: $REGION"
echo "⏰ Frequência: A cada 5 minutos"
echo ""

# Obter URL do serviço Cloud Run
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)')

if [ -z "$SERVICE_URL" ]; then
  echo "❌ Erro: Não foi possível obter a URL do serviço $SERVICE_NAME"
  exit 1
fi

HEALTH_ENDPOINT="${SERVICE_URL}/health"
echo "🔗 Endpoint de health check: $HEALTH_ENDPOINT"
echo ""

# Verificar se o job já existe
EXISTING_JOB=$(gcloud scheduler jobs list \
  --location=$REGION \
  --filter="name:$SCHEDULER_JOB_NAME" \
  --format="value(name)" 2>/dev/null)

if [ -n "$EXISTING_JOB" ]; then
  echo "⚠️  Job '$SCHEDULER_JOB_NAME' já existe. Atualizando..."
  gcloud scheduler jobs update http $SCHEDULER_JOB_NAME \
    --location=$REGION \
    --schedule="$SCHEDULE" \
    --uri="$HEALTH_ENDPOINT" \
    --http-method=GET \
    --attempt-deadline=60s
else
  echo "✨ Criando novo job '$SCHEDULER_JOB_NAME'..."
  gcloud scheduler jobs create http $SCHEDULER_JOB_NAME \
    --location=$REGION \
    --schedule="$SCHEDULE" \
    --uri="$HEALTH_ENDPOINT" \
    --http-method=GET \
    --attempt-deadline=60s \
    --description="Mantém o container da API ativo para coleta contínua de dados TAPO"
fi

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ Cloud Scheduler configurado com sucesso!"
  echo ""
  echo "📊 Para verificar o status do job:"
  echo "   gcloud scheduler jobs describe $SCHEDULER_JOB_NAME --location=$REGION"
  echo ""
  echo "🔍 Para ver os logs de execução:"
  echo "   gcloud scheduler jobs logs $SCHEDULER_JOB_NAME --location=$REGION --limit=10"
  echo ""
  echo "🚀 Para executar manualmente agora:"
  echo "   gcloud scheduler jobs run $SCHEDULER_JOB_NAME --location=$REGION"
  echo ""
  echo "💡 O job irá fazer ping no endpoint /health a cada 5 minutos,"
  echo "   mantendo o container ativo e o loop de coleta rodando."
else
  echo ""
  echo "❌ Erro ao configurar Cloud Scheduler"
  exit 1
fi
