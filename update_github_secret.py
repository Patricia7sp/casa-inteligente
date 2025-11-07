"""
Script para atualizar DATABASE_URL no GitHub Secrets
"""
import requests
import base64
from nacl import encoding, public
import os

# Configurações
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Forneça via variável de ambiente
REPO_OWNER = "Patricia7sp"
REPO_NAME = "casa-inteligente"
SECRET_NAME = "DATABASE_URL"
SECRET_VALUE = "postgresql://postgres:hafbuf-6vomdo-bucsUq@db.pqqrodiuuhckvdqawgeg.supabase.co:5432/postgres"

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

# 1. Obter a public key do repositório
print("📥 Obtendo public key do repositório...")
response = requests.get(
    f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/public-key",
    headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
)

if response.status_code != 200:
    print(f"❌ Erro ao obter public key: {response.status_code}")
    print(response.text)
    exit(1)

public_key_data = response.json()
public_key = public_key_data["key"]
key_id = public_key_data["key_id"]

print(f"✅ Public key obtida (Key ID: {key_id})")

# 2. Criptografar o secret
print("🔒 Criptografando DATABASE_URL...")
encrypted_value = encrypt_secret(public_key, SECRET_VALUE)
print("✅ Secret criptografado")

# 3. Criar/atualizar o secret
print(f"📤 Atualizando secret '{SECRET_NAME}' no GitHub...")
response = requests.put(
    f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/{SECRET_NAME}",
    headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    },
    json={
        "encrypted_value": encrypted_value,
        "key_id": key_id
    }
)

if response.status_code in [201, 204]:
    print(f"✅ Secret '{SECRET_NAME}' atualizado com sucesso!")
    print(f"\n📝 DATABASE_URL configurado:")
    print(f"   postgresql://postgres:***@db.pqqrodiuuhckvdqawgeg.supabase.co:5432/postgres")
    print(f"\n🚀 Próximos passos:")
    print(f"   1. Execute o SQL no Supabase: supabase_schema.sql")
    print(f"   2. Faça commit e push para triggerar o CI/CD")
    print(f"   3. O deploy usará a nova DATABASE_URL do Supabase")
else:
    print(f"❌ Erro ao atualizar secret: {response.status_code}")
    print(response.text)
    exit(1)
