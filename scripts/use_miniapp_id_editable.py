#!/usr/bin/env python3
"""
Usar MiniApp ID para obter Local Key
Edite este script e coloque o MiniApp ID encontrado
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


def use_miniapp_id(miniapp_id):
    """Usar MiniApp ID específico"""

    # Credenciais
    username = os.getenv("SMARTLIFE_USERNAME", "paty7sp@gmail.com")
    password = os.getenv("SMARTLIFE_PASSWORD", "P@ty0740")
    client_id = os.getenv("TUYA_CLIENT_ID", "nwykv3tnwx5na9kvyjvu")
    client_secret = os.getenv("TUYA_CLIENT_SECRET", "021747b14008401f9f173dc693113aef")
    device_id = os.getenv("TUYA_DEVICE_ID", "eb0254d3ac39b4d2740fwq")

    print("🎯 USANDO MINIAPP ID PARA OBTER LOCAL KEY")
    print("=" * 60)
    print(f"MiniApp ID: {miniapp_id}")
    print(f"Device ID: {device_id}")
    print()

    # Tentar diferentes endpoints
    endpoints = [
        "https://openapi.tuyaus.com",
        "https://a1.tuyaus.com",
        "https://a1.tuyacn.com",
    ]

    # Paths para tentar
    paths = [
        f"/v1.0/miniapps/{miniapp_id}/devices",
        f"/v1.0/miniapps/{miniapp_id}/devices/{device_id}",
        f"/v1.0/apps/{miniapp_id}/devices",
        f"/v1.0/apps/{miniapp_id}/devices/{device_id}",
        f"/v1.0/miniapp/{miniapp_id}/devices/{device_id}",
        f"/v1.0/app/{miniapp_id}/device/{device_id}",
    ]

    for base_url in endpoints:
        print(f"\n🌐 Tentando: {base_url}")

        for path in paths:
            print(f"   📡 {path}")

            if try_endpoint(base_url, path, client_id, client_secret, device_id):
                return True

    return False


def try_endpoint(base_url, path, client_id, client_secret, device_id):
    """Tentar endpoint específico"""
    timestamp = str(int(time.time() * 1000))
    nonce = ""

    # Calcular assinatura
    string_to_sign = f"GET\n\n\n{path}"
    message = f"{client_id}{timestamp}{nonce}{string_to_sign}"
    sign = (
        hmac.new(client_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256)
        .hexdigest()
        .upper()
    )

    url = f"{base_url}{path}"

    headers = {
        "client_id": client_id,
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

                print(f"      ✅ Sucesso!")

                # Procurar Local Key
                if isinstance(result, dict):
                    local_key = result.get("local_key")
                    if local_key:
                        print(f"      🎉 LOCAL KEY: {local_key}")
                        save_local_key(local_key)
                        return True

                    # Verificar se é o nosso dispositivo
                    if result.get("id") == device_id:
                        local_key = result.get("local_key")
                        if local_key:
                            print(f"      🎉 LOCAL KEY: {local_key}")
                            save_local_key(local_key)
                            return True

                print(f"      📋 Dados: {json.dumps(result, indent=6)[:200]}...")

            else:
                print(f"      ❌ Erro {data.get('code')}: {data.get('msg')}")

        else:
            print(f"      ❌ HTTP {response.status_code}")

    except Exception as e:
        print(f"      ❌ {str(e)[:50]}")

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

    # 🔧 EDITE AQUI: Coloque o MiniApp ID encontrado
    miniapp_id = "tydxwunc8rjqvh4gaw"  # <-- EDITE ESTA LINHA

    if miniapp_id == "COLOQUE_O_MINIAPP_ID_AQUI":
        print("❌ EDITE O SCRIPT PRIMEIRO!")
        print("=" * 60)
        print("1. Abra este script")
        print("2. Altere a linha:")
        print('   miniapp_id = "tydxwunc8rjqvh4gaw"')
        print("3. Coloque o MiniApp ID que você encontrou")
        print("4. Execute novamente")
        return

    result = use_miniapp_id(miniapp_id)

    print("\n" + "=" * 60)

    if result:
        print("🎉 SUCESSO! LOCAL KEY OBTIDA VIA MINIAPP!")
        print("=" * 60)
        print("✅ Execute: python scripts/test_manual_local_key.py")
        print("✅ Execute: python scripts/monitor_novadigital_final.py")
    else:
        print("❌ MINIAPP ID NÃO FUNCIONOU")
        print("=" * 60)
        print()
        print("💡 TENTE:")
        print("   1. Verificar se o ID está correto")
        print("   2. Procurar por outro ID no app")
        print("   3. Resetar tomada (SOLUCAO_FINAL_RESETAR.md)")


if __name__ == "__main__":
    main()
