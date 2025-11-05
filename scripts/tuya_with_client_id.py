#!/usr/bin/env python3
"""
Usar Client ID e User Account do app Tuya para obter Local Key
"""

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
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except:
        pass
    
    username = env_vars.get('TUYA_USERNAME') or env_vars.get('username')
    password = env_vars.get('TUYA_PASSWORD') or env_vars.get('password')
    
    return username, password


def try_app_api_with_client_id(username, password, client_id, user_account):
    """Tentar API usando Client ID do app"""
    print("📱 USANDO CLIENT ID DO APP TUYA")
    print("=" * 50)
    
    print(f"📋 Informações do app:")
    print(f"   Client ID: {client_id}")
    print(f"   User Account: {user_account}")
    print(f"   Username: {username}")
    
    # Endpoints da API mobile com Client ID
    mobile_endpoints = [
        "https://a1.tuyacn.com/api.json",
        "https://a1.tuyaeu.com/api.json", 
        "https://a1.tuyaus.com/api.json"
    ]
    
    # Payload de login com Client ID
    timestamp = str(int(time.time()))
    
    login_data = {
        "a": "tuya.m.user.login",
        "t": timestamp,
        "v": "1.0",
        "clientId": client_id,
        "postData": json.dumps({
            "userName": username,
            "password": password,
            "countryCode": "55",
            "bizType": "SMART_HOME",
            "appType": "SMART_TUYA_APP"
        })
    }
    
    for endpoint in mobile_endpoints:
        print(f"\n🔍 Testando: {endpoint}")
        
        try:
            response = requests.post(endpoint, data=login_data, timeout=15)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Resposta: {result}")
                
                if result.get("success"):
                    print(f"   ✅ LOGIN BEM-SUCEDIDO!")
                    
                    login_result = result.get("result", {})
                    access_token = login_result.get("access_token")
                    
                    if access_token:
                        print(f"   📋 Token: {access_token[:20]}...")
                        return {
                            'access_token': access_token,
                            'endpoint': endpoint,
                            'client_id': client_id
                        }
                else:
                    print(f"   ❌ Erro: {result.get('errorMsg', 'Unknown')}")
        
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    return None


def try_get_devices_with_user_account(login_info, user_account):
    """Obter dispositivos usando User Account"""
    print(f"\n📱 OBTENDO DISPOSITIVOS COM USER ACCOUNT")
    print("=" * 50)
    
    access_token = login_info['access_token']
    endpoint = login_info['endpoint']
    client_id = login_info['client_id']
    
    # Payload para listar dispositivos com User Account
    devices_data = {
        "a": "tuya.m.device.list",
        "t": str(int(time.time())),
        "v": "1.0",
        "clientId": client_id,
        "access_token": access_token,
        "postData": json.dumps({
            "uid": user_account,
            "homeId": "",
            "pageSize": 50,
            "pageNo": 1
        })
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
                    
                    # Se encontrar nosso dispositivo
                    if device.get('id') == 'eb0254d3ac39b4d2740fwq':
                        print(f"🎯 DISPOSITIVO ALVO ENCONTRADO!")
                        local_key = device.get('localKey')
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


def try_alternative_device_endpoints(login_info, user_account):
    """Tentar endpoints alternativos para dispositivos"""
    print(f"\n🔄 TENTANDO ENDPOINTS ALTERNATIVOS")
    print("=" * 50)
    
    access_token = login_info['access_token']
    endpoint = login_info['endpoint']
    client_id = login_info['client_id']
    
    # Diferentes APIs para dispositivos
    device_apis = [
        {
            "a": "tuya.m.my.group.device.list",
            "postData": {"uid": user_account}
        },
        {
            "a": "tuya.m.device.info.get",
            "postData": {"devId": "eb0254d3ac39b4d2740fwq"}
        },
        {
            "a": "tuya.m.device.detail.get",
            "postData": {"devId": "eb0254d3ac39b4d2740fwq"}
        },
        {
            "a": "tuya.m.location.list",
            "postData": {"uid": user_account}
        }
    ]
    
    for api in device_apis:
        print(f"\n🔍 Testando API: {api['a']}")
        
        request_data = {
            "a": api['a'],
            "t": str(int(time.time())),
            "v": "1.0",
            "clientId": client_id,
            "access_token": access_token,
            "postData": json.dumps(api['postData'])
        }
        
        try:
            response = requests.post(endpoint, data=request_data, timeout=15)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Resposta: {result}")
                
                if result.get("success"):
                    print(f"   ✅ API funcionou!")
                    
                    # Procurar Local Key na resposta
                    result_data = result.get("result", {})
                    
                    # Verificar se tem localKey diretamente
                    if result_data.get('localKey'):
                        local_key = result_data.get('localKey')
                        print(f"   🔑 LOCAL KEY ENCONTRADA: {local_key}")
                        return local_key
                    
                    # Verificar se tem lista de dispositivos
                    if isinstance(result_data, list):
                        for device in result_data:
                            if device.get('id') == 'eb0254d3ac39b4d2740fwq':
                                local_key = device.get('localKey')
                                if local_key:
                                    print(f"   🔑 LOCAL KEY ENCONTRADA: {local_key}")
                                    return local_key
                else:
                    print(f"   ❌ Erro: {result.get('errorMsg', 'Unknown')}")
        
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    return None


def main():
    """Função principal"""
    print("🎯 ACESSO TUYA COM CLIENT ID DO APP")
    print("=" * 60)
    
    # Informações do app
    client_id = "nfdmss3jjw4jtydrnmhn"
    user_account = "aa-107243654274021126469"
    
    # Carregar credenciais
    username, password = load_credentials()
    
    if not username or not password:
        print("❌ Credenciais não encontradas no .env")
        return
    
    print(f"✅ Credenciais carregadas")
    
    # Tentar login com Client ID
    login_info = try_app_api_with_client_id(username, password, client_id, user_account)
    
    if login_info:
        print(f"\n🎉 LOGIN BEM-SUCEDIDO!")
        
        # Tentar obter dispositivos
        local_key = try_get_devices_with_user_account(login_info, user_account)
        
        if not local_key:
            # Tentar endpoints alternativos
            local_key = try_alternative_device_endpoints(login_info, user_account)
        
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
            print(f"\n⏳ Local Key não encontrada")
            print(f"💡 Dispositivo pode não estar vinculado a esta conta")
    else:
        print(f"\n❌ Login falhou")
        print(f"💡 Verifique as credenciais no .env")


if __name__ == "__main__":
    main()
