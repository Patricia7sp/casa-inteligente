#!/usr/bin/env python3
"""
Verificar se as credenciais Tuya são válidas
"""

import asyncio
import aiohttp
import json
import hashlib
import time
import hmac
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from utils.config import settings


async def verify_credentials():
    """Verificar validade das credenciais"""
    print("🔍 VERIFICANDO CREDENCIAIS TUYA")
    print("=" * 50)

    access_id = getattr(settings, "tuya_access_id", None)
    access_key = getattr(settings, "tuya_access_key", None)
    region = getattr(settings, "tuya_region", "us")

    if not all([access_id, access_key]):
        print("❌ Configurações não encontradas")
        return

    print(f"Access ID: {access_id}")
    print(f"Access Key: {access_key[:10]}...")
    print(f"Region: {region}")

    # Verificar formato
    if len(access_id) != 20:
        print(f"⚠️  Access ID deveria ter 20 caracteres (tem {len(access_id)})")

    if len(access_key) != 32:
        print(f"⚠️  Access Key deveria ter 32 caracteres (tem {len(access_key)})")

    # Tentar diferentes endpoints
    endpoints = [
        f"https://openapi.tuya{region}.com",
        "https://openapi.tuyaus.com",
        "https://openapi.tuyaeu.com",
    ]

    for base_url in endpoints:
        print(f"\n🌐 Testando endpoint: {base_url}")

        try:
            async with aiohttp.ClientSession() as session:

                # Testar com timestamp atual
                timestamp = str(int(time.time() * 1000))
                path = "/v1.0/token?grant_type=1"
                string_to_sign = f"GET\napplication/json\n{timestamp}\n{path}"

                signature = hmac.new(
                    access_key.encode("utf-8"),
                    string_to_sign.encode("utf-8"),
                    hashlib.sha256,
                ).hexdigest()

                headers = {
                    "Content-Type": "application/json",
                    "X-T": timestamp,
                    "client_id": access_id,
                    "sign": signature.upper(),
                    "sign_method": "HMAC-SHA256",
                }

                async with session.get(
                    f"{base_url}{path}", headers=headers, timeout=10
                ) as response:
                    result = await response.json()

                    print(f"   Status: {response.status}")
                    print(f"   Código: {result.get('code')}")
                    print(f"   Mensagem: {result.get('msg')}")

                    if result.get("code") == 1013:
                        print(
                            f"   ⚠️  Erro de timestamp (problema que estamos tentando corrigir)"
                        )
                    elif result.get("code") == 1004:
                        print(f"   ❌ Access ID inválido")
                    elif result.get("code") == 1005:
                        print(f"   ❌ Assinatura inválida")
                    elif result.get("code") == 1007:
                        print(f"   ❌ Access Key inválida")
                    elif result.get("code") == 1008:
                        print(f"   ❌ Projeto não encontrado")
                    elif result.get("code") == 1106:
                        print(f"   ❌ Projeto suspenso")
                    elif result.get("success"):
                        print(f"   ✅ SUCESSO! Credenciais válidas")
                        return True
                    else:
                        print(f"   ❓ Código desconhecido: {result}")

        except Exception as e:
            print(f"   ❌ Erro de conexão: {e}")

    return False


async def test_simple_signature():
    """Testar assinatura simplificada"""
    print(f"\n🧪 TESTE ASSINATURA SIMPLIFICADA")
    print("=" * 50)

    access_id = getattr(settings, "tuya_access_id", None)
    access_key = getattr(settings, "tuya_access_key", None)

    # Teste com exemplo da documentação
    timestamp = "1234567890123"
    path = "/v1.0/token?grant_type=1"
    string_to_sign = f"GET\napplication/json\n{timestamp}\n{path}"

    signature = hmac.new(
        access_key.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    print(f"String to sign: {repr(string_to_sign)}")
    print(f"Signature: {signature.upper()}")
    print(f"Expected format: 64 character uppercase hex string")

    if len(signature) == 64 and all(c in "0123456789abcdef" for c in signature.lower()):
        print(f"✅ Formato da assinatura correto")
    else:
        print(f"❌ Formato da assinatura inválido")


async def main():
    await test_simple_signature()
    success = await verify_credentials()

    if success:
        print(f"\n✅ CREDENCIAIS VÁLIDAS!")
        print(f"   O problema é apenas o timestamp")
    else:
        print(f"\n❌ PROBLEMA NAS CREDENCIAIS!")
        print(f"   Verifique:")
        print(f"   1. Access ID e Access Key corretos")
        print(f"   2. Projeto Cloud ativo")
        print(f"   3. Região correta (us, eu, cn)")


if __name__ == "__main__":
    asyncio.run(main())
