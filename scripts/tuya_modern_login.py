#!/usr/bin/env python3
"""
Tentar login Tuya com endpoints mais recentes
"""

import os
import requests
import json
import hashlib
import time
import hmac
from pathlib import Path


def load_credentials():
    """Carregar credenciais do .env"""
    env_path = Path(__file__).parent.parent / ".env"

    env_vars = {}
    try:
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    except:
        pass

    username = env_vars.get("TUYA_USERNAME") or env_vars.get("username")
    password = env_vars.get("TUYA_PASSWORD") or env_vars.get("password")

    return username, password


def try_modern_login(username, password):
    """Tentar endpoints mais modernos"""
    print("🔐 TENTANDO ENDPOINTS MODERNOS")
    print("=" * 50)

    # Endpoints mais recentes do Tuya
    modern_endpoints = [
        {
            "url": "https://a1.tuyacn.com/v1.0/users/login",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": {
                "username": username,
                "password": password,
                "countryCode": "55",
                "bizType": "SMART_HOME",
            },
        },
        {
            "url": "https://a1.tuyaus.com/v1.0/users/login",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": {
                "username": username,
                "password": password,
                "countryCode": "55",
                "bizType": "SMART_HOME",
            },
        },
        {
            "url": "https://auth.tuya.com/api/login",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": {"username": username, "password": password, "countryCode": "55"},
        },
        {
            "url": "https://passport.tuya.com/api/login",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": {"username": username, "password": password, "countryCode": "55"},
        },
    ]

    for endpoint in modern_endpoints:
        print(f"\n🔍 Testando: {endpoint['url']}")

        try:
            response = requests.request(
                method=endpoint["method"],
                url=endpoint["url"],
                headers=endpoint["headers"],
                json=endpoint["data"],
                timeout=15,
            )

            print(f"   Status: {response.status_code}")
            print(f"   Resposta: {response.text}")

            if response.status_code == 200:
                result = response.json()

                if result.get("success") or result.get("code") == 200:
                    print(f"   ✅ LOGIN BEM-SUCEDIDO!")

                    # Extrair token
                    if "result" in result:
                        token = result["result"].get("access_token")
                    elif "data" in result:
                        token = result["data"].get("access_token")
                    else:
                        token = result.get("access_token")

                    if token:
                        print(f"   📋 Token: {token[:20]}...")
                        return {"access_token": token, "endpoint": endpoint["url"]}
                else:
                    print(
                        f"   ❌ Erro: {result.get('msg', result.get('message', 'Unknown'))}"
                    )
            else:
                print(f"   ❌ HTTP {response.status_code}")

        except Exception as e:
            print(f"   ❌ Erro: {e}")

    return None


def try_tuya_cloud_login(username, password):
    """Tentar login via Tuya Cloud API"""
    print("\n☁️ TENTANDO TUYA CLOUD API")
    print("=" * 50)

    # Endpoint da Cloud API
    cloud_endpoints = [
        "https://openapi.tuyacn.com/v1.0/iot-03/users/login",
        "https://openapi.tuyaus.com/v1.0/iot-03/users/login",
        "https://openapi.tuyaeu.com/v1.0/iot-03/users/login",
    ]

    for endpoint in cloud_endpoints:
        print(f"\n🔍 Testando: {endpoint}")

        try:
            data = {"username": username, "password": password, "countryCode": "55"}

            response = requests.post(endpoint, json=data, timeout=15)
            print(f"   Status: {response.status_code}")
            print(f"   Resposta: {response.text}")

            if response.status_code == 200:
                result = response.json()

                if result.get("success"):
                    print(f"   ✅ LOGIN CLOUD BEM-SUCEDIDO!")

                    token = result.get("result", {}).get("access_token")
                    if token:
                        print(f"   📋 Token: {token[:20]}...")
                        return {"access_token": token, "endpoint": endpoint}

        except Exception as e:
            print(f"   ❌ Erro: {e}")

    return None


def try_device_list_with_token(login_info):
    """Tentar listar dispositivos com token"""
    print(f"\n📱 TENTANDO LISTAR DISPOSITIVOS")
    print("=" * 50)

    token = login_info["access_token"]

    # Diferentes endpoints para lista de dispositivos
    device_endpoints = [
        {
            "url": "https://a1.tuyacn.com/v1.0/users/devices",
            "headers": {"Authorization": f"Bearer {token}"},
        },
        {
            "url": "https://a1.tuyaus.com/v1.0/users/devices",
            "headers": {"Authorization": f"Bearer {token}"},
        },
        {
            "url": "https://openapi.tuyacn.com/v1.0/users/devices",
            "headers": {"access_token": token},
        },
    ]

    for endpoint in device_endpoints:
        print(f"\n🔍 Testando: {endpoint['url']}")

        try:
            response = requests.get(
                endpoint["url"], headers=endpoint["headers"], timeout=15
            )
            print(f"   Status: {response.status_code}")
            print(f"   Resposta: {response.text}")

            if response.status_code == 200:
                result = response.json()

                if result.get("success"):
                    devices = result.get("result", [])
                    print(f"   ✅ {len(devices)} dispositivo(s) encontrado(s)!")

                    for device in devices:
                        print(f"\n   📱 Dispositivo:")
                        print(f"      Nome: {device.get('name', 'Unknown')}")
                        print(f"      ID: {device.get('id', 'Unknown')}")
                        print(f"      Local Key: {device.get('localKey', 'N/A')}")

                        if device.get("id") == "eb0254d3ac39b4d2740fwq":
                            local_key = device.get("localKey")
                            if local_key:
                                print(f"      🎯 LOCAL KEY ENCONTRADA: {local_key}")
                                return local_key

        except Exception as e:
            print(f"   ❌ Erro: {e}")

    return None


def main():
    """Função principal"""
    print("🎯 LOGIN TUYA - ENDPOINTS MODERNOS")
    print("=" * 60)

    # Carregar credenciais
    username, password = load_credentials()

    if not username or not password:
        print("❌ Credenciais não encontradas no .env")
        return

    print(f"✅ Credenciais carregadas: {username}")

    # Tentar login moderno
    login_info = try_modern_login(username, password)

    if not login_info:
        login_info = try_tuya_cloud_login(username, password)

    if login_info:
        print(f"\n🎉 LOGIN BEM-SUCEDIDO!")

        # Tentar listar dispositivos
        local_key = try_device_list_with_token(login_info)

        if local_key:
            print(f"\n🎉 SUCESSO COMPLETO!")
            print(f"✅ Local Key: {local_key}")
            print(f"\n📋 Configure no .env:")
            print(f"TUYA_LOCAL_KEY={local_key}")
            print(f"\n📋 Execute:")
            print(f"   python scripts/monitor_energy.py")
        else:
            print(f"\n⏳ Dispositivos não encontrados")
    else:
        print(f"\n❌ Nenhum método de login funcionou")
        print(f"💡 Alternativa: Acesse https://iot.tuya.com/ manualmente")


if __name__ == "__main__":
    main()
