#!/usr/bin/env python3
"""
Tentar obter Local Key via métodos avançados
"""

import tinytuya
import json
import requests
import time
import sys
from pathlib import Path


def try_advanced_methods():
    """Tentar métodos avançados para obter Local Key"""
    print("🔍 MÉTODOS AVANÇADOS - LOCAL KEY")
    print("=" * 50)
    
    device_id = "eb0254d3ac39b4d2740fwq"
    device_ip = "192.168.68.100"
    product_key = "keyjup78v54myhan"
    
    print(f"Dispositivo:")
    print(f"   ID: {device_id}")
    print(f"   IP: {device_ip}")
    print(f"   Product Key: {product_key}")
    print()
    
    # Método 1: Tentar conexão para forçar revelação da chave
    print("1️⃣ Tentando conexão forçada...")
    try:
        device = tinytuya.OutletDevice(
            dev_id=device_id,
            address=device_ip,
            local_key='',
            version=3.4
        )
        
        # Tentar diferentes payloads
        payloads = [
            device.generate_payload('status'),
            device.generate_payload('set', {'1': True}),
            device.generate_payload('query'),
            {'cmd': 'status'}
        ]
        
        for i, payload in enumerate(payloads):
            try:
                print(f"   Tentativa {i+1}...")
                result = device.send(payload)
                print(f"   Resposta: {result}")
                
                if result and 'dps' in str(result):
                    print(f"   ✅ DPS detectados!")
                    break
                    
            except Exception as e:
                print(f"   Erro {i+1}: {e}")
            
            time.sleep(1)
    
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print()
    
    # Método 2: Verificar se há chave padrão para o produto
    print("2️⃣ Verificando chave padrão do produto...")
    try:
        # Alguns dispositivos usam chaves padrão baseadas no product key
        default_keys = [
            product_key,
            product_key[::-1],  # invertido
            product_key[:16],   # primeira metade
            product_key[16:],   # segunda metade
            "0000000000000000",  # zeros
        ]
        
        for key in default_keys:
            try:
                print(f"   Testando chave: {key[:8]}...")
                device = tinytuya.OutletDevice(
                    dev_id=device_id,
                    address=device_ip,
                    local_key=key,
                    version=3.4
                )
                
                status = device.status()
                if status and 'Error' not in str(status):
                    print(f"   ✅ CHAVE FUNCIONOU!: {key}")
                    return key
                    
            except Exception as e:
                print(f"   Erro: {e}")
    
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print()
    
    # Método 3: Tentar obter via Tuya IoT Platform (se possível)
    print("3️⃣ Verificando Tuya IoT Platform...")
    print("   💡 Acesse: https://iot.tuya.com/")
    print("   💡 Projeto: Casa Inteligente")
    print("   💡 Vá em Devices > encontre seu dispositivo")
    print("   💡 Clique em Device Details > procure Local Key")
    print()
    
    return None


def create_monitoring_script():
    """Criar script de monitoramento que funcionará quando tiver a chave"""
    print("📊 CRIANDO SCRIPT DE MONITORAMENTO")
    print("=" * 50)
    
    monitoring_script = '''#!/usr/bin/env python3
"""
Monitoramento de Energia - Dispositivo Tuya
Execute quando tiver a Local Key
"""

import tinytuya
import time
import json
from datetime import datetime

def monitor_energy():
    """Monitorar consumo de energia"""
    device_id = "eb0254d3ac39b4d2740fwq"
    device_ip = "192.168.68.100"
    local_key = "SUA_LOCAL_KEY_AQUI"  # Substitua aqui
    
    try:
        device = tinytuya.OutletDevice(
            dev_id=device_id,
            address=device_ip,
            local_key=local_key,
            version=3.4
        )
        
        print("🔗 Conectando ao dispositivo...")
        status = device.status()
        
        if status:
            print("✅ Conectado!")
            print("📊 Status inicial:")
            for key, value in status.items():
                print(f"   {key}: {value}")
            
            print("\\n⚡ Iniciando monitoramento de energia...")
            print("   Pressione Ctrl+C para parar")
            
            while True:
                try:
                    # Obter status atual
                    current_status = device.status()
                    
                    # Extrair dados de energia
                    power = current_status.get('18', 0)  # Potência em W
                    voltage = current_status.get('19', 0)  # Tensão em V
                    current = current_status.get('20', 0)  # Corrente em A
                    
                    print(f"{datetime.now().strftime('%H:%M:%S')} - "
                          f"Potência: {power}W, "
                          f"Tensão: {voltage}V, "
                          f"Corrente: {current}A")
                    
                    time.sleep(10)  # Atualizar a cada 10 segundos
                    
                except KeyboardInterrupt:
                    print("\\n⏹️ Monitoramento parado")
                    break
                except Exception as e:
                    print(f"❌ Erro: {e}")
                    time.sleep(5)
        
        else:
            print("❌ Falha na conexão - verifique Local Key")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    monitor_energy()
'''
    
    with open('scripts/monitor_energy.py', 'w') as f:
        f.write(monitoring_script)
    
    print("✅ Script de monitoramento criado: scripts/monitor_energy.py")
    print("💡 Substitua 'SUA_LOCAL_KEY_AQUI' e execute")


def main():
    """Função principal"""
    print("🎯 OBTENDO LOCAL KEY PARA MONITORAMENTO")
    print("=" * 60)
    
    # Tentar métodos avançados
    key = try_advanced_methods()
    
    if key:
        print(f"\n🎉 SUCESSO! Local Key encontrada: {key}")
        print(f"💡 Configure no .env e use scripts de monitoramento")
    else:
        print(f"\n⏳ Local Key não encontrada automaticamente")
        print(f"💡 Use o método mais fácil: app Tuya Smart")
    
    # Criar script de monitoramento
    create_monitoring_script()
    
    print(f"\n📋 PRÓXIMOS PASSOS:")
    print("=" * 40)
    print("1️⃣ Configure o dispositivo no app Tuya Smart")
    print("2️⃣ Obtenha a Local Key")
    print("3️⃣ Configure no .env:")
    print("   TUYA_DEVICE_ID=eb0254d3ac39b4d2740fwq")
    print("   TUYA_IP_ADDRESS=192.168.68.100")
    print("   TUYA_LOCAL_KEY=sua_local_key")
    print("4️⃣ Execute: python scripts/monitor_energy.py")


if __name__ == "__main__":
    main()
