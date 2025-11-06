# Imagem base Python
FROM python:3.10-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY src/ ./src/
COPY .env.example .env

# Criar diretório de logs
RUN mkdir -p logs

# Cloud Run injeta a variável PORT automaticamente
# Não definir PORT aqui, deixar Cloud Run controlar

# Comando para iniciar a aplicação
# Cloud Run passa a porta via $PORT
CMD exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080} --timeout-keep-alive 60 --log-level info
