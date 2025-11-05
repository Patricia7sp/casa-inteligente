#!/usr/bin/env python3
"""
Usar MiniApp ID para obter Local Key
ID do MiniApp pode ser usado para acessar APIs diferentes
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


class MiniAppKeyExtractor:
    """Extrair Local Key usando MiniApp ID"""
    
    def __init__(self):
        # Credenciais
        self.username = os.getenv('SMARTLIFE_USERNAME', 'paty7sp@gmail.com')
        self.password = os.getenv('SMARTLIFE_PASSWORD', 'P@ty0740')
        self.client_id = os.getenv('TUYA_CLIENT_ID', 'nwykv3tnwx5na9kvyjvu')
        self.client_secret = os.getenv('TUYA_CLIENT_SECRET', '021747b14008401f9f173dc693113aef')
        self.device_id = os.getenv('TUYA_DEVICE_ID', 'eb0254d3ac39b4d2740fwq')
        
        # MiniApp ID (você precisa fornecer)
        self.miniapp_id = None
        
        # Endpoints MiniApp
        self.miniapp_endpoints = [
            "https://openapi.tuyaus.com",
            "https://a1.tuyaus.com",
            "https://a1.tuyacn.com"
        ]
    
    def get_miniapp_id(self):
        """Obter MiniApp ID do usuário"""
        print("🔍 OBTENDO MINIAPP ID")
        print("=" * 60)
        print("Você encontrou o ID do MiniApp no app SmartLife.")
        print("Preciso desse ID para continuar.")
        print()
        
        miniapp_id = input("Digite o MiniApp ID encontrado: ").strip()
        
        if miniapp_id:
            self.miniapp_id = miniapp_id
            print(f"✅ MiniApp ID definido: {miniapp_id}")
            return True
        else:
            print("❌ MiniApp ID não fornecido")
            return False
    
    def try_miniapp_apis(self):
        """Tentar APIs específicas do MiniApp"""
        print(f"\n🎯 TENTANDO APIS DO MINIAPP")
        print("=" * 60)
        print(f"MiniApp ID: {self.miniapp_id}")
        print()
        
        # Tentar diferentes endpoints MiniApp
        miniapp_paths = [
            f"/v1.0/miniapps/{self.miniapp_id}/devices",
            f"/v1.0/miniapps/{self.miniapp_id}/token",
            f"/v1.0/apps/{self.miniapp_id}/devices",
            f"/v1.0/apps/{self.miniapp_id}/auth",
            f"/v1.0/miniapp/{self.miniapp_id}/devices/{self.device_id}",
            f"/v1.0/app/{self.miniapp_id}/device/{self.device_id}"
        ]
        
        for base_url in self.miniapp_endpoints:
            print(f"\n🌐 Tentando: {base_url}")
            
            for path in miniapp_paths:
                if self._try_miniapp_endpoint(base_url, path):
                    return True
        
        return False
    
    def _try_miniapp_endpoint(self, base_url, path):
        """Tentar endpoint específico do MiniApp"""
        timestamp = str(int(time.time() * 1000))
        nonce = ""
        
        # Calcular assinatura
        string_to_sign = f"GET\n\n\n{path}"
        message = f"{self.client_id}{timestamp}{nonce}{string_to_sign}"
        sign = hmac.new(
            self.client_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()
        
        url = f"{base_url}{path}"
        
        headers = {
            'client_id': self.client_id,
            'sign': sign,
            'sign_method': 'HMAC-SHA256',
            't': timestamp,
            'nonce': nonce
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    result = data['result']
                    
                    print(f"   ✅ Sucesso em {path}")
                    
                    # Procurar Local Key
                    if isinstance(result, dict):
                        local_key = result.get('local_key')
                        if local_key:
                            print(f"   🎉 LOCAL KEY: {local_key}")
                            self._save_local_key(local_key)
                            return True
                        
                        # Procurar em dispositivos
                        devices = result.get('devices', [])
                        for device in devices:
                            if device.get('id') == self.device_id:
                                local_key = device.get('local_key')
                                if local_key:
                                    print(f"   🎉 LOCAL KEY encontrada: {local_key}")
                                    self._save_local_key(local_key)
                                    return True
                    
                    print(f"   📋 Dados: {json.dumps(result, indent=6)[:200]}...")
                    
                else:
                    print(f"   ❌ Erro {data.get('code')}: {data.get('msg')}")
            else:
                print(f"   ❌ HTTP {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ {str(e)[:50]}")
        
        return False
    
    def try_miniapp_auth(self):
        """Tentar autenticação via MiniApp"""
        print(f"\n🔐 TENTANDO AUTENTICAÇÃO MINIAPP")
        print("=" * 60)
        
        # Tentar obter token via MiniApp
        timestamp = str(int(time.time() * 1000))
        nonce = ""
        
        path = f"/v1.0/miniapps/{self.miniapp_id}/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "miniapp_id": self.miniapp_id
        }
        
        payload_str = json.dumps(payload, separators=(',', ':'))
        
        # Calcular assinatura
        string_to_sign = f"POST\n\n\n{path}\n{payload_str}"
        message = f"{self.client_id}{timestamp}{nonce}{string_to_sign}"
        sign = hmac.new(
            self.client_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()
        
        url = f"https://openapi.tuyaus.com{path}"
        
        headers = {
            'client_id': self.client_id,
            'sign': sign,
            'sign_method': 'HMAC-SHA256',
            't': timestamp,
            'nonce': nonce,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, data=payload_str)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    token = data['result'].get('access_token')
                    if token:
                        print(f"✅ Token MiniApp obtido!")
                        return self.use_miniapp_token(token)
                else:
                    print(f"❌ Erro: {data.get('msg')}")
        
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        return False
    
    def use_miniapp_token(self, token):
        """Usar token do MiniApp para obter dispositivos"""
        print(f"\n📱 USANDO TOKEN MINIAPP")
        print("=" * 60)
        
        timestamp = str(int(time.time() * 1000))
        nonce = ""
        
        path = f"/v1.0/miniapps/{self.miniapp_id}/devices"
        string_to_sign = f"GET\n\n\n{path}"
        
        message = f"{self.client_id}{timestamp}{nonce}{string_to_sign}"
        sign = hmac.new(
            self.client_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()
        
        url = f"https://openapi.tuyaus.com{path}"
        
        headers = {
            'client_id': self.client_id,
            'access_token': token,
            'sign': sign,
            'sign_method': 'HMAC-SHA256',
            't': timestamp,
            'nonce': nonce
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    devices = data['result']
                    
                    print(f"✅ Dispositivos MiniApp: {len(devices)}")
                    
                    for device in devices:
                        if device.get('id') == self.device_id:
                            local_key = device.get('local_key')
                            if local_key:
                                print(f"🎉 LOCAL KEY: {local_key}")
                                self._save_local_key(local_key)
                                return True
                
                print(f"❌ Erro: {data.get('msg')}")
        
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        return False
    
    def try_alternative_miniapp_methods(self):
        """Tentar métodos alternativos com MiniApp ID"""
        print(f"\n🔄 MÉTODOS ALTERNATIVOS COM MINIAPP ID")
        print("=" * 60)
        
        # Tentar diferentes abordagens
        methods = [
            ("Direct device query", f"/v1.0/miniapps/{self.miniapp_id}/devices/{self.device_id}"),
            ("App device list", f"/v1.0/apps/{self.miniapp_id}/devices"),
            ("MiniApp info", f"/v1.0/miniapps/{self.miniapp_id}"),
            ("Device via MiniApp", f"/v1.0/devices/{self.device_id}?miniapp_id={self.miniapp_id}")
        ]
        
        for method_name, path in methods:
            print(f"\n📡 {method_name}: {path}")
            
            if self._try_alternative_method(path):
                return True
        
        return False
    
    def _try_alternative_method(self, path):
        """Tentar método alternativo"""
        timestamp = str(int(time.time() * 1000))
        nonce = ""
        
        string_to_sign = f"GET\n\n\n{path}"
        message = f"{self.client_id}{timestamp}{nonce}{string_to_sign}"
        sign = hmac.new(
            self.client_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()
        
        url = f"https://openapi.tuyaus.com{path}"
        
        headers = {
            'client_id': self.client_id,
            'sign': sign,
            'sign_method': 'HMAC-SHA256',
            't': timestamp,
            'nonce': nonce
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    result = data['result']
                    
                    print(f"   ✅ Sucesso!")
                    
                    # Procurar Local Key
                    if isinstance(result, dict):
                        local_key = result.get('local_key')
                        if local_key:
                            print(f"   🎉 LOCAL KEY: {local_key}")
                            self._save_local_key(local_key)
                            return True
                        
                        # Verificar se é o nosso dispositivo
                        if result.get('id') == self.device_id:
                            local_key = result.get('local_key')
                            if local_key:
                                print(f"   🎉 LOCAL KEY: {local_key}")
                                self._save_local_key(local_key)
                                return True
                    
                    print(f"   📋 Resultado: {json.dumps(result, indent=6)[:200]}...")
                
                else:
                    print(f"   ❌ Erro {data.get('code')}: {data.get('msg')}")
        
        except Exception as e:
            print(f"   ❌ {str(e)[:50]}")
        
        return False
    
    def _save_local_key(self, local_key):
        """Salvar Local Key no .env"""
        print(f"\n💾 Salvando Local Key no .env...")
        
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('TUYA_LOCAL_KEY='):
                lines[i] = f'TUYA_LOCAL_KEY={local_key}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'\nTUYA_LOCAL_KEY={local_key}\n')
        
        with open('.env', 'w') as f:
            f.writelines(lines)
        
        print(f"✅ Local Key salva no .env!")
    
    def run_miniapp_extraction(self):
        """Executar extração usando MiniApp ID"""
        print("🎯 EXTRAÇÃO DE LOCAL KEY VIA MINIAPP ID")
        print("=" * 60)
        
        # 1. Obter MiniApp ID
        if not self.get_miniapp_id():
            return None
        
        # 2. Tentar APIs MiniApp
        if self.try_miniapp_apis():
            return True
        
        # 3. Tentar autenticação MiniApp
        if self.try_miniapp_auth():
            return True
        
        # 4. Tentar métodos alternativos
        if self.try_alternative_miniapp_methods():
            return True
        
        return None


def main():
    """Função principal"""
    print("🎯 USANDO MINIAPP ID PARA OBTER LOCAL KEY")
    print("=" * 60)
    print("MiniApp ID pode ser a chave para acessar APIs diferentes!")
    print()
    
    extractor = MiniAppKeyExtractor()
    result = extractor.run_miniapp_extraction()
    
    print("\n" + "=" * 60)
    
    if result:
        print("🎉 SUCESSO! LOCAL KEY OBTIDA VIA MINIAPP!")
        print("=" * 60)
        print("✅ Execute: python scripts/test_manual_local_key.py")
        print("✅ Execute: python scripts/monitor_novadigital_final.py")
    else:
        print("❌ MINIAPP ID NÃO LIBEROU LOCAL KEY")
        print("=" * 60)
        print()
        print("💡 POSSÍVEIS RAZÕES:")
        print("   1. MiniApp ID incorreto")
        print("   2. API não disponível para este MiniApp")
        print("   3. Precisa de permissões adicionais")
        print()
        print("🎯 OPÇÕES FINAIS:")
        print("   1. Verificar se há outro ID no app")
        print("   2. Resetar tomada (SOLUCAO_FINAL_RESETAR.md)")
        print("   3. Comprar TAPO P110 (R$ 100)")


if __name__ == "__main__":
    main()
