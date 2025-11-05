#!/usr/bin/env python3
"""
Usar UID da conta para obter Local Key
UID: az1762259983829275FA
"""

import requests
import json
import time
import hashlib
import hmac
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


def use_uid_to_get_devices(uid):
    """Usar UID da conta para obter dispositivos"""

    client_id = os.getenv("TUYA_CLIENT_ID", "nwykv3tnwx5na9kvyjvu")
    client_secret = os.getenv("TUYA_CLIENT_SECRET", "021747b14008401f9f173dc693113aef")
    device_id = os.getenv("TUYA_DEVICE_ID", "eb0254d3ac39b4d2740fwq")

    print("🎯 USANDO UID DA CONTA PARA OBTER LOCAL KEY")
    print("=" * 60)
    print(f"UID: {uid}")
    print(f"Device ID: {device_id}")
    print()

    # Primeiro, obter token
    print("1️⃣ OBTENDO TOKEN DE ACESSO")
    print("-" * 40)

    access_token = get_access_token(client_id, client_secret)

    if not access_token:
        print("❌ Falha ao obter token")
        return False

    print(f"✅ Token obtido: {access_token[:20]}...")

    # Tentar diferentes endpoints com UID
    print("\n2️⃣ TENTANDO ENDPOINTS COM UID")
    print("-" * 40)

    endpoints = [
        f"/v1.0/users/{uid}/devices",
        f"/v2.0/cloud/thing/{uid}/device",
        f"/v1.0/iot-03/users/{uid}/devices",
        f"/v1.0/devices?uid={uid}",
        f"/v1.1/users/{uid}/devices",
    ]

    for endpoint in endpoints:
        print(f"\n📡 Tentando: {endpoint}")

        if try_endpoint_with_token(
            endpoint, access_token, client_id, client_secret, device_id
        ):
            return True

    # Tentar endpoint direto do dispositivo com token
    print("\n3️⃣ TENTANDO ENDPOINT DIRETO DO DISPOSITIVO")
    print("-" * 40)

    return try_device_endpoint_with_token(
        device_id, access_token, client_id, client_secret
    )


def get_access_token(client_id, client_secret):
    """Obter token de acesso"""

    timestamp = str(int(time.time() * 1000))
    nonce = ""

    # Calcular assinatura para obter token
    string_to_sign = f"GET\n\n\n/v1.0/token?grant_type=1"
    message = f"{client_id}{timestamp}{nonce}{string_to_sign}"
    sign = (
        hmac.new(client_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256)
        .hexdigest()
        .upper()
    )

    url = "https://openapi.tuyaus.com/v1.0/token?grant_type=1"

    headers = {
        "client_id": client_id,
        "sign": sign,
        "sign_method": "HMAC-SHA256",
        "t": timestamp,
        "nonce": nonce,
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            if data.get("success"):
                return data["result"]["access_token"]
            else:
                print(f"   ❌ Erro: {data.get('msg')} (código: {data.get('code')})")
        else:
            print(f"   ❌ HTTP {response.status_code}")

    except Exception as e:
        print(f"   ❌ Erro: {e}")

    return None


def try_endpoint_with_token(
    endpoint, access_token, client_id, client_secret, device_id
):
    """Tentar endpoint com token"""

    timestamp = str(int(time.time() * 1000))
    nonce = ""

    # Calcular assinatura
    string_to_sign = f"GET\n\n\n{endpoint}"
    message = f"{client_id}{timestamp}{nonce}{string_to_sign}"
    sign = (
        hmac.new(client_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256)
        .hexdigest()
        .upper()
    )

    url = f"https://openapi.tuyaus.com{endpoint}"

    headers = {
        "client_id": client_id,
        "access_token": access_token,
        "sign": sign,
        "sign_method": "HMAC-SHA256",
        "t": timestamp,
        "nonce": nonce,
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if data.get("success"):
                result = data["result"]

                print(f"   ✅ Sucesso!")

                # Se for lista de dispositivos
                if isinstance(result, list):
                    print(f"   📱 Dispositivos encontrados: {len(result)}")

                    for device in result:
                        print(f"\n   📱 {device.get('name', 'Sem nome')}")
                        print(f"      ID: {device.get('id')}")
                        print(f"      Online: {device.get('online')}")

                        local_key = device.get("local_key")
                        if local_key:
                            print(f"      🔑 Local Key: {local_key}")

                            # Se for nosso dispositivo
                            if device.get("id") == device_id:
                                print(f"      ✅ É o nosso dispositivo!")
                                save_local_key(local_key)
                                return True
                        else:
                            print(f"      ⚠️ Local Key não disponível")

                # Se for dispositivo único
                elif isinstance(result, dict):
                    local_key = result.get("local_key")
                    if local_key:
                        print(f"   🎉 LOCAL KEY: {local_key}")
                        save_local_key(local_key)
                        return True

                    print(f"   📋 Dados: {json.dumps(result, indent=6)[:300]}...")

            else:
                print(f"   ❌ Erro: {data.get('msg')} (código: {data.get('code')})")

        else:
            print(f"   ❌ HTTP {response.status_code}")

    except Exception as e:
        print(f"   ❌ Erro: {str(e)[:50]}")

    return False


def try_device_endpoint_with_token(device_id, access_token, client_id, client_secret):
    """Tentar endpoint direto do dispositivo com token válido"""

    timestamp = str(int(time.time() * 1000))
    nonce = ""

    endpoint = f"/v1.0/devices/{device_id}"
    string_to_sign = f"GET\n\n\n{endpoint}"

    message = f"{client_id}{timestamp}{nonce}{string_to_sign}"
    sign = (
        hmac.new(client_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256)
        .hexdigest()
        .upper()
    )

    url = f"https://openapi.tuyaus.com{endpoint}"

    headers = {
        "client_id": client_id,
        "access_token": access_token,
        "sign": sign,
        "sign_method": "HMAC-SHA256",
        "t": timestamp,
        "nonce": nonce,
    }

    try:
        print(f"📡 Tentando: {endpoint}")
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            if data.get("success"):
                device = data["result"]

                print(f"   ✅ Dispositivo encontrado!")
                print(f"   Nome: {device.get('name')}")
                print(f"   ID: {device.get('id')}")
                print(f"   Online: {device.get('online')}")

                local_key = device.get("local_key")
                if local_key:
                    print(f"\n   🎉 LOCAL KEY ENCONTRADA!")
                    print(f"   Local Key: {local_key}")
                    save_local_key(local_key)
                    return True
                else:
                    print(f"\n   ⚠️ Local Key não retornada")
                    print(f"   Dados completos:")
                    print(json.dumps(device, indent=6))

            else:
                print(f"   ❌ Erro: {data.get('msg')} (código: {data.get('code')})")

        else:
            print(f"   ❌ HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")

    except Exception as e:
        print(f"   ❌ Erro: {e}")

    return False


def save_local_key(local_key):
    """Salvar Local Key no .env"""
    print(f"\n💾 Salvando Local Key no .env...")

    with open(".env", "r") as f:
        lines = f.readlines()

    updated = False
    for i, line in enumerate(lines):
        if line.startswith("TUYA_LOCAL_KEY="):
            lines[i] = f"TUYA_LOCAL_KEY={local_key}\n"
            updated = True
            break

    if not updated:
        lines.append(f"\nTUYA_LOCAL_KEY={local_key}\n")

    with open(".env", "w") as f:
        f.writelines(lines)

    print(f"✅ Local Key salva no .env!")


def main():
    """Função principal"""

    # UID da conta encontrado na plataforma
    uid = "az1762259983829275FA"

    print("🎯 TENTATIVA COM UID DA CONTA")
    print("=" * 60)
    print("Você vinculou o app na plataforma Tuya!")
    print("Agora vamos usar o UID para obter a Local Key.")
    print()

    result = use_uid_to_get_devices(uid)

    print("\n" + "=" * 60)

    if result:
        print("🎉 SUCESSO! LOCAL KEY OBTIDA!")
        print("=" * 60)
        print("✅ Local Key salva no .env")
        print()
        print("📋 PRÓXIMOS PASSOS:")
        print("   1. Execute: python scripts/test_manual_local_key.py")
        print("   2. Execute: python scripts/monitor_novadigital_final.py")
        print("   3. Monitoramento funcionando! 🎯")
    else:
        print("❌ UID NÃO LIBEROU LOCAL KEY")
        print("=" * 60)
        print()
        print("💡 POSSÍVEL RAZÃO:")
        print("   A API pode estar retornando dispositivos")
        print("   mas sem a Local Key no response.")
        print()
        print("🎯 TENTE:")
        print("   1. Na plataforma, clique em 'Manage Devices'")
        print("   2. Encontre seu dispositivo")
        print("   3. Clique em 'Device Details'")
        print("   4. Procure por 'Local Key' na página")
        print("   5. Copie manualmente se aparecer")


if __name__ == "__main__":
    main()
