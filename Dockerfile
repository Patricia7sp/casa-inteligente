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
COPY entrypoint.sh .

# Criar diretório de logs
RUN mkdir -p logs

# Dar permissão de execução ao entrypoint
RUN chmod +x entrypoint.sh

# Cloud Run injeta a variável PORT automaticamente
# Não definir PORT aqui, deixar Cloud Run controlar

# Comando para iniciar a aplicação
CMD ["./entrypoint.sh"]
