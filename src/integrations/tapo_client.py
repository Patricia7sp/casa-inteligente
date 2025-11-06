"""
Cliente para integração com tomadas inteligentes TP-Link TAPO
"""

import asyncio
import logging
from typing import Dict, List, Optional
from pytapo import Tapo
from datetime import datetime

logger = logging.getLogger(__name__)


class TapoClient:
    """Cliente para comunicação com tomadas TAPO"""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.devices: Dict[str, Tapo] = {}

    async def add_device(self, ip_address: str, device_name: str) -> bool:
        """
        Adicionar um dispositivo TAPO

        Args:
            ip_address: Endereço IP da tomada
            device_name: Nome identificador do dispositivo

        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            device = Tapo(ip_address, self.username, self.password)
            # Testar conexão
            await device.getDeviceInfo()
            self.devices[device_name] = device
            logger.info(
                f"Dispositivo TAPO {device_name} ({ip_address}) adicionado com sucesso"
            )
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar dispositivo TAPO {device_name}: {str(e)}")
            return False

    async def get_energy_usage(self, device_name: str) -> Optional[Dict]:
        """
        Obter dados de consumo de energia de um dispositivo

        Args:
            device_name: Nome do dispositivo

        Returns:
            Dict com dados de consumo ou None se erro
        """
        if device_name not in self.devices:
            logger.error(f"Dispositivo {device_name} não encontrado")
            return None

        try:
            device = self.devices[device_name]

            # Obter informações de energia
            energy_info = await device.getEnergyUsage()

            # Obter informações atuais
            device_info = await device.getDeviceInfo()

            data = {
                "timestamp": datetime.utcnow(),
                "power_watts": energy_info.get("current_power", 0),
                "voltage": energy_info.get("voltage", 0),
                "current": energy_info.get("current", 0),
                "energy_today_kwh": energy_info.get("today_energy", 0)
                / 1000,  # Converter para kWh
                "energy_total_kwh": energy_info.get("total_energy", 0)
                / 1000,  # Converter para kWh
                "device_on": device_info.get("device_on", False),
            }

            logger.info(
                f"Dados coletados do dispositivo {device_name}: {data['power_watts']:.2f}W"
            )
            return data

        except Exception as e:
            logger.error(f"Erro ao obter dados do dispositivo {device_name}: {str(e)}")
            return None

    async def turn_on(self, device_name: str) -> bool:
        """Ligar um dispositivo"""
        if device_name not in self.devices:
            return False

        try:
            await self.devices[device_name].turnOn()
            logger.info(f"Dispositivo {device_name} ligado")
            return True
        except Exception as e:
            logger.error(f"Erro ao ligar dispositivo {device_name}: {str(e)}")
            return False

    async def turn_off(self, device_name: str) -> bool:
        """Desligar um dispositivo"""
        if device_name not in self.devices:
            return False

        try:
            await self.devices[device_name].turnOff()
            logger.info(f"Dispositivo {device_name} desligado")
            return True
        except Exception as e:
            logger.error(f"Erro ao desligar dispositivo {device_name}: {str(e)}")
            return False

    async def get_device_info(self, device_name: str) -> Optional[Dict]:
        """Obter informações do dispositivo"""
        if device_name not in self.devices:
            return None

        try:
            return await self.devices[device_name].getDeviceInfo()
        except Exception as e:
            logger.error(
                f"Erro ao obter informações do dispositivo {device_name}: {str(e)}"
            )
            return None

    async def test_connection(self, ip_address: str) -> bool:
        """Testar conexão com um dispositivo pelo IP"""
        try:
            device = Tapo(ip_address, self.username, self.password)
            await device.getDeviceInfo()
            return True
        except Exception as e:
            logger.error(f"Erro ao testar conexão com {ip_address}: {str(e)}")
            return False

    async def scan_network(self, ip_range: str = "192.168.1") -> List[str]:
        """
        Escanear rede em busca de dispositivos TAPO

        Args:
            ip_range: Range de IP para escanear (ex: "192.168.1")

        Returns:
            Lista de IPs com dispositivos TAPO encontrados
        """
        found_devices = []

        for i in range(1, 255):
            ip = f"{ip_range}.{i}"
            if await self.test_connection(ip):
                found_devices.append(ip)
                logger.info(f"Dispositivo TAPO encontrado em {ip}")

        return found_devices
