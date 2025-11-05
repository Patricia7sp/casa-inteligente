#!/usr/bin/env python3
"""
Acessar API Tuya com login e senha (versão automática)
"""

import os
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


def try_web_login(username, password):
    """Tentar login via web interface"""
    print(f"\n🌐 TENTANDO LOGIN WEB")
    print("=" * 50)
    
    # Endpoints web
    web_endpoints = [
        "https://passport.tuya.com/iot/login",
        "https://auth.tuya.com/api/login",
        "https://iot.tuya.com/api/login"
    ]
    
    for endpoint in web_endpoints:
        print(f"🔍 Testando: {endpoint}")
        
        web_data = {
            "username": username,
            "password": password,
            "countryCode": "55",
            "validateCode": "",
            "validateType": ""
        }
        
        try:
            response = requests.post(endpoint, json=web_data, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Resposta: {result}")
                
                if result.get("success") or result.get("code") == 200:
                    print(f"   ✅ Login web bem-sucedido!")
                    return result
        
        except Exception as e:
            print(f"   Erro: {e}")
    
    return None


def try_tuya_iot_login(username, password):
    """Tentar login direto na Tuya IoT Platform"""
    print(f"\n🏭 TENTANDO LOGIN TUYA IOT")
    print("=" * 50)
    
    # Endpoint da Tuya IoT Platform
    iot_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post("https://iot.tuya.com/api/v1/auth/login", json=iot_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Resposta: {result}")
            
            if result.get("success"):
                print(f"✅ Login IoT bem-sucedido!")
                return result
    
    except Exception as e:
        print(f"Erro: {e}")
    
    return None


def get_credentials_from_env():
    """Obter credenciais do ambiente"""
    print("🔐 OBTENDO CREDENCIAIS DO AMBIENTE")
    print("=" * 50)
    
    username = os.getenv('TUYA_USERNAME')
    password = os.getenv('TUYA_PASSWORD')
    
    if not username or not password:
        print("❌ Credenciais não encontradas no ambiente")
        print("💡 Configure:")
        print("   export TUYA_USERNAME=seu_email")
        print("   export TUYA_PASSWORD=sua_senha")
        return None, None
    
    print(f"✅ Credenciais encontradas:")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)}")
    
    return username, password


def create_config_with_local_key(local_key):
    """Criar configuração com Local Key encontrada"""
    print(f"\n📝 CRIANDO CONFIGURAÇÃO FINAL")
    print("=" * 50)
    
    config = {
        "tuya_local": {
            "device_id": "eb0254d3ac39b4d2740fwq",
            "ip_address": "192.168.68.100",
            "local_key": local_key,
            "version": "3.4"
        }
    }
    
    # Salvar arquivo
    with open('tuya_config_found.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuração salva: tuya_config_found.json")
    
    # Mostrar .env
    print(f"\n📋 Configure no .env:")
    print(f"TUYA_DEVICE_ID=eb0254d3ac39b4d2740fwq")
    print(f"TUYA_IP_ADDRESS=192.168.68.100")
    print(f"TUYA_LOCAL_KEY={local_key}")
    print(f"TUYA_VERSION=3.4")
    
    print(f"\n📋 Execute monitoramento:")
    print(f"   python scripts/monitor_energy.py")


def main():
    """Função principal"""
    print("🎯 ACESSO TUYA COM LOGIN E SENHA")
    print("=" * 60)
    print("Testando múltiplos métodos de login...")
    print()
    
    # Obter credenciais
    username, password = get_credentials_from_env()
    
    if not username or not password:
        print("\n❌ Configure as credenciais no ambiente:")
        print("export TUYA_USERNAME=seu_email")
        print("export TUYA_PASSWORD=sua_senha")
        print("\nDepois execute novamente:")
        print("python scripts/tuya_login_auto.py")
        return
    
    # Método 1: Login via API do app
    print("\n" + "="*60)
    print("MÉTODO 1: API DO APP TUYA")
    print("="*60)
    
    login_info = login_tuya_account(username, password)
    
    if login_info:
        print(f"\n🎉 LOGIN BEM-SUCEDIDO!")
        
        # Tentar obter dispositivos
        local_key = get_devices_with_token(login_info)
        
        if local_key:
            create_config_with_local_key(local_key)
            return
    
    # Método 2: Login via web
    print("\n" + "="*60)
    print("MÉTODO 2: LOGIN WEB")
    print("="*60)
    
    web_result = try_web_login(username, password)
    
    if web_result:
        print(f"✅ Login web funcionou!")
        # Aqui poderíamos extrair token e continuar
    
    # Método 3: Login Tuya IoT
    print("\n" + "="*60)
    print("MÉTODO 3: TUYA IOT PLATFORM")
    print("="*60)
    
    iot_result = try_tuya_iot_login(username, password)
    
    if iot_result:
        print(f"✅ Login IoT funcionou!")
        # Aqui poderíamos extrair token e continuar
    
    print(f"\n❌ Nenhum método de login funcionou")
    print(f"💡 Sugestões:")
    print(f"   1. Verifique usuário e senha")
    print(f"   2. Confirme que usa a conta Tuya correta")
    print(f"   3. Tente acessar https://iot.tuya.com/ manualmente")
    print(f"   4. Use método manual: GUIA_API_LOCAL_TUYA.md")


if __name__ == "__main__":
    main()
