#!/bin/bash

# Script para criar repositório GitHub via API
# Uso: ./scripts/create_github_repo.sh SEU_TOKEN

set -e

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar token
if [ -z "$1" ]; then
    echo -e "${RED}ERRO: Token do GitHub não fornecido${NC}"
    echo "Uso: $0 SEU_GITHUB_TOKEN"
    exit 1
fi

TOKEN="$1"
REPO_NAME="casa-inteligente"
REPO_DESCRIPTION="Sistema inteligente para monitoramento de consumo de energia residencial"
USERNAME="Patricia7sp"

echo -e "${YELLOW}Criando repositório GitHub: $REPO_NAME${NC}"

# Criar repositório via API
response=$(curl -s -w "%{http_code}" -o /tmp/repo_response.json \
    -X POST \
    -H "Authorization: token $TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/user/repos \
    -d "{
        \"name\": \"$REPO_NAME\",
        \"description\": \"$REPO_DESCRIPTION\",
        \"private\": false,
        \"has_issues\": true,
        \"has_projects\": true,
        \"has_wiki\": true,
        \"auto_init\": false
    }")

http_code="${response: -3}"

if [ "$http_code" -eq 201 ]; then
    echo -e "${GREEN}✅ Repositório criado com sucesso!${NC}"
    
    # Obter URL do repositório
    repo_url=$(jq -r '.clone_url' /tmp/repo_response.json)
    echo -e "${GREEN}📦 URL do repositório: $repo_url${NC}"
    
    # Configurar remote
    echo -e "${YELLOW}Configurando remote origin...${NC}"
    git remote add origin $repo_url
    
    # Fazer push
    echo -e "${YELLOW}Fazendo push do código...${NC}"
    git push -u origin main
    
    echo -e "${GREEN}🚀 Repositório configurado e código enviado!${NC}"
    echo -e "${GREEN}🔗 Acesse: https://github.com/$USERNAME/$REPO_NAME${NC}"
    
else
    echo -e "${RED}❌ Erro ao criar repositório (HTTP $http_code)${NC}"
    cat /tmp/repo_response.json
    exit 1
fi

# Limpar arquivo temporário
rm -f /tmp/repo_response.json
