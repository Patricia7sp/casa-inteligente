#!/bin/bash
# Script para configurar gcloud e criar credenciais automaticamente
# Projeto: casa-inteligente-477314
# Email: paty7sp@gmail.com

set -e

PROJECT_ID="casa-inteligente-477314"
EMAIL="paty7sp@gmail.com"
APP_NAME="casa-inteligente-monitor"

echo "🎯 CONFIGURAÇÃO AUTOMÁTICA DO GCLOUD"
echo "============================================================"
echo "📁 Projeto: $PROJECT_ID"
echo "📧 Email: $EMAIL"
echo ""

# 1. Fazer login (abrirá navegador)
echo "1️⃣ FAZENDO LOGIN NO GCLOUD"
echo "------------------------------------------------------------"
echo "Abrindo navegador para autenticação..."
gcloud auth login $EMAIL --brief

# 2. Configurar projeto
echo ""
echo "2️⃣ CONFIGURANDO PROJETO"
echo "------------------------------------------------------------"
gcloud config set project $PROJECT_ID
echo "✅ Projeto configurado: $PROJECT_ID"

# 3. Configurar conta
echo ""
echo "3️⃣ CONFIGURANDO CONTA"
echo "------------------------------------------------------------"
gcloud config set account $EMAIL
echo "✅ Conta configurada: $EMAIL"

# 4. Ativar Gmail API
echo ""
echo "4️⃣ ATIVANDO GMAIL API"
echo "------------------------------------------------------------"
gcloud services enable gmail.googleapis.com
echo "✅ Gmail API ativada"

# 5. Ativar APIs necessárias
echo ""
echo "5️⃣ ATIVANDO APIS NECESSÁRIAS"
echo "------------------------------------------------------------"
gcloud services enable iamcredentials.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
echo "✅ APIs ativadas"

# 6. Criar credenciais OAuth
echo ""
echo "6️⃣ CRIANDO CREDENCIAIS OAUTH"
echo "------------------------------------------------------------"

# Verificar se já existe
if [ -f "config/gmail_credentials.json" ]; then
    echo "⚠️  Credenciais já existem em config/gmail_credentials.json"
    read -p "Deseja substituir? (s/n): " replace
    if [ "$replace" != "s" ]; then
        echo "⏭️  Mantendo credenciais existentes"
        exit 0
    fi
fi

# Criar OAuth client
echo "Criando OAuth client..."

# Nota: gcloud não tem comando direto para criar OAuth client
# Vamos usar a API REST
echo ""
echo "⚠️  ATENÇÃO:"
echo "O gcloud CLI não suporta criação automática de OAuth clients."
echo "Vou criar um script Python que usa a API do Google Cloud."
echo ""

# 7. Criar script Python para OAuth
cat > /tmp/create_oauth_client.py << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
import subprocess
import json
import sys

def create_oauth_client():
    project_id = "casa-inteligente-477314"
    
    print("Criando OAuth client via API...")
    
    # Obter token de acesso
    result = subprocess.run(
        ['gcloud', 'auth', 'print-access-token'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Erro ao obter token")
        sys.exit(1)
    
    access_token = result.stdout.strip()
    
    # Criar OAuth client via API REST
    import requests
    
    url = f"https://oauth2.googleapis.com/v2/clients"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'client_name': 'Energy Monitor',
        'client_type': 'DESKTOP',
        'redirect_uris': ['http://localhost']
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        client_data = response.json()
        
        # Salvar credenciais
        credentials = {
            'installed': {
                'client_id': client_data['client_id'],
                'client_secret': client_data['client_secret'],
                'redirect_uris': ['http://localhost'],
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token'
            }
        }
        
        with open('config/gmail_credentials.json', 'w') as f:
            json.dump(credentials, f, indent=2)
        
        print("✅ Credenciais criadas e salvas!")
        return True
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)
        return False

if __name__ == '__main__':
    create_oauth_client()
PYTHON_SCRIPT

python3 /tmp/create_oauth_client.py

echo ""
echo "============================================================"
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo "============================================================"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "   1. Autenticar: python src/integrations/gmail_client.py"
echo "   2. Testar: python src/agents/weekly_energy_agent.py --now"
echo ""
