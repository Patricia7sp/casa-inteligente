"""
Cliente para integração com dispositivos TP-Link Tapo
Suporta tomadas inteligentes P100, P110 e similares
Usa a biblioteca 'tapo' (Rust-based, oficial e confiável)
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from tapo import ApiClient

logger = logging.getLogger(__name__)


class TapoClient:
    """Cliente para comunicação com dispositivos TAPO usando biblioteca tapo"""

    def __init__(self, username: str, password: str):
        """
        Inicializar cliente TAPO

        Args:
            username: Email da conta TP-Link/Tapo
            password: Senha da conta TP-Link/Tapo
        """
        self.username = username
        self.password = password
        self.api_client = None
        self.devices: Dict[str, any] = {}  # {device_name: device_handler}

    async def _get_api_client(self) -> ApiClient:
        """Obter cliente API (lazy initialization)"""
        if not self.api_client:
            self.api_client = ApiClient(self.username, self.password)
        return self.api_client

    async def add_device(self, ip_address: str, device_name: str) -> bool:
        """
        Adicionar um dispositivo TAPO

        Args:
            ip_address: IP do dispositivo
            device_name: Nome identificador do dispositivo

        Returns:
            True se adicionado com sucesso
        """
        try:
            client = await self._get_api_client()

            # Conectar ao dispositivo P110 (tomada com medição de energia)
            device = await client.p110(ip_address)

            # Testar conexão obtendo informações do dispositivo
            device_info = await device.get_device_info()

            self.devices[device_name] = device
            logger.info(
                f"✅ Dispositivo {device_name} ({ip_address}) adicionado com sucesso"
            )
            logger.debug(f"   Modelo: {device_info.model}, FW: {device_info.fw_ver}")

            return True

        except Exception as e:
            logger.error(
                f"❌ Erro ao adicionar dispositivo {device_name} ({ip_address}): {str(e)}"
            )
            return False

    async def get_energy_usage(self, device_name: str) -> Optional[Dict]:
        """
        Obter dados de consumo de energia de um dispositivo

        Args:
            device_name: Nome do dispositivo

        Returns:
            Dicionário com dados de energia ou None se falhar
        """
        if device_name not in self.devices:
            logger.error(f"Dispositivo {device_name} não encontrado")
            return None

        try:
            device = self.devices[device_name]

            # Obter informações de energia
            current_power = await device.get_current_power()
            energy_usage = await device.get_energy_usage()
            device_info = await device.get_device_info()

            # Converter para formato esperado
            data = {
                "timestamp": datetime.now(),
                "power_watts": current_power.current_power / 1000.0,  # mW para W
                "voltage": 127,  # Valor padrão Brasil (P110 não fornece)
                "current": (
                    current_power.current_power / 127000.0
                    if current_power.current_power > 0
                    else 0
                ),  # Estimativa
                "energy_today_kwh": energy_usage.today_energy / 1000.0,  # Wh para kWh
                "device_on": device_info.device_on,
                "today_runtime": energy_usage.today_runtime,  # segundos ligado hoje
            }

            logger.debug(
                f"📊 {device_name}: {data['power_watts']:.1f}W, {data['energy_today_kwh']:.3f}kWh hoje"
            )

            return data

        except Exception as e:
            logger.error(f"Erro ao obter dados de energia de {device_name}: {str(e)}")
            return None

    async def turn_on(self, device_name: str) -> bool:
        """Ligar dispositivo"""
        if device_name not in self.devices:
            logger.error(f"Dispositivo {device_name} não encontrado")
            return False

        try:
            device = self.devices[device_name]
            await device.on()
            logger.info(f"✅ {device_name} ligado")
            return True
        except Exception as e:
            logger.error(f"Erro ao ligar {device_name}: {str(e)}")
            return False

    async def turn_off(self, device_name: str) -> bool:
        """Desligar dispositivo"""
        if device_name not in self.devices:
            logger.error(f"Dispositivo {device_name} não encontrado")
            return False

        try:
            device = self.devices[device_name]
            await device.off()
            logger.info(f"✅ {device_name} desligado")
            return True
        except Exception as e:
            logger.error(f"Erro ao desligar {device_name}: {str(e)}")
            return False

    async def get_device_info(self, device_name: str) -> Optional[Dict]:
        """Obter informações do dispositivo"""
        if device_name not in self.devices:
            logger.error(f"Dispositivo {device_name} não encontrado")
            return None

        try:
            device = self.devices[device_name]
            info = await device.get_device_info()

            return {
                "device_id": info.device_id,
                "type": info.type,
                "model": info.model,
                "hw_ver": info.hw_ver,
                "fw_ver": info.fw_ver,
                "mac": info.mac,
                "device_on": info.device_on,
                "on_time": getattr(info, "on_time", 0),
                "overheated": getattr(info, "overheated", False),
                "nickname": getattr(info, "nickname", device_name),
                "ip": getattr(info, "ip", ""),
                "signal_level": getattr(info, "signal_level", 0),
                "rssi": getattr(info, "rssi", 0),
            }
        except Exception as e:
            logger.error(f"Erro ao obter info de {device_name}: {str(e)}")
            return None

    async def test_connection(self, ip_address: str) -> bool:
        """Testar conexão com um dispositivo"""
        try:
            client = await self._get_api_client()
            device = await client.p110(ip_address)
            await device.get_device_info()
            return True
        except Exception as e:
            logger.debug(f"Falha ao conectar em {ip_address}: {str(e)}")
            return False

    async def scan_network(self, network_prefix: str = "192.168.68") -> List[Dict]:
        """
        Escanear rede local para encontrar dispositivos TAPO

        Args:
            network_prefix: Prefixo da rede (ex: "192.168.1")

        Returns:
            Lista de dispositivos encontrados
        """
        logger.info(f"🔍 Escaneando rede {network_prefix}.0/24...")
        devices_found = []

        # Testar IPs de 1 a 254
        for i in range(1, 255):
            ip = f"{network_prefix}.{i}"

            if await self.test_connection(ip):
                try:
                    client = await self._get_api_client()
                    device = await client.p110(ip)
                    info = await device.get_device_info()

                    devices_found.append(
                        {
                            "ip": ip,
                            "name": getattr(info, "nickname", f"TAPO-{info.mac[-6:]}"),
                            "model": info.model,
                            "mac": info.mac,
                            "device_on": info.device_on,
                        }
                    )

                    logger.info(f"✅ Encontrado: {ip} - {info.model}")

                except Exception as e:
                    logger.debug(f"Erro ao obter info de {ip}: {str(e)}")

        logger.info(f"📡 Scan completo: {len(devices_found)} dispositivos encontrados")
        return devices_found
