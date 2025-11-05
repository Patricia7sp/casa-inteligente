#!/usr/bin/env python3
"""
Ler credenciais do .env e fazer login Tuya automaticamente
"""

import os
import requests
import json
import hashlib
import time
import hmac
from pathlib import Path


def load_env_file():
    """Carregar variáveis do arquivo .env"""
    print("📁 CARREGANDO CONFIGURAÇÃO DO .ENV")
    print("=" * 50)
    
    env_path = Path(__file__).parent.parent / ".env"
    
    if not env_path.exists():
        print(f"❌ Arquivo .env não encontrado em: {env_path}")
        return {}
    
    print(f"✅ Arquivo .env encontrado: {env_path}")
    
    env_vars = {}
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        
        print(f"✅ {len(env_vars)} variáveis carregadas")
        
        # Mostrar variáveis relevantes (sem mostrar senhas)
        for key, value in env_vars.items():
            if 'password' in key.lower() or 'pass' in key.lower():
                print(f"   {key}: {'*' * len(value)}")
            else:
                print(f"   {key}: {value}")
    
    except Exception as e:
        print(f"❌ Erro ao ler .env: {e}")
        return {}
    
    return env_vars


def login_tuya_account(username, password):
    """Fazer login na conta Tuya"""
    print("\n🔐 FAZENDO LOGIN NA CONTA TUYA")
    print("=" * 50)
    
    # Endpoints de login do Tuya
    login_endpoints = [
        "https://a1.tuyacn.com/api.json",
        "https://a1.tuyaeu.com/api.json", 
        "https://a1.tuyaus.com/api.json",
        "https://a1.tuyacz.com/api.json"
    ]
    
    # Payload de login baseado no app Tuya
    login_data = {
        "a": "tuya.m.user.login",
        "t": str(int(time.time())),
        "postData": json.dumps({
            "userName": username,
            "password": password,
            "countryCode": "55",
            "bizType": "SMART_HOME",
            "appType": "SMART_TUYA_APP"
        }),
        "v": "1.0",
        "appVersion": "3.26.0",
        "osSystem": "iOS",
        "osVersion": "15.0"
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
                    
                    print(f"   📋 Access Token: {access_token[:20] if access_token else 'None'}...")
                    print(f"   📋 User ID: {user_id}")
                    print(f"   📋 Expire em: {expire_time}s")
                    
                    if access_token:
                        return {
                            'access_token': access_token,
                            'refresh_token': refresh_token,
                            'user_id': user_id,
                            'endpoint': endpoint,
                            'expire_time': expire_time
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
    
    access_token = login_info['access_token']
    endpoint = login_info['endpoint']
    
    # Payload para listar dispositivos
    devices_data = {
        "a": "tuya.m.device.list",
        "t": str(int(time.time())),
        "postData": json.dumps({
            "homeId": "",  # Vazio para todas as casas
            "pageSize": 50,
            "pageNo": 1
        }),
        "v": "1.0",
        "appVersion": "3.26.0",
        "osSystem": "iOS",
        "osVersion": "15.0",
        "access_token": access_token
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


def try_alternative_credentials(env_vars):
    """Tentar diferentes combinações de credenciais"""
    print(f"\n🔄 TENTANDO CREDENCIAIS ALTERNATIVAS")
    print("=" * 50)
    
    # Possíveis nomes de variáveis
    username_options = ['TUYA_USERNAME', 'TUYA_EMAIL', 'TUYA_USER', 'EMAIL', 'username']
    password_options = ['TUYA_PASSWORD', 'TUYA_PASS', 'PASSWORD', 'password']
    
    for user_opt in username_options:
        for pass_opt in password_options:
            username = env_vars.get(user_opt)
            password = env_vars.get(pass_opt)
            
            if username and password:
                print(f"\n🔍 Tentando: {user_opt} / {pass_opt}")
                login_info = login_tuya_account(username, password)
                
                if login_info:
                    local_key = get_devices_with_token(login_info)
                    if local_key:
                        return local_key
    
    return None


def main():
    """Função principal"""
    print("🎯 LOGIN TUYA AUTOMÁTICO COM .ENV")
    print("=" * 60)
    
    # Carregar .env
    env_vars = load_env_file()
    
    if not env_vars:
        print("❌ Não foi possível carregar .env")
        return
    
    # Tentar obter credenciais
    username = env_vars.get('TUYA_USERNAME') or env_vars.get('username')
    password = env_vars.get('TUYA_PASSWORD') or env_vars.get('password')
    
    if username and password:
        print(f"\n✅ Credenciais encontradas no .env")
        
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
                return
    
    # Tentar credenciais alternativas
    print(f"\n⏳ Tentando outras combinações de credenciais...")
    local_key = try_alternative_credentials(env_vars)
    
    if local_key:
        print(f"\n🎉 SUCESSO COMPLETO!")
        print(f"✅ Local Key obtida: {local_key}")
    else:
        print(f"\n❌ Nenhuma credencial funcionou")
        print(f"💡 Verifique se as credenciais estão no .env:")
        print(f"   TUYA_USERNAME=seu_email")
        print(f"   TUYA_PASSWORD=sua_senha")
        print(f"\nOu execute manualmente:")
        print(f"   python scripts/tuya_login_terminal.py")


if __name__ == "__main__":
    main()
