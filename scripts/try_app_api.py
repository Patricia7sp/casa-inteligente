#!/usr/bin/env python3
"""
Alternativa à Local Key: Usar API do App Tuya Smart
"""

import requests
import json
import hashlib
import time
import hmac
import sys
from pathlib import Path


def test_tuya_app_api():
    """Testar API do App Tuya Smart"""
    print("📱 TESTANDO API DO APP TUYA SMART")
    print("=" * 50)
    
    print("🔄 MÉTODOS ALTERNATIVOS À LOCAL KEY:")
    print()
    
    print("1️⃣ INTERCEPTAR COMUNICAÇÃO DO APP:")
    print("   - Usar Wireshark para capturar tráfego")
    print("   - Configurar dispositivo no app")
    print("   - Extrair token e endpoints")
    print()
    
    print("2️⃣ REVERSE ENGINEERING DO APP:")
    print("   - Decompilar APK Android")
    print("   - Encontrar endpoints de API")
    print("   - Usar credenciais do app")
    print()
    
    print("3️⃣ TUYA OPEN API (sem Cloud):")
    print("   - API pública do Tuya")
    print("   - Requer registro de app")
    print("   - Limitada mas funcional")
    print()
    
    print("4️⃣ WEB SCRAPING DO PAINEL:")
    print("   - Acessar painel web Tuya")
    print("   - Extrair dados via HTML")
    print("   - Simular navegador")


def try_tuya_open_api():
    """Tentar Tuya Open API sem Cloud"""
    print("\n🌐 TESTANDO TUYA OPEN API")
    print("=" * 50)
    
    # Endpoints da Open API que não precisam de projeto Cloud
    endpoints = [
        "https://openapi.tuyaus.com/v1.0/open-apis/query-api-logs",
        "https://openapi.tuyaus.com/v1.0/token?grant_type=1",
        "https://openapi.tuyaus.com/v1.0/apps/schema"
    ]
    
    # Tentar com credenciais genéricas
    print("🔍 Tentando endpoints públicos...")
    
    for endpoint in endpoints:
        print(f"\n   Testando: {endpoint}")
        try:
            response = requests.get(endpoint, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Resposta: {result}")
            else:
                print(f"   Erro: {response.text}")
                
        except Exception as e:
            print(f"   Erro: {e}")


def try_app_credentials():
    """Tentar usar credenciais do app"""
    print("\n🔑 TESTANDO CREDENCIAIS DO APP")
    print("=" * 50)
    
    print("Se você tem login do app Tuya Smart:")
    print()
    
    # Tentar API de login do app
    login_endpoints = [
        "https://a1.tuyacn.com/api.json",
        "https://a1.tuyaeu.com/api.json", 
        "https://a1.tuyaus.com/api.json"
    ]
    
    for endpoint in login_endpoints:
        print(f"\n🔍 Testando login em: {endpoint}")
        
        # Payload de login do app
        login_data = {
            "a": "tuya.m.user.login",
            "t": str(int(time.time())),
            "postData": json.dumps({
                "userName": "seu_email@exemplo.com",
                "password": "sua_senha",
                "countryCode": "55"
            })
        }
        
        try:
            response = requests.post(endpoint, data=login_data, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"   ✅ Login bem-sucedido!")
                    print(f"   📋 Token: {result.get('result', {}).get('access_token', 'N/A')}")
                    return True
                else:
                    print(f"   ❌ Erro: {result.get('errorMsg', 'Unknown')}")
            else:
                print(f"   Erro HTTP: {response.text}")
                
        except Exception as e:
            print(f"   Erro: {e}")
    
    return False


def try_mobile_api():
    """Tentar API mobile do Tuya"""
    print("\n📱 TESTANDO API MOBILE TUYA")
    print("=" * 50)
    
    # Endpoints da API mobile
    mobile_endpoints = [
        "https://mobile.tuyacn.com/api.json",
        "https://mobile.tuyaeu.com/api.json",
        "https://mobile.tuyaus.com/api.json"
    ]
    
    for endpoint in mobile_endpoints:
        print(f"\n🔍 Testando API mobile: {endpoint}")
        
        # Tentar obter lista de dispositivos
        device_data = {
            "a": "tuya.m.device.list",
            "t": str(int(time.time())),
            "postData": "{}"
        }
        
        try:
            response = requests.post(endpoint, data=device_data, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Resposta: {result}")
                
                if result.get("success"):
                    devices = result.get("result", [])
                    print(f"   ✅ {len(devices)} dispositivo(s) encontrado(s)")
                    return True
            else:
                print(f"   Erro: {response.text}")
                
        except Exception as e:
            print(f"   Erro: {e}")
    
    return False


def create_intercept_guide():
    """Criar guia para interceptação"""
    print("\n📡 GUIA DE INTERCEPTAÇÃO")
    print("=" * 50)
    
    print("🔧 MÉTODO WIRESHARK (Mais confiável):")
    print()
    print("1️⃣ INSTALAR WIRESHARK:")
    print("   - macOS: brew install wireshark")
    print("   - Windows: baixar de wireshark.org")
    print()
    print("2️⃣ CONFIGURAR CAPTURA:")
    print("   - Iniciar Wireshark")
    print("   - Selecionar interface de rede (WiFi)")
    print("   - Aplicar filtro: http.host contains \"tuya\"")
    print()
    print("3️⃣ CAPTURAR TRÁFEGO:")
    print("   - Iniciar captura")
    print("   - Abrir app Tuya Smart")
    print("   - Configurar/usar dispositivo")
    print("   - Parar captura")
    print()
    print("4️⃣ ANALISAR DADOS:")
    print("   - Procurar por requisições POST")
    print("   - Encontrar endpoint de dispositivos")
    print("   - Extrair token e assinatura")
    print("   - Replicar no Python")
    print()
    
    print("🔧 MÉTODO MITMPROXY (Alternativa):")
    print()
    print("1️⃣ INSTALAR:")
    print("   pip install mitmproxy")
    print()
    print("2️⃣ CONFIGURAR CELULAR:")
    print("   - Conectar celular na mesma rede")
    print("   - Configurar proxy WiFi: IP_DO_PC:8080")
    print("   - Instalar certificado no celular")
    print()
    print("3️⃣ CAPTURAR:")
    print("   mitmproxy -s capture_tuya.py")
    print("   - Usar app Tuya Smart")
    print("   - Analisar logs capturados")


def main():
    """Função principal"""
    print("🎯 ALTERNATIVAS À LOCAL KEY")
    print("=" * 60)
    print("Explorando APIs do App Tuya Smart")
    print()
    
    # Mostrar opções
    test_tuya_app_api()
    
    # Tentar APIs
    print("\n" + "="*60)
    print("🧪 TESTANDO ENDPOINTS")
    print("="*60)
    
    # Tentar Open API
    try_tuya_open_api()
    
    # Tentar credenciais do app
    try_app_credentials()
    
    # Tentar API mobile
    try_mobile_api()
    
    # Criar guia de interceptação
    create_intercept_guide()
    
    print("\n" + "="*60)
    print("📋 RESUMO")
    print("="*60)
    print("✅ Opções exploradas:")
    print("   - Tuya Open API")
    print("   - API Mobile")
    print("   - Credenciais do app")
    print()
    print("🎯 PRÓXIMA AÇÃO RECOMENDADA:")
    print("   1. Use Wireshark para interceptar comunicação")
    print("   2. Configure dispositivo no app Tuya Smart")
    print("   3. Capture requisições de dispositivos")
    print("   4. Extraia token e endpoint")
    print("   5. Replice no script Python")
    print()
    print("📁 Arquivo útil:")
    print("   - scripts/intercept_tuya_app.py (será criado)")


if __name__ == "__main__":
    main()
