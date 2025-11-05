"""
Cliente para integração com tomadas inteligentes Nova Digital
"""

import asyncio
import logging
import aiohttp
import json
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NovaDigitalClient:
    """Cliente para comunicação com tomadas Nova Digital"""

    def __init__(self, api_key: str, base_url: str = "https://api.novadigital.com.br"):
        self.api_key = api_key
        self.base_url = base_url
        self.devices: Dict[str, Dict] = {}
        self.session = None

    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()

    async def authenticate(self) -> bool:
        """
        Autenticar com a API Nova Digital
        
        Returns:
            bool: True se autenticado com sucesso
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    }
                )

            # Testar autenticação
            async with self.session.get(f"{self.base_url}/auth/verify") as response:
                if response.status == 200:
                    logger.info("Autenticação Nova Digital bem-sucedida")
                    return True
                else:
                    logger.error(
                        f"Falha na autenticação Nova Digital: {response.status}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Erro ao autenticar com Nova Digital: {str(e)}")
            return False

    async def get_devices(self) -> List[Dict]:
        """
        Obter lista de dispositivos cadastrados
        
        Returns:
            List[Dict]: Lista de dispositivos
        """
        try:
            async with self.session.get(f"{self.base_url}/devices") as response:
                if response.status == 200:
                    devices = await response.json()
                    logger.info(f"Encontrados {len(devices)} dispositivos Nova Digital")
                    return devices
                else:
                    logger.error(f"Erro ao obter dispositivos: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Erro ao obter dispositivos Nova Digital: {str(e)}")
            return []

    async def add_device(self, device_id: str, device_name: str) -> bool:
        """
        Adicionar um dispositivo Nova Digital
        
        Args:
            device_id: ID do dispositivo na Nova Digital
            device_name: Nome identificador local
            
        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            # Obter informações do dispositivo
            async with self.session.get(
                f"{self.base_url}/devices/{device_id}"
            ) as response:
                if response.status == 200:
                    device_info = await response.json()
                    self.devices[device_name] = {
                        "id": device_id,
                        "name": device_name,
                        "info": device_info,
                    }
                    logger.info(
                        f"Dispositivo Nova Digital {device_name} ({device_id}) adicionado com sucesso"
                    )
                    return True
                else:
                    logger.error(
                        f"Dispositivo {device_id} não encontrado: {response.status}"
                    )
                    return False

        except Exception as e:
            logger.error(
                f"Erro ao adicionar dispositivo Nova Digital {device_name}: {str(e)}"
            )
            return False

    async def get_energy_usage(self, device_name: str) -> Optional[Dict]:
        """
        Obter dados de consumo de energia de um dispositivo
        
        Args:
            device_name: Nome do dispositivo
            
        Returns:
            Dict: Dados de consumo ou None se erro
        """
        try:
            if device_name not in self.devices:
                logger.error(f"Dispositivo {device_name} não encontrado")
                return None

            device_id = self.devices[device_name]["id"]

            # Obter dados de energia em tempo real
            async with self.session.get(
                f"{self.base_url}/devices/{device_id}/energy"
            ) as response:
                if response.status == 200:
                    energy_data = await response.json()

                    # Padronizar formato de dados
                    return {
                        "timestamp": datetime.utcnow(),
                        "power_watts": energy_data.get("power", 0),
                        "voltage": energy_data.get("voltage", 220),
                        "current": energy_data.get("current", 0),
                        "energy_today_kwh": energy_data.get("energy_today", 0),
                        "energy_total_kwh": energy_data.get("energy_total", 0),
                        "device_id": device_id,
                        "device_name": device_name,
                    }
                else:
                    logger.error(
                        f"Erro ao obter dados de energia do dispositivo {device_name}: {response.status}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Erro ao obter dados de energia Nova Digital: {str(e)}")
            return None

    async def get_historical_data(
        self, device_name: str, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """
        Obter dados históricos de consumo
        
        Args:
            device_name: Nome do dispositivo
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            List[Dict]: Lista de dados históricos
        """
        try:
            if device_name not in self.devices:
                logger.error(f"Dispositivo {device_name} não encontrado")
                return []

            device_id = self.devices[device_name]["id"]

            params = {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "interval": "hour",  # ou "day", "month"
            }

            async with self.session.get(
                f"{self.base_url}/devices/{device_id}/energy/history", params=params
            ) as response:
                if response.status == 200:
                    historical_data = await response.json()

                    # Padronizar formato
                    standardized_data = []
                    for record in historical_data:
                        standardized_data.append(
                            {
                                "timestamp": datetime.fromisoformat(
                                    record["timestamp"]
                                ),
                                "power_watts": record.get("power", 0),
                                "energy_kwh": record.get("energy", 0),
                                "device_id": device_id,
                                "device_name": device_name,
                            }
                        )

                    return standardized_data
                else:
                    logger.error(f"Erro ao obter dados históricos: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Erro ao obter dados históricos Nova Digital: {str(e)}")
            return []

    async def control_device(self, device_name: str, action: str) -> bool:
        """
        Controlar dispositivo (ligar/desligar)
        
        Args:
            device_name: Nome do dispositivo
            action: "on" ou "off"
            
        Returns:
            bool: True se executado com sucesso
        """
        try:
            if device_name not in self.devices:
                logger.error(f"Dispositivo {device_name} não encontrado")
                return False

            device_id = self.devices[device_name]["id"]

            data = {"action": action}

            async with self.session.post(
                f"{self.base_url}/devices/{device_id}/control", json=data
            ) as response:
                if response.status == 200:
                    logger.info(f"Dispositivo {device_name} {action} com sucesso")
                    return True
                else:
                    logger.error(
                        f"Erro ao controlar dispositivo {device_name}: {response.status}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Erro ao controlar dispositivo Nova Digital: {str(e)}")
            return False

    async def test_connection(self) -> bool:
        """
        Testar conexão com a API Nova Digital
        
        Returns:
            bool: True se conexão OK
        """
        try:
            if await self.authenticate():
                devices = await self.get_devices()
                logger.info(
                    f"Conexão Nova Digital OK. {len(devices)} dispositivos encontrados."
                )
                return True
            return False

        except Exception as e:
            logger.error(f"Erro ao testar conexão Nova Digital: {str(e)}")
            return False


# Classe de fábrica para criar clientes automaticamente
class DeviceClientFactory:
    """Fábrica para criar clientes de diferentes fabricantes"""

    @staticmethod
    def create_client(device_type: str, **kwargs):
        """
        Criar cliente baseado no tipo de dispositivo
        
        Args:
            device_type: "TAPO" ou "NOVA_DIGITAL"
            **kwargs: Parâmetros específicos do cliente
            
        Returns:
            Instância do cliente correspondente
        """
        if device_type.upper() == "TAPO":
            from src.integrations.tapo_client import TapoClient

            return TapoClient(
                username=kwargs.get("username"), password=kwargs.get("password")
            )
        elif device_type.upper() == "NOVA_DIGITAL":
            return NovaDigitalClient(
                api_key=kwargs.get("api_key"),
                base_url=kwargs.get("base_url", "https://api.novadigital.com.br"),
            )
        else:
            raise ValueError(f"Tipo de dispositivo não suportado: {device_type}")
