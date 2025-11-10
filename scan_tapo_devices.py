#!/usr/bin/env python3
"""
Script para escanear a rede local e encontrar dispositivos TAPO
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.integrations.tapo_client import TapoClient
from src.utils.config import settings

async def main():
    print("🔍 Escaneando rede local para encontrar dispositivos TAPO...")
    print(f"👤 Usuário: {settings.tapo_username}")
    print()
    
    client = TapoClient(settings.tapo_username, settings.tapo_password)
    
    # Escanear rede
    devices = await client.scan_network()
    
    if devices:
        print(f"✅ Encontrados {len(devices)} dispositivos TAPO:")
        print()
        for device in devices:
            print(f"📱 {device['name']}")
            print(f"   IP: {device['ip']}")
            print(f"   MAC: {device.get('mac', 'N/A')}")
            print(f"   Modelo: {device.get('model', 'N/A')}")
            print()
    else:
        print("❌ Nenhum dispositivo TAPO encontrado na rede")
        print()
        print("💡 Dicas:")
        print("   - Verifique se os dispositivos estão ligados")
        print("   - Confirme que está na mesma rede WiFi")
        print("   - Verifique usuário/senha TAPO no .env")

if __name__ == "__main__":
    asyncio.run(main())
