#!/usr/bin/env python3
"""
Cliente Local Tuya - Solução imediata sem Cloud API
"""

import tinytuya
import json
import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from utils.config import settings
except ImportError:
    # Se não encontrar config, usar variáveis de ambiente
    import os

    class Settings:
        def __getattr__(self, name):
            return os.getenv(name.upper(), None)

    settings = Settings()


class TuyaLocalClient:
    """Cliente local para dispositivos Tuya sem Cloud API"""

    def __init__(self):
        self.devices = []
        self.connected_devices = {}

    async def discover_devices(self) -> List[Dict]:
        """
        Descobrir dispositivos Tuya na rede local

        Returns:
            List[Dict]: Lista de dispositivos encontrados
        """
        print("🔍 Descobrindo dispositivos Tuya na rede...")
        print("-" * 50)

        try:
            # Descobrir dispositivos na rede
            devices = tinytuya.deviceScan()

            if not devices:
                print("❌ Nenhum dispositivo encontrado")
                print("💡 Verifique:")
                print("   - Dispositivos estão na mesma rede WiFi")
                print("   - Dispositivos estão configurados no app Tuya")
                print("   - Firewall não está bloqueando")
                return []

            print(f"✅ Encontrados {len(devices)} dispositivo(s):")

            device_list = []
            for ip, dev in devices.items():
                device_info = {
                    "ip": ip,
                    "id": dev.get("id", "Unknown"),
                    "name": f"Device_{dev.get('id', 'Unknown')[:8]}",
                    "key": dev.get("key", ""),
                    "version": dev.get("version", "3.3"),
                }

                print(f"   📱 {device_info['name']}")
                print(f"      IP: {ip}")
                print(f"      ID: {dev.get('id')}")
                print(f"      Versão: {dev.get('version')}")
                print()

                device_list.append(device_info)

            self.devices = device_list
            return device_list

        except Exception as e:
            print(f"❌ Erro ao descobrir dispositivos: {e}")
            return []

    async def connect_device(self, device_id: str, ip: str, local_key: str) -> bool:
        """
        Conectar a um dispositivo específico

        Args:
            device_id: ID do dispositivo
            ip: Endereço IP do dispositivo
            local_key: Chave local do dispositivo

        Returns:
            bool: True se conexão bem-sucedida
        """
        try:
            print(f"🔗 Conectando ao dispositivo {device_id}...")

            # Criar conexão com dispositivo
            device = tinytuya.OutletDevice(
                dev_id=device_id, address=ip, local_key=local_key
            )

            # Testar conexão
            status = device.status()

            if status:
                print(f"✅ Conectado com sucesso!")
                print(f"   Status: {status}")

                self.connected_devices[device_id] = device
                return True
            else:
                print(f"❌ Falha na conexão")
                return False

        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False

    async def get_device_status(self, device_id: str) -> Optional[Dict]:
        """
        Obter status de um dispositivo

        Args:
            device_id: ID do dispositivo

        Returns:
            Dict: Status do dispositivo
        """
        try:
            if device_id not in self.connected_devices:
                print(f"❌ Dispositivo {device_id} não conectado")
                return None

            device = self.connected_devices[device_id]
            status = device.status()

            return status

        except Exception as e:
            print(f"❌ Erro ao obter status: {e}")
            return None

    async def control_device(self, device_id: str, command: Dict) -> bool:
        """
        Controlar um dispositivo

        Args:
            device_id: ID do dispositivo
            command: Comando de controle

        Returns:
            bool: True se comando executado com sucesso
        """
        try:
            if device_id not in self.connected_devices:
                print(f"❌ Dispositivo {device_id} não conectado")
                return False

            device = self.connected_devices[device_id]

            # Enviar comando
            result = device.set_value(command)

            if result:
                print(f"✅ Comando enviado: {command}")
                return True
            else:
                print(f"❌ Falha ao enviar comando")
                return False

        except Exception as e:
            print(f"❌ Erro ao controlar dispositivo: {e}")
            return False

    async def get_energy_data(self, device_id: str) -> Optional[Dict]:
        """
        Obter dados de energia do dispositivo

        Args:
            device_id: ID do dispositivo

        Returns:
            Dict: Dados de energia
        """
        try:
            if device_id not in self.connected_devices:
                print(f"❌ Dispositivo {device_id} não conectado")
                return None

            device = self.connected_devices[device_id]

            # Obter status completo (inclui dados de energia se disponível)
            status = device.status()

            # Extrair dados de energia
            energy_data = {}
            for key, value in status.items():
                if (
                    "power" in key.lower()
                    or "energy" in key.lower()
                    or "voltage" in key.lower()
                ):
                    energy_data[key] = value

            return energy_data if energy_data else None

        except Exception as e:
            print(f"❌ Erro ao obter dados de energia: {e}")
            return None

    async def test_connection(self) -> bool:
        """
        Testar conexão completa

        Returns:
            bool: True se tudo funcionando
        """
        print("🧪 TESTE COMPLETO - API LOCAL TUYA")
        print("=" * 50)

        # Descobrir dispositivos
        devices = await self.discover_devices()

        if not devices:
            print("❌ Nenhum dispositivo encontrado")
            return False

        # Tentar conectar ao primeiro dispositivo
        first_device = devices[0]

        # Para teste, vamos tentar sem chave local primeiro
        print(f"\n🔧 Testando conexão básica...")

        try:
            device = tinytuya.OutletDevice(
                dev_id=first_device["id"],
                address=first_device["ip"],
                local_key="",  # Tentar sem chave primeiro
            )

            status = device.status()

            if status:
                print(f"✅ Conexão bem-sucedida!")
                print(f"📊 Status do dispositivo:")
                for key, value in status.items():
                    print(f"   {key}: {value}")

                # Testar controle se for tomada
                if "1" in status:  # Indica que é tomada
                    print(f"\n🎛️  Testando controle...")

                    # Ligar
                    device.turn_on()
                    await asyncio.sleep(2)

                    # Desligar
                    device.turn_off()
                    await asyncio.sleep(2)

                    # Ligar novamente
                    device.turn_on()

                    print(f"✅ Controle testado com sucesso!")

                return True
            else:
                print(f"❌ Falha na conexão - pode precisar de Local Key")
                print(f"💡 Para obter Local Key:")
                print(f"   1. Use app Tuya Smart")
                print(f"   2. Configure o dispositivo")
                print(f"   3. Use ferramenta tinytuya scan")

                return False

        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            return False


async def main():
    """Função principal para testar API local"""
    client = TuyaLocalClient()
    success = await client.test_connection()

    if success:
        print(f"\n🎉 API LOCAL TUYA FUNCIONANDO!")
        print(f"✅ Solução implementada com sucesso")
        print(f"✅ Sem dependência de Cloud API")
        print(f"✅ Controle local disponível")
    else:
        print(f"\n❌ API LOCAL PRECISA DE CONFIGURAÇÃO")
        print(f"💡 Siga os passos no GUIA_API_LOCAL_TUYA.md")


if __name__ == "__main__":
    asyncio.run(main())
