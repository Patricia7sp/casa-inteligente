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

# Expor porta (Cloud Run usa variável PORT)
EXPOSE 8000
ENV PORT=8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Comando para iniciar a aplicação
CMD exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT} --timeout-keep-alive 60
