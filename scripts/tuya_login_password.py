#!/usr/bin/env python3
"""
Acessar API Tuya com login e senha (como TAPO)
"""

import requests
import json
import hashlib
import time
import hmac
import sys
from pathlib import Path


def login_tuya_account(username, password):
    """Fazer login na conta Tuya"""
    print("🔐 FAZENDO LOGIN NA CONTA TUYA")
    print("=" * 50)

    # Endpoints de login do Tuya
    login_endpoints = [
        "https://a1.tuyacn.com/api.json",
        "https://a1.tuyaeu.com/api.json",
        "https://a1.tuyaus.com/api.json",
        "https://a1.tuyacz.com/api.json",
    ]

    # Payload de login baseado no app Tuya
    login_data = {
        "a": "tuya.m.user.login",
        "t": str(int(time.time())),
        "postData": json.dumps(
            {
                "userName": username,
                "password": password,
                "countryCode": "55",
                "bizType": "SMART_HOME",
                "appType": "SMART_TUYA_APP",
            }
        ),
        "v": "1.0",
        "appVersion": "3.26.0",
        "osSystem": "iOS",
        "osVersion": "15.0",
    }

    print(f"📧 Username: {username}")
    print(f"🌐 Tentando endpoints de login...")

    for endpoint in login_endpoints:
        print(f"\n🔍 Testando: {endpoint}")

        try:
            response = requests.post(endpoint, data=login_data, timeout=15)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"   Resposta: {result}")

                if result.get("success"):
                    print(f"   ✅ LOGIN BEM-SUCEDIDO!")

                    # Extrair token e informações
                    login_result = result.get("result", {})
                    access_token = login_result.get("access_token")
                    refresh_token = login_result.get("refresh_token")
                    user_id = login_result.get("uid")
                    expire_time = login_result.get("expire_time")

                    print(
                        f"   📋 Access Token: {access_token[:20] if access_token else 'None'}..."
                    )
                    print(f"   📋 User ID: {user_id}")
                    print(f"   📋 Expire em: {expire_time}s")

                    if access_token:
                        return {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "user_id": user_id,
                            "endpoint": endpoint,
                            "expire_time": expire_time,
                        }
                else:
                    print(f"   ❌ Erro: {result.get('errorMsg', 'Unknown')}")
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")

        except Exception as e:
            print(f"   ❌ Erro: {e}")

    return None


def get_devices_with_token(login_info):
    """Obter dispositivos usando token de login"""
    print(f"\n📱 OBTENDO DISPOSITIVOS COM TOKEN")
    print("=" * 50)

    access_token = login_info["access_token"]
    endpoint = login_info["endpoint"]

    # Payload para listar dispositivos
    devices_data = {
        "a": "tuya.m.device.list",
        "t": str(int(time.time())),
        "postData": json.dumps(
            {"homeId": "", "pageSize": 50, "pageNo": 1}  # Vazio para todas as casas
        ),
        "v": "1.0",
        "appVersion": "3.26.0",
        "osSystem": "iOS",
        "osVersion": "15.0",
        "access_token": access_token,
    }

    try:
        response = requests.post(endpoint, data=devices_data, timeout=15)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Resposta: {result}")

            if result.get("success"):
                devices = result.get("result", [])
                print(f"✅ {len(devices)} dispositivo(s) encontrado(s)!")

                for device in devices:
                    print(f"\n📱 Dispositivo:")
                    print(f"   Nome: {device.get('name', 'Unknown')}")
                    print(f"   ID: {device.get('id', 'Unknown')}")
                    print(f"   IP: {device.get('ip', 'Unknown')}")
                    print(f"   Local Key: {device.get('localKey', 'NÃO DISPONÍVEL')}")
                    print(f"   Online: {device.get('online', False)}")
                    print(f"   Produto: {device.get('productId', 'Unknown')}")

                    # Se encontrar nosso dispositivo
                    if device.get("id") == "eb0254d3ac39b4d2740fwq":
                        print(f"🎯 DISPOSITIVO ALVO ENCONTRADO!")
                        local_key = device.get("localKey")
                        if local_key:
                            print(f"🔑 LOCAL KEY: {local_key}")
                            return local_key

                return None
            else:
                print(f"❌ Erro: {result.get('errorMsg', 'Unknown')}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")

    except Exception as e:
        print(f"❌ Erro: {e}")

    return None


def try_alternative_login(username, password):
    """Tentar métodos alternativos de login"""
    print(f"\n🔄 MÉTODOS ALTERNATIVOS DE LOGIN")
    print("=" * 50)

    # Método 2: API Web do Tuya
    print("1️⃣ Tentando API Web...")

    web_login_data = {
        "username": username,
        "password": password,
        "countryCode": "55",
        "validateCode": "",
        "validateType": "",
    }

    web_endpoints = [
        "https://passport.tuya.com/iot/login",
        "https://auth.tuya.com/api/login",
        "https://iot.tuya.com/api/login",
    ]

    for endpoint in web_endpoints:
        print(f"   Testando: {endpoint}")
        try:
            response = requests.post(endpoint, json=web_login_data, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Resposta: {result}")
        except Exception as e:
            print(f"   Erro: {e}")

    # Método 3: API Mobile (diferente formato)
    print(f"\n2️⃣ Tentando API Mobile...")

    mobile_data = {
        "account": username,
        "passwd": hashlib.md5(password.encode()).hexdigest(),
        "countryCode": "55",
    }

    try:
        response = requests.post(
            "https://mobile.tuyacn.com/passport/login", json=mobile_data, timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Resposta: {result}")
    except Exception as e:
        print(f"   Erro: {e}")


def get_credentials_from_user():
    """Obter credenciais do usuário"""
    print("🔐 INSIRA SUAS CREDENCIAIS TUYA")
    print("=" * 50)

    username = input("📧 Email/Username: ").strip()
    password = input("🔑 Password: ").strip()

    if not username or not password:
        print("❌ Credenciais inválidas")
        return None, None

    return username, password


def main():
    """Função principal"""
    print("🎯 ACESSO TUYA COM LOGIN E SENHA")
    print("=" * 60)
    print("Similar ao método usado com TAPO")
    print()

    # Obter credenciais
    username, password = get_credentials_from_user()

    if not username or not password:
        return

    # Tentar login
    login_info = login_tuya_account(username, password)

    if login_info:
        print(f"\n🎉 LOGIN BEM-SUCEDIDO!")

        # Tentar obter dispositivos
        local_key = get_devices_with_token(login_info)

        if local_key:
            print(f"\n🎉 SUCESSO COMPLETO!")
            print(f"✅ Local Key obtida: {local_key}")
            print(f"\n📋 Configure no .env:")
            print(f"TUYA_DEVICE_ID=eb0254d3ac39b4d2740fwq")
            print(f"TUYA_IP_ADDRESS=192.168.68.100")
            print(f"TUYA_LOCAL_KEY={local_key}")
            print(f"\n📋 Execute:")
            print(f"   python scripts/monitor_energy.py")
        else:
            print(f"\n⏳ Local Key não encontrada nos dispositivos")
            print(f"💡 Verifique se o dispositivo está vinculado à sua conta")
    else:
        print(f"\n❌ Falha no login")

        # Tentar métodos alternativos
        try_alternative_login(username, password)

        print(f"\n📋 Sugestões:")
        print(f"   1. Verifique usuário e senha")
        print(f"   2. Confirme que usa a conta Tuya correta")
        print(f"   3. Tente acessar https://iot.tuya.com/ manualmente")


if __name__ == "__main__":
    main()
