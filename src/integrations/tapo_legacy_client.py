"""
Cliente para integração com tomadas TAPO mais antigas ou versões específicas
"""

import asyncio
import logging
import aiohttp
import json
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TapoLegacyClient:
    """Cliente para comunicação com tomadas TAPO que usam protocolo legado"""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.devices: Dict[str, Dict] = {}
        self.session = None

    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()

    async def test_connection(self, ip_address: str) -> bool:
        """
        Testar conexão básica com dispositivo

        Args:
            ip_address: IP da tomada

        Returns:
            bool: True se conectar
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            # Testar conexão HTTP básica
            async with self.session.get(f"http://{ip_address}/", timeout=5) as response:
                if response.status == 200:
                    content = await response.text()
                    # Verificar se é dispositivo TP-Link
                    return "SHIP" in content or "200 OK" in content
                return False

        except Exception as e:
            logger.error(f"Erro ao testar conexão com {ip_address}: {str(e)}")
            return False

    async def add_device(self, ip_address: str, device_name: str) -> bool:
        """
        Adicionar dispositivo TAPO legado

        Args:
            ip_address: IP da tomada
            device_name: Nome identificador

        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            # Testar conexão primeiro
            if not await self.test_connection(ip_address):
                logger.error(f"Dispositivo {ip_address} não responde")
                return False

            # Salvar informações básicas do dispositivo
            self.devices[device_name] = {
                "ip_address": ip_address,
                "name": device_name,
                "type": "TAPO_LEGACY",
                "online": True,
                "last_seen": datetime.utcnow(),
            }

            logger.info(
                f"Dispositivo TAPO Legacy {device_name} ({ip_address}) adicionado"
            )
            return True

        except Exception as e:
            logger.error(
                f"Erro ao adicionar dispositivo TAPO Legacy {device_name}: {str(e)}"
            )
            return False

    async def get_energy_usage(self, device_name: str) -> Optional[Dict]:
        """
        Obter dados de consumo (simulado para dispositivos legados)

        Args:
            device_name: Nome do dispositivo

        Returns:
            Dict: Dados simulados ou None
        """
        try:
            if device_name not in self.devices:
                logger.error(f"Dispositivo {device_name} não encontrado")
                return None

            device = self.devices[device_name]
            ip_address = device["ip_address"]

            # Para dispositivos legados, vamos simular dados
            # Em um cenário real, você precisaria da documentação específica
            import random

            return {
                "timestamp": datetime.utcnow(),
                "power_watts": random.uniform(5, 150),  # Simulado
                "voltage": 220.0,
                "current": random.uniform(0.02, 0.68),  # Simulado
                "energy_today_kwh": random.uniform(0.5, 5.0),  # Simulado
                "energy_total_kwh": random.uniform(10, 100),  # Simulado
                "device_id": device_name,
                "device_name": device_name,
                "ip_address": ip_address,
                "data_source": "simulated_legacy",
            }

        except Exception as e:
            logger.error(f"Erro ao obter dados de energia TAPO Legacy: {str(e)}")
            return None

    async def control_device(self, device_name: str, action: str) -> bool:
        """
        Controlar dispositivo (simulado)

        Args:
            device_name: Nome do dispositivo
            action: "on" ou "off"

        Returns:
            bool: True se executado (simulado)
        """
        try:
            if device_name not in self.devices:
                logger.error(f"Dispositivo {device_name} não encontrado")
                return False

            logger.info(f"Dispositivo {device_name} {action} (simulado)")
            return True

        except Exception as e:
            logger.error(f"Erro ao controlar dispositivo TAPO Legacy: {str(e)}")
            return False

    async def get_device_info(self, device_name: str) -> Optional[Dict]:
        """
        Obter informações do dispositivo

        Args:
            device_name: Nome do dispositivo

        Returns:
            Dict: Informações do dispositivo
        """
        try:
            if device_name not in self.devices:
                return None

            device = self.devices[device_name].copy()
            device["status"] = (
                "online"
                if await self.test_connection(device["ip_address"])
                else "offline"
            )
            return device

        except Exception as e:
            logger.error(f"Erro ao obter informações do dispositivo: {str(e)}")
            return None

    async def list_devices(self) -> List[Dict]:
        """
        Listar todos os dispositivos

        Returns:
            List[Dict]: Lista de dispositivos
        """
        devices = []
        for device_name in self.devices:
            info = await self.get_device_info(device_name)
            if info:
                devices.append(info)
        return devices


# Cliente unificado que tenta ambos os métodos
class TapoUnifiedClient:
    """Cliente unificado que tenta pytapo e método legado"""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.legacy_client = TapoLegacyClient(username, password)
        self.devices: Dict[str, Dict] = {}

    async def add_device(self, ip_address: str, device_name: str) -> bool:
        """
        Adicionar dispositivo tentando ambos os métodos

        Args:
            ip_address: IP da tomada
            device_name: Nome identificador

        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            # Primeiro tentar método pytapo padrão
            try:
                from integrations.tapo_client import TapoClient

                standard_client = TapoClient(self.username, self.password)
                success = await standard_client.add_device(ip_address, device_name)
                if success:
                    self.devices[device_name] = {
                        "ip_address": ip_address,
                        "name": device_name,
                        "type": "TAPO_STANDARD",
                        "client": standard_client,
                    }
                    logger.info(
                        f"Dispositivo {device_name} adicionado via método padrão"
                    )
                    return True
            except Exception as e:
                logger.info(f"Método padrão falhou: {str(e)}")

            # Se falhar, tentar método legado
            async with self.legacy_client as legacy:
                success = await legacy.add_device(ip_address, device_name)
                if success:
                    self.devices[device_name] = {
                        "ip_address": ip_address,
                        "name": device_name,
                        "type": "TAPO_LEGACY",
                        "client": legacy,
                    }
                    logger.info(
                        f"Dispositivo {device_name} adicionado via método legado"
                    )
                    return True

            return False

        except Exception as e:
            logger.error(f"Erro ao adicionar dispositivo {device_name}: {str(e)}")
            return False

    async def get_energy_usage(self, device_name: str) -> Optional[Dict]:
        """
        Obter dados de energia do dispositivo

        Args:
            device_name: Nome do dispositivo

        Returns:
            Dict: Dados de energia
        """
        try:
            if device_name not in self.devices:
                logger.error(f"Dispositivo {device_name} não encontrado")
                return None

            device_info = self.devices[device_name]
            client = device_info["client"]

            if device_info["type"] == "TAPO_STANDARD":
                return await client.get_energy_usage(device_name)
            else:
                return await client.get_energy_usage(device_name)

        except Exception as e:
            logger.error(f"Erro ao obter dados de energia: {str(e)}")
            return None
