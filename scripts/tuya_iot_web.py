#!/usr/bin/env python3
"""
Acessar Tuya IoT Platform via web scraping
"""

import requests
from bs4 import BeautifulSoup
import json
import time
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


def try_iot_platform_login(username, password):
    """Tentar login na Tuya IoT Platform"""
    print("🏭 TENTANDO TUYA IOT PLATFORM")
    print("=" * 50)

    # URLs da IoT Platform
    iot_urls = [
        "https://iot.tuya.com/",
        "https://iot.tuya.com/login",
        "https://platform.tuya.com/",
        "https://platform.tuya.com/login",
    ]

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    )

    for url in iot_urls:
        print(f"\n🔍 Testando: {url}")

        try:
            # Obter página de login
            response = session.get(url, timeout=15)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # Procurar formulário de login
                login_form = soup.find("form")
                if login_form:
                    print(f"   ✅ Formulário de login encontrado!")

                    # Extrair campos do formulário
                    inputs = login_form.find_all("input")
                    form_data = {}

                    for inp in inputs:
                        name = inp.get("name")
                        value = inp.get("value", "")
                        if name:
                            if "username" in name.lower() or "email" in name.lower():
                                form_data[name] = username
                            elif "password" in name.lower():
                                form_data[name] = password
                            else:
                                form_data[name] = value

                    print(f"   📋 Campos do formulário: {list(form_data.keys())}")

                    # Enviar formulário
                    login_url = (
                        url
                        if login_form.get("action") in ["#", "", None]
                        else login_form.get("action")
                    )

                    if not login_url.startswith("http"):
                        login_url = url.rstrip("/") + "/" + login_url.lstrip("/")

                    print(f"   🔗 Enviando para: {login_url}")

                    login_response = session.post(login_url, data=form_data, timeout=15)
                    print(f"   Status: {login_response.status_code}")

                    # Verificar se login funcionou
                    if (
                        "dashboard" in login_response.url.lower()
                        or "home" in login_response.url.lower()
                    ):
                        print(f"   ✅ LOGIN BEM-SUCEDIDO!")
                        print(f"   🌐 Redirecionado para: {login_response.url}")

                        # Tentar acessar página de dispositivos
                        return try_get_devices_from_iot(session, login_response.url)
                    else:
                        print(f"   ❌ Login falhou")
                        print(f"   🌐 URL final: {login_response.url}")
                else:
                    print(f"   ❌ Formulário de login não encontrado")
                    print(f"   💡 Pode ser SPA (React/Vue)")

        except Exception as e:
            print(f"   ❌ Erro: {e}")

    return None


def try_get_devices_from_iot(session, base_url):
    """Tentar obter dispositivos da IoT Platform"""
    print(f"\n📱 TENTANDO OBTER DISPOSITIVOS DA IOT")
    print("=" * 50)

    # URLs de dispositivos na IoT Platform
    device_urls = [
        f"{base_url}/devices",
        f"{base_url}/device",
        f"{base_url}/device/list",
        f"{base_url}/api/devices",
        "https://iot.tuya.com/devices",
        "https://iot.tuya.com/device/list",
    ]

    for url in device_urls:
        print(f"\n🔍 Testando: {url}")

        try:
            response = session.get(url, timeout=15)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                # Procurar por dados JSON na página
                try:
                    # Tentar parsear como JSON
                    data = response.json()
                    print(f"   📋 Resposta JSON: {data}")

                    if "devices" in data or "result" in data:
                        devices = data.get("devices", data.get("result", []))
                        print(f"   ✅ {len(devices)} dispositivo(s) encontrado(s)!")

                        for device in devices:
                            if device.get("id") == "eb0254d3ac39b4d2740fwq":
                                local_key = device.get("localKey") or device.get(
                                    "local_key"
                                )
                                if local_key:
                                    print(f"   🎯 LOCAL KEY: {local_key}")
                                    return local_key

                except:
                    # Se não for JSON, procurar no HTML
                    soup = BeautifulSoup(response.text, "html.parser")

                    # Procurar por scripts com dados
                    scripts = soup.find_all("script")
                    for script in scripts:
                        if script.string and "devices" in script.string:
                            print(f"   📋 Script com dispositivos encontrado!")
                            # Tentar extrair JSON do script
                            try:
                                # Procurar por JSON no script
                                start = script.string.find("[")
                                end = script.string.rfind("]") + 1
                                if start != -1 and end != -1:
                                    json_str = script.string[start:end]
                                    devices = json.loads(json_str)

                                    for device in devices:
                                        if device.get("id") == "eb0254d3ac39b4d2740fwq":
                                            local_key = device.get(
                                                "localKey"
                                            ) or device.get("local_key")
                                            if local_key:
                                                print(f"   🎯 LOCAL KEY: {local_key}")
                                                return local_key
                            except:
                                pass

                print(f"   ❌ Dispositivos não encontrados nesta página")

        except Exception as e:
            print(f"   ❌ Erro: {e}")

    return None


def try_api_direct():
    """Tentar API direta com as credenciais Cloud que já temos"""
    print(f"\n🌐 TENTANDO API DIRETA COM CREDENCIAIS CLOUD")
    print("=" * 50)

    # Usar as credenciais Cloud que já estão no .env
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

    access_id = env_vars.get("TUYA_ACCESS_ID")
    access_key = env_vars.get("TUYA_ACCESS_KEY")
    region = env_vars.get("TUYA_REGION", "us")

    if access_id and access_key:
        print(f"✅ Credenciais Cloud encontradas:")
        print(f"   Access ID: {access_id}")
        print(f"   Region: {region}")

        # Tentar obter token com diferentes timestamps
        import hashlib
        import hmac

        base_url = f"https://openapi.tuya{region}.com"

        for offset in [0, 5000, -5000, 10000, -10000, 30000]:
            timestamp = str(int(time.time() * 1000) + offset)

            try:
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

                response = requests.get(
                    f"{base_url}{path}", headers=headers, timeout=10
                )
                result = response.json()

                if result.get("success"):
                    print(f"   ✅ Token obtido com offset {offset}ms!")
                    return result["result"]["access_token"]
                else:
                    print(f"   Offset {offset}ms: {result.get('msg')}")

            except Exception as e:
                print(f"   Erro offset {offset}ms: {e}")

    return None


def main():
    """Função principal"""
    print("🎯 TUYA IOT PLATFORM - WEB SCRAPING")
    print("=" * 60)

    # Carregar credenciais
    username, password = load_credentials()

    if not username or not password:
        print("❌ Credenciais não encontradas no .env")
        return

    print(f"✅ Credenciais: {username}")

    # Tentar login na IoT Platform
    local_key = try_iot_platform_login(username, password)

    if not local_key:
        print(f"\n⏳ Web scraping não funcionou")

        # Tentar API direta
        print(f"\n🔄 Tentando API direta...")
        token = try_api_direct()

        if token:
            print(f"✅ Token obtido: {token[:20]}...")
            print(f"💡 Agora podemos usar este token para obter dispositivos")
        else:
            print(f"❌ API também não funcionou")

    if local_key:
        print(f"\n🎉 SUCESSO!")
        print(f"✅ Local Key: {local_key}")
        print(f"\n📋 Configure no .env:")
        print(f"TUYA_LOCAL_KEY={local_key}")
        print(f"\n📋 Execute:")
        print(f"   python scripts/monitor_energy.py")
    else:
        print(f"\n💡 ÚLTIMA ALTERNATIVA:")
        print(f"   1. Acesse manualmente: https://iot.tuya.com/")
        print(f"   2. Login: {username}")
        print(f"   3. Devices > seu dispositivo > Device Details")
        print(f"   4. Copie Local Key")


if __name__ == "__main__":
    main()
