"""
Cliente oficial para API Cloud TAPO TP-Link
Baseado na documentação mais recente da TP-Link Cloud API
"""

import asyncio
import aiohttp
import json
import hashlib
import time
import uuid
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TapoCloudClient:
    """Cliente oficial para TP-Link Cloud API"""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.token = None
        self.device_list = []
        self.base_url = "https://eu-wap.tplinkcloud.com"  # Default EU
        self.terminal_uuid = str(uuid.uuid4())
        self.session = None

    async def __aenter__(self):
        """Context manager entry"""
        # Configurar SSL context para ignorar verificação (dev only)
        ssl_context = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(connector=ssl_context)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()

    async def discover_region(self):
        """Descobrir região correta da API"""
        regions = [
            "https://eu-wap.tplinkcloud.com",
            "https://us-wap.tplinkcloud.com",
            "https://asia-wap.tplinkcloud.com",
            "https://wap.tplinkcloud.com",
        ]

        # Configurar SSL context
        ssl_context = aiohttp.TCPConnector(ssl=False)

        for region in regions:
            try:
                async with aiohttp.ClientSession(connector=ssl_context) as session:
                    # Testar conexão básica
                    async with session.get(
                        f"{region}/api/v2/server/info", timeout=5
                    ) as response:
                        if response.status == 200:
                            self.base_url = region
                            logger.info(f"Região descoberta: {region}")
                            return True
            except:
                continue

        logger.error("Não foi possível descobrir região da API")
        return False

    async def login(self) -> bool:
        """
        Fazer login na TP-Link Cloud

        Returns:
            bool: True se login bem-sucedido
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            # Descobrir região se necessário
            if not await self.discover_region():
                logger.warning("Usando região padrão (EU)")

            login_url = f"{self.base_url}/api/v2/login"

            login_data = {
                "appType": "Tapo_Android",
                "cloudPassword": self.password,
                "cloudUserName": self.username,
                "terminalUUID": self.terminal_uuid,
            }

            logger.info(f"Fazendo login na TP-Link Cloud: {self.username}")

            async with self.session.post(
                login_url, json=login_data, timeout=10
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    if "result" in result and "token" in result["result"]:
                        self.token = result["result"]["token"]
                        logger.info("Login TP-Link Cloud bem-sucedido")

                        # Obter lista de dispositivos
                        await self.refresh_device_list()
                        return True
                    else:
                        logger.error(f"Login falhou: {result}")
                        return False
                else:
                    logger.error(f"Erro HTTP no login: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Erro ao fazer login TP-Link Cloud: {str(e)}")
            return False

    async def refresh_device_list(self) -> bool:
        """
        Atualizar lista de dispositivos

        Returns:
            bool: True se bem-sucedido
        """
        try:
            if not self.token:
                logger.error("Token não disponível")
                return False

            device_list_url = f"{self.base_url}/api/v2/device/getDeviceList"

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }

            async with self.session.post(
                device_list_url, headers=headers, timeout=10
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    if "result" in result and "deviceList" in result["result"]:
                        self.device_list = result["result"]["deviceList"]
                        logger.info(
                            f"Encontrados {len(self.device_list)} dispositivos na cloud"
                        )
                        return True
                    else:
                        logger.error(f"Erro ao obter dispositivos: {result}")
                        return False
                else:
                    logger.error(f"Erro HTTP ao listar dispositivos: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Erro ao obter lista de dispositivos: {str(e)}")
            return False

    async def get_device_list(self) -> List[Dict]:
        """
        Obter lista de dispositivos

        Returns:
            List[Dict]: Lista de dispositivos
        """
        if not self.device_list:
            await self.refresh_device_list()

        return self.device_list

    async def get_device_info(self, device_id: str) -> Optional[Dict]:
        """
        Obter informações detalhadas do dispositivo

        Args:
            device_id: ID do dispositivo

        Returns:
            Dict: Informações do dispositivo
        """
        try:
            if not self.token:
                return None

            device_info_url = f"{self.base_url}/api/v2/device/getDeviceInfo"

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }

            device_data = {"device_id": device_id}

            async with self.session.post(
                device_info_url, headers=headers, json=device_data, timeout=10
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    if "result" in result and "responseData" in result["result"]:
                        return result["result"]["responseData"]
                    else:
                        logger.error(
                            f"Erro ao obter info do dispositivo {device_id}: {result}"
                        )
                        return None
                else:
                    logger.error(
                        f"Erro HTTP ao obter info do dispositivo: {response.status}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Erro ao obter informações do dispositivo: {str(e)}")
            return None

    async def get_energy_usage(self, device_id: str) -> Optional[Dict]:
        """
        Obter dados de consumo de energia

        Args:
            device_id: ID do dispositivo

        Returns:
            Dict: Dados de energia
        """
        try:
            if not self.token:
                return None

            # Obter informações do dispositivo que incluem dados de energia
            device_info = await self.get_device_info(device_id)

            if not device_info:
                return None

            # Extrair dados de energia se disponíveis
            energy_data = {
                "timestamp": datetime.utcnow(),
                "device_id": device_id,
                "power_watts": 0,
                "voltage": 220.0,
                "current": 0,
                "energy_today_kwh": 0,
                "energy_total_kwh": 0,
                "data_source": "tapo_cloud",
            }

            # Verificar diferentes campos onde podem estar os dados de energia
            if "power_usage" in device_info:
                energy_data.update(
                    {
                        "power_watts": device_info["power_usage"].get(
                            "current_power", 0
                        ),
                        "energy_today_kwh": device_info["power_usage"].get(
                            "today_energy", 0
                        ),
                        "energy_total_kwh": device_info["power_usage"].get(
                            "total_energy", 0
                        ),
                    }
                )

            elif "energy_monitoring" in device_info:
                energy_data.update(
                    {
                        "power_watts": device_info["energy_monitoring"].get(
                            "current_power", 0
                        ),
                        "voltage": device_info["energy_monitoring"].get(
                            "voltage", 220.0
                        ),
                        "current": device_info["energy_monitoring"].get("current", 0),
                        "energy_today_kwh": device_info["energy_monitoring"].get(
                            "today_energy", 0
                        ),
                        "energy_total_kwh": device_info["energy_monitoring"].get(
                            "total_energy", 0
                        ),
                    }
                )

            elif "device_info" in device_info:
                info = device_info["device_info"]
                energy_data.update(
                    {
                        "power_watts": info.get("power", 0),
                        "voltage": info.get("voltage", 220.0),
                        "current": info.get("current", 0),
                        "energy_today_kwh": info.get("energy_today", 0),
                        "energy_total_kwh": info.get("energy_total", 0),
                    }
                )

            return energy_data

        except Exception as e:
            logger.error(f"Erro ao obter dados de energia: {str(e)}")
            return None

    async def control_device(self, device_id: str, action: str) -> bool:
        """
        Controlar dispositivo (ligar/desligar)

        Args:
            device_id: ID do dispositivo
            action: "on" ou "off"

        Returns:
            bool: True se executado com sucesso
        """
        try:
            if not self.token:
                return False

            control_url = f"{self.base_url}/api/v2/device/control"

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }

            control_data = {
                "device_id": device_id,
                "request_data": {"turn_on": action == "on", "request": action},
            }

            async with self.session.post(
                control_url, headers=headers, json=control_data, timeout=10
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    if "result" in result and result["result"] == "success":
                        logger.info(f"Dispositivo {device_id} {action} com sucesso")
                        return True
                    else:
                        logger.error(f"Erro ao controlar dispositivo: {result}")
                        return False
                else:
                    logger.error(
                        f"Erro HTTP ao controlar dispositivo: {response.status}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Erro ao controlar dispositivo: {str(e)}")
            return False

    async def test_connection(self) -> bool:
        """
        Testar conexão com a API Cloud

        Returns:
            bool: True se conexão OK
        """
        try:
            if await self.login():
                devices = await self.get_device_list()
                logger.info(
                    f"Conexão TP-Link Cloud OK. {len(devices)} dispositivos encontrados."
                )
                return True
            return False

        except Exception as e:
            logger.error(f"Erro ao testar conexão TP-Link Cloud: {str(e)}")
            return False

    def find_device_by_name(self, name: str) -> Optional[str]:
        """
        Encontrar device ID pelo nome

        Args:
            name: Nome do dispositivo

        Returns:
            str: Device ID ou None
        """
        for device in self.device_list:
            if device.get("alias", "").lower() == name.lower():
                return device.get("device_id")

        return None

    def find_device_by_ip(self, ip: str) -> Optional[str]:
        """
        Encontrar device ID pelo IP (se disponível)

        Args:
            ip: IP do dispositivo

        Returns:
            str: Device ID ou None
        """
        for device in self.device_list:
            if device.get("device_ip", "") == ip:
                return device.get("device_id")

        return None
