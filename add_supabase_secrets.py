#!/usr/bin/env python3
"""
Script para adicionar secrets do Supabase no GitHub
"""
import requests
import base64
from nacl import encoding, public
import json

# Configurações
GITHUB_TOKEN = input("Cole seu GitHub Personal Access Token: ").strip()
REPO_OWNER = "Patricia7sp"
REPO_NAME = "casa-inteligente"

# Secrets do Supabase
SUPABASE_URL = "https://pqqrodiuuhckvdqawgeg.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxcXJvZGl1dWhja3ZkcWF3Z2VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0OTI0MTIsImV4cCI6MjA3ODA2ODQxMn0.ve7NIbFcZdTGa16O3Pttmpx2mxWgklvbPwwTSCHuDFs"

def get_public_key():
    """Obter chave pública do repositório"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/public-key"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Erro ao obter chave pública: {response.status_code}")
        print(response.text)
        return None

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Criptografar secret"""
    public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def create_or_update_secret(secret_name: str, secret_value: str, key_id: str, public_key: str):
    """Criar ou atualizar secret"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/{secret_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    encrypted_value = encrypt_secret(public_key, secret_value)
    
    data = {
        "encrypted_value": encrypted_value,
        "key_id": key_id
    }
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code in [201, 204]:
        print(f"✅ Secret '{secret_name}' criado/atualizado com sucesso!")
        return True
    else:
        print(f"❌ Erro ao criar secret '{secret_name}': {response.status_code}")
        print(response.text)
        return False

def main():
    print("🔐 Adicionando secrets do Supabase no GitHub...")
    
    # Obter chave pública
    key_data = get_public_key()
    if not key_data:
        print("❌ Falha ao obter chave pública")
        return
    
    key_id = key_data["key_id"]
    public_key = key_data["key"]
    
    print(f"✅ Chave pública obtida: {key_id}")
    
    # Adicionar secrets
    secrets = {
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_ANON_KEY": SUPABASE_ANON_KEY
    }
    
    for name, value in secrets.items():
        create_or_update_secret(name, value, key_id, public_key)
    
    print("\n🎉 Processo concluído!")
    print("\n📝 Próximos passos:")
    print("1. Faça commit e push do workflow atualizado")
    print("2. O próximo deploy usará os secrets do Supabase")
    print("3. O coletor começará a funcionar automaticamente")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro: {str(e)}")
