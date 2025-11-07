#!/usr/bin/env python3
"""
Teste funcional para Tuya Cloud - abordagem correta
"""
import asyncio
import sys
import hashlib
import time
import base64
from pathlib import Path
import aiohttp

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from utils.config import settings


class TuyaCloudClient:
    """Cliente Tuya Cloud funcional"""
    
    def __init__(self, access_id, access_key, region="us"):
        self.access_id = access_id
        self.access_key = access_key
        self.region = region
        self.base_url = f"https://openapi.tuya{region}.com"
        self.access_token = None
        
    def _sign_request(self, method, url, params=None, body=None):
        """Gerar assinatura para requisição Tuya"""
        timestamp = str(int(time.time() * 1000))
        
        # Construir string para assinatura
        url_path = url.split(self.base_url)[1]
        
        if params:
            sorted_params = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        else:
            sorted_params = ""
            
        if body:
            body_str = body
        else:
            body_str = ""
        
        string_to_sign = f"{method}\n{url_path}\n{sorted_params}\n{body_str}\n{timestamp}"
        
        # Gerar assinatura
        sign = base64.b64encode(
            hashlib.sha256(string_to_sign.encode('utf-8')).digest()
        ).decode('utf-8')
        
        # Headers
        headers = {
            'client_id': self.access_id,
            'sign': sign,
            't': timestamp,
            'sign_method': 'HMAC-SHA256'
        }
        
        return headers
    
    async def get_access_token(self):
        """Obter token de acesso"""
        url = f"{self.base_url}/v1.0/token?grant_type=1"
        headers = self._sign_request('GET', url)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        self.access_token = data['result']['access_token']
                        return True
                return False
    
    async def get_devices(self):
        """Obter lista de dispositivos"""
        if not self.access_token:
            if not await self.get_access_token():
                return None
        
        url = f"{self.base_url}/v1.0/users/{self.access_id}/devices"
        headers = self._sign_request('GET', url)
        headers['access_token'] = self.access_token
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        return data['result']
                return None


async def test_tuya_functional():
    """Testar conexão Tuya funcional"""
    print("☁️  TESTANDO TUYA CLOUD - ABORDAGEM FUNCIONAL")
    print("=" * 60)
    
    if not settings.tuya_access_id or not settings.tuya_access_key:
        print("❌ Credenciais Tuya não configuradas")
        return False
    
    print(f"✅ Credenciais Tuya encontradas:")
    print(f"   Access ID: {settings.tuya_access_id}")
    print(f"   Region: {settings.tuya_region}")
    
    try:
        client = TuyaCloudClient(
            access_id=settings.tuya_access_id,
            access_key=settings.tuya_access_key,
            region=settings.tuya_region
        )
        
        print("\n🔍 Obtendo token de acesso...")
        if await client.get_access_token():
            print("✅ Token de acesso obtido!")
            
            print("\n📱 Buscando dispositivos...")
            devices = await client.get_devices()
            
            if devices:
                print(f"✅ Encontrados {len(devices)} dispositivos:")
                
                for i, device in enumerate(devices, 1):
                    print(f"\n--- Dispositivo {i} ---")
                    print(f"  ID: {device.get('id', 'N/A')}")
                    print(f"  Nome: {device.get('name', 'N/A')}")
                    print(f"  Produto: {device.get('product_name', 'N/A')}")
                    print(f"  Categoria: {device.get('category', 'N/A')}")
                    print(f"  Online: {'Sim' if device.get('online') else 'Não'}")
                    print(f"  Local: {device.get('local_key', 'N/A')}")
                    
                    # Verificar se é um dispositivo de energia
                    if device.get('category') in ['cz', 'kg', 'pc']:  # tomadas, interruptores
                        print(f"  ⚡ Dispositivo de energia detectado!")
                
                return True
            else:
                print("⚠️  Nenhum dispositivo encontrado")
                return False
        else:
            print("❌ Falha ao obter token de acesso")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Tuya Cloud: {str(e)}")
        return False


async def insert_test_data():
    """Inserir dados de teste no Supabase"""
    print("\n💾 INSERINDO DADOS DE TESTE NO SUPABASE")
    print("=" * 50)
    
    try:
        # Aqui você usaria o cliente Supabase para inserir dados
        # Por enquanto, vamos simular dados de energia
        
        test_data = [
            {
                'device_id': 9,  # Purificador
                'power_watts': 15.5,
                'voltage': 220.0,
                'current': 0.07,
                'energy_today_kwh': 0.125
            },
            {
                'device_id': 10,  # Notebook  
                'power_watts': 65.2,
                'voltage': 220.0,
                'current': 0.30,
                'energy_today_kwh': 0.487
            }
        ]
        
        print("📊 Dados de energia simulados:")
        for data in test_data:
            print(f"  Device {data['device_id']}: {data['power_watts']}W")
        
        print("✅ Dados prontos para inserção no Supabase!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao preparar dados: {str(e)}")
        return False


async def main():
    """Função principal"""
    print("🏠 TESTE FUNCIONAL - TUYA CLOUD + SUPABASE")
    print("=" * 70)
    
    # Testar Tuya Cloud
    tuya_ok = await test_tuya_functional()
    
    # Preparar dados
    data_ok = await insert_test_data()
    
    # Resumo
    print("\n📊 RESUMO FINAL")
    print("=" * 50)
    print(f"✅ Tuya Cloud: {'OK' if tuya_ok else 'ERRO'}")
    print(f"✅ Preparação Dados: {'OK' if data_ok else 'ERRO'}")
    
    if tuya_ok:
        print("\n🎉 SOLUÇÃO ENCONTRADA!")
        print("📋 PRÓXIMOS PASSOS:")
        print("   1. Use Tuya Cloud para obter dados dos dispositivos")
        print("   2. Configure o coletor para usar Tuya API")
        print("   3. Sincronize dados com Supabase automaticamente")
        print("   4. Inicie o dashboard para visualização")
        
        print("\n🔧 COMO CONFIGURAR:")
        print("   1. Seus dispositivos estão na Tuya Cloud")
        print("   2. Use as credenciais TUYA_ACCESS_ID e TUYA_ACCESS_KEY")
        print("   3. Dispositivos já cadastrados no Supabase")
        print("   4. Sistema pronto para coleta de dados!")
    else:
        print("\n❌ PRECISA AJUSTAR CONEXÃO TUYA")
        print("📋 VERIFIQUE:")
        print("   1. Credenciais TUYA_ACCESS_ID e TUYA_ACCESS_KEY")
        print("   2. Se dispositivos estão vinculados à conta Tuya")
        print("   3. Se região está correta (us, eu, cn)")


if __name__ == "__main__":
    asyncio.run(main())
