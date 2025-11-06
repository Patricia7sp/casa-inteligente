#!/bin/bash
set -e

# Usar a porta fornecida pelo Cloud Run ou 8080 como padrão
PORT=${PORT:-8080}

echo "🚀 Iniciando Casa Inteligente na porta $PORT..."

# Iniciar uvicorn
exec uvicorn src.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --timeout-keep-alive 60 \
    --log-level info \
    --access-log
