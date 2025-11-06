#!/usr/bin/env python3
"""
Script para configurar secrets no GitHub Actions via API
"""

import json
import base64
import requests
from pathlib import Path
from nacl import encoding, public

# Configurações
GITHUB_TOKEN = input("Cole seu GitHub Personal Access Token (com permissão repo): ").strip()
REPO_OWNER = "Patricia7sp"
REPO_NAME = "casa-inteligente"

# Headers para API
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {GITHUB_TOKEN}",
}

def get_public_key():
    """Obter chave pública do repositório para criptografar secrets"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/public-key"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Criptografar secret usando a chave pública do repositório"""
    public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def set_secret(secret_name: str, secret_value: str, key_id: str, public_key: str):
    """Configurar um secret no GitHub"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/{secret_name}"
    
    encrypted_value = encrypt_secret(public_key, secret_value)
    
    data = {
        "encrypted_value": encrypted_value,
        "key_id": key_id
    }
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code in [201, 204]:
        print(f"✅ Secret '{secret_name}' configurado com sucesso!")
        return True
    else:
        print(f"❌ Erro ao configurar '{secret_name}': {response.status_code}")
        print(f"   Resposta: {response.text}")
        return False

def main():
    print("🔐 CONFIGURANDO SECRETS NO GITHUB ACTIONS")
    print("=" * 60)
    print()
    
    # Obter chave pública
    print("📥 Obtendo chave pública do repositório...")
    try:
        key_data = get_public_key()
        key_id = key_data["key_id"]
        public_key = key_data["key"]
        print(f"✅ Chave pública obtida: {key_id}")
        print()
    except Exception as e:
        print(f"❌ Erro ao obter chave pública: {e}")
        return
    
    # Secrets para configurar
    secrets = {}
    
    # 1. GCP_PROJECT_ID
    secrets["GCP_PROJECT_ID"] = "casa-inteligente-477314"
    
    # 2. GCP_SA_KEY
    gcp_key_file = Path("config/gcp-sa-key.json")
    if gcp_key_file.exists():
        with open(gcp_key_file, 'r') as f:
            secrets["GCP_SA_KEY"] = f.read()
    else:
        print("⚠️  Arquivo config/gcp-sa-key.json não encontrado!")
        secrets["GCP_SA_KEY"] = input("Cole o conteúdo do GCP_SA_KEY (JSON completo): ").strip()
    
    # 3. DATABASE_URL
    secrets["DATABASE_URL"] = "postgresql://postgres:casa_inteligente_2024@localhost:5432/casa_inteligente"
    
    # 4. REDIS_URL
    secrets["REDIS_URL"] = "redis://localhost:6379"
    
    # Opcionais - perguntar se quer configurar
    print()
    print("📋 SECRETS OPCIONAIS")
    print("-" * 60)
    
    if input("Configurar TAPO_USERNAME? (s/n): ").lower() == 's':
        secrets["TAPO_USERNAME"] = input("TAPO_USERNAME: ").strip()
    
    if input("Configurar TAPO_PASSWORD? (s/n): ").lower() == 's':
        secrets["TAPO_PASSWORD"] = input("TAPO_PASSWORD: ").strip()
    
    if input("Configurar TELEGRAM_BOT_TOKEN? (s/n): ").lower() == 's':
        secrets["TELEGRAM_BOT_TOKEN"] = input("TELEGRAM_BOT_TOKEN: ").strip()
    
    if input("Configurar TELEGRAM_CHAT_ID? (s/n): ").lower() == 's':
        secrets["TELEGRAM_CHAT_ID"] = input("TELEGRAM_CHAT_ID: ").strip()
    
    if input("Configurar EMAIL_USERNAME? (s/n): ").lower() == 's':
        secrets["EMAIL_USERNAME"] = input("EMAIL_USERNAME: ").strip()
    
    if input("Configurar EMAIL_PASSWORD? (s/n): ").lower() == 's':
        secrets["EMAIL_PASSWORD"] = input("EMAIL_PASSWORD: ").strip()
    
    if input("Configurar OPENAI_API_KEY? (s/n): ").lower() == 's':
        secrets["OPENAI_API_KEY"] = input("OPENAI_API_KEY: ").strip()
    
    # Configurar todos os secrets
    print()
    print("🚀 CONFIGURANDO SECRETS...")
    print("=" * 60)
    
    success_count = 0
    for secret_name, secret_value in secrets.items():
        if secret_value:
            if set_secret(secret_name, secret_value, key_id, public_key):
                success_count += 1
    
    print()
    print("=" * 60)
    print(f"✅ {success_count}/{len(secrets)} secrets configurados com sucesso!")
    print()
    print("🎯 PRÓXIMOS PASSOS:")
    print("1. Verificar secrets em: https://github.com/Patricia7sp/casa-inteligente/settings/secrets/actions")
    print("2. Fazer commit e push para testar CI/CD")
    print("3. Acompanhar em: https://github.com/Patricia7sp/casa-inteligente/actions")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
