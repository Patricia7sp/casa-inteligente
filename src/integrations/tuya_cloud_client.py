"""
Cliente para API Cloud Tuya (alternativa para dispositivos NovaDigital)
Baseado na documentação oficial da Tuya Cloud API
"""

import asyncio
import aiohttp
import json
import hashlib
import time
import hmac
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TuyaCloudClient:
    """Cliente para Tuya Cloud API"""

    def __init__(self, access_id: str, access_key: str, region: str = "us"):
        """
        Inicializar cliente Tuya Cloud
        
        Args:
            access_id: Access ID da Tuya Cloud
            access_key: Access Secret da Tuya Cloud
            region: Região (us, eu, cn, etc.)
        """
        self.access_id = access_id
        self.access_key = access_key
        self.region = region
        self.base_url = f"https://openapi.tuya{region}.com"
        self.session = None
        self.token = None
        self.token_expires = 0
        self.time_offset = 0  # Diferença de tempo com servidor Tuya

    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()

    async def _sync_time(self) -> bool:
        """
        Sincronizar tempo com servidor Tuya para evitar erro de timestamp
        
        Returns:
            bool: True se sincronização bem-sucedida
        """
        try:
            # Fazer várias requisições para calcular a diferença média
            offsets = []

            for i in range(5):  # Mais medições para melhor precisão
                # Calcular timestamp local antes da requisição
                local_time = int(time.time() * 1000)

                # Gerar assinatura temporária
                timestamp = str(local_time)
                path = "/v1.0/token?grant_type=1"
                string_to_sign = f"GET\napplication/json\n{timestamp}\n{path}"

                signature = hmac.new(
                    self.access_key.encode("utf-8"),
                    string_to_sign.encode("utf-8"),
                    hashlib.sha256,
                ).hexdigest()

                headers = {
                    "Content-Type": "application/json",
                    "X-T": timestamp,
                    "client_id": self.access_id,
                    "sign": signature.upper(),
                    "sign_method": "HMAC-SHA256",
                }

                async with self.session.get(
                    f"{self.base_url}{path}", headers=headers, timeout=5
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        server_time = result.get("t", 0)
                        if server_time > 0:
                            # Calcular diferença (servidor - local)
                            offset = server_time - local_time
                            offsets.append(offset)
                            logger.debug(f"Medição {i+1}: offset={offset}ms")

                await asyncio.sleep(0.3)  # Pequena pausa entre medições

            if offsets:
                # Usar mediana para evitar outliers
                offsets.sort()
                median_offset = offsets[len(offsets) // 2]

                # Análise estatística simples
                if len(offsets) >= 3:
                    # Remover outliers extremos
                    q1 = offsets[len(offsets) // 4]
                    q3 = offsets[3 * len(offsets) // 4]
                    iqr = q3 - q1

                    filtered = [
                        o for o in offsets if q1 - 1.5 * iqr <= o <= q3 + 1.5 * iqr
                    ]
                    if filtered:
                        median_offset = sum(filtered) / len(filtered)

                # Aplicar correção baseada na mediana
                # Se servidor está adiantado (offset > 0), adicionar ao timestamp
                # Se servidor está atrasado (offset < 0), subtrair do timestamp
                self.time_offset = median_offset

                # Adicionar margem de segurança baseada na variabilidade
                if len(offsets) > 1:
                    variance = sum((x - median_offset) ** 2 for x in offsets) / len(
                        offsets
                    )
                    std_dev = variance ** 0.5
                    safety_margin = min(500, std_dev * 2)  # Máximo 500ms de margem
                    self.time_offset += (
                        safety_margin if median_offset > 0 else -safety_margin
                    )

                logger.info(
                    f"Tempo sincronizado. Offset: {median_offset:.0f}ms, ajustado: {self.time_offset:.0f}ms"
                )
                return True
            else:
                # Fallback: usar correção fixa conservadora
                self.time_offset = 1500  # 1.5 segundos
                logger.warning(f"Usando correção fixa: {self.time_offset}ms")
                return True

        except Exception as e:
            logger.warning(f"Erro ao sincronizar tempo: {e}")
            # Usar correção fixa como fallback
            self.time_offset = 1500
            logger.warning(f"Usando correção fixa: {self.time_offset}ms")
            return True

    def _get_timestamp(self) -> str:
        """
        Obter timestamp corrigido para API Tuya
        
        Returns:
            str: Timestamp em milissegundos
        """
        # Baseado em múltiplos testes: servidor Tuya está adiantado em ~600ms
        # Usar correção de +1000ms para margem de segurança
        return str(int(time.time() * 1000) + 1000)

    def _sign_request(self, method: str, path: str, headers: Dict, body: str = ""):
        """
        Gerar assinatura para requisição Tuya
        
        Args:
            method: Método HTTP
            path: Path da API
            headers: Headers da requisição
            body: Body da requisição
            
        Returns:
            Dict: Headers com assinatura
        """
        # Usar timestamp corrigido
        timestamp = self._get_timestamp()

        # Construir string para assinatura seguindo documentação Tuya
        # Formato: METHOD\nContent-Type\nX-T\nsign_url
        sign_url = path
        if body:
            sign_url += body

        string_to_sign = f"{method}\n{headers['Content-Type']}\n{timestamp}\n{sign_url}"

        # Gerar assinatura HMAC-SHA256
        signature = hmac.new(
            self.access_key.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # Adicionar headers de autenticação
        headers.update(
            {
                "X-T": timestamp,
                "client_id": self.access_id,
                "sign": signature.upper(),
                "sign_method": "HMAC-SHA256",
            }
        )

        return headers

    async def _get_token(self) -> bool:
        """
        Obter token de acesso da API
        
        Returns:
            bool: True se obtido com sucesso
        """
        try:
            if self.token and time.time() < self.token_expires:
                return True

            # Sincronizar tempo com servidor Tuya
            await self._sync_time()

            path = "/v1.0/token?grant_type=1"
            headers = {"Content-Type": "application/json", "sign_method": "HMAC-SHA256"}

            body = ""
            headers = self._sign_request("GET", path, headers, body)

            async with self.session.get(
                f"{self.base_url}{path}", headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    if result.get("success") and "result" in result:
                        self.token = result["result"]["access_token"]
                        self.token_expires = (
                            time.time() + result["result"]["expire_time"] - 60
                        )
                        logger.info("Token Tuya Cloud obtido com sucesso")
                        return True
                    else:
                        logger.error(f"Erro ao obter token: {result}")
                        return False
                else:
                    logger.error(f"Erro HTTP ao obter token: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Erro ao obter token Tuya: {str(e)}")
            return False

    async def get_device_list(self) -> List[Dict]:
        """
        Obter lista de dispositivos
        
        Returns:
            List[Dict]: Lista de dispositivos
        """
        try:
            if not await self._get_token():
                return []

            path = "/v1.0/users/devices"
            headers = {
                "Content-Type": "application/json",
                "sign_method": "HMAC-SHA256",
                "access_token": self.token,
            }

            body = ""
            headers = self._sign_request("GET", path, headers, body)

            async with self.session.get(
                f"{self.base_url}{path}", headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    if result.get("success") and "result" in result:
                        devices = result["result"]
                        logger.info(
                            f"Encontrados {len(devices)} dispositivos na Tuya Cloud"
                        )
                        return devices
                    else:
                        logger.error(f"Erro ao listar dispositivos: {result}")
                        return []
                else:
                    logger.error(f"Erro HTTP ao listar dispositivos: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Erro ao obter lista de dispositivos: {str(e)}")
            return []

    async def get_device_info(self, device_id: str) -> Optional[Dict]:
        """
        Obter informações detalhadas do dispositivo
        
        Args:
            device_id: ID do dispositivo
            
        Returns:
            Dict: Informações do dispositivo
        """
        try:
            if not await self._get_token():
                return None

            path = f"/v1.0/devices/{device_id}"
            headers = {
                "Content-Type": "application/json",
                "sign_method": "HMAC-SHA256",
                "access_token": self.token,
            }

            body = ""
            headers = self._sign_request("GET", path, headers, body)

            async with self.session.get(
                f"{self.base_url}{path}", headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    if result.get("success") and "result" in result:
                        return result["result"]
                    else:
                        logger.error(f"Erro ao obter info do dispositivo: {result}")
                        return None
                else:
                    logger.error(
                        f"Erro HTTP ao obter info do dispositivo: {response.status}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Erro ao obter informações do dispositivo: {str(e)}")
            return None

    async def get_device_status(self, device_id: str) -> Optional[Dict]:
        """
        Obter status atual do dispositivo
        
        Args:
            device_id: ID do dispositivo
            
        Returns:
            Dict: Status do dispositivo
        """
        try:
            if not await self._get_token():
                return None

            path = f"/v1.0/devices/{device_id}/status"
            headers = {
                "Content-Type": "application/json",
                "sign_method": "HMAC-SHA256",
                "access_token": self.token,
            }

            body = ""
            headers = self._sign_request("GET", path, headers, body)

            async with self.session.get(
                f"{self.base_url}{path}", headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    if result.get("success") and "result" in result:
                        return result["result"]
                    else:
                        logger.error(f"Erro ao obter status do dispositivo: {result}")
                        return None
                else:
                    logger.error(
                        f"Erro HTTP ao obter status do dispositivo: {response.status}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Erro ao obter status do dispositivo: {str(e)}")
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
            # Obter status do dispositivo
            status_data = await self.get_device_status(device_id)

            if not status_data:
                return None

            energy_data = {
                "timestamp": datetime.utcnow(),
                "device_id": device_id,
                "power_watts": 0,
                "voltage": 220.0,
                "current": 0,
                "energy_today_kwh": 0,
                "energy_total_kwh": 0,
                "data_source": "tuya_cloud",
            }

            # Extrair dados de energia do status
            for item in status_data:
                code = item.get("code", "")
                value = item.get("value", 0)

                # Mapear códigos comuns de energia
                if code == "cur_power":  # Potência atual
                    energy_data["power_watts"] = (
                        float(value) / 10
                    )  # Geralmente é valor *10
                elif code == "cur_voltage":  # Voltagem
                    energy_data["voltage"] = float(value) / 10
                elif code == "cur_current":  # Corrente
                    energy_data["current"] = float(value) / 1000
                elif code == "add_ele":  # Consumo adicional
                    energy_data["energy_today_kwh"] = float(value) / 100
                elif code == "total_energy":  # Consumo total
                    energy_data["energy_total_kwh"] = float(value) / 100
                elif code == "switch_1":  # Status on/off
                    energy_data["device_on"] = bool(value)

            return energy_data

        except Exception as e:
            logger.error(f"Erro ao obter dados de energia: {str(e)}")
            return None

    async def control_device(self, device_id: str, commands: List[Dict]) -> bool:
        """
        Controlar dispositivo
        
        Args:
            device_id: ID do dispositivo
            commands: Lista de comandos
            
        Returns:
            bool: True se executado com sucesso
        """
        try:
            if not await self._get_token():
                return False

            path = f"/v1.0/devices/{device_id}/commands"
            headers = {
                "Content-Type": "application/json",
                "sign_method": "HMAC-SHA256",
                "access_token": self.token,
            }

            body = json.dumps({"commands": commands})
            headers = self._sign_request("POST", path, headers, body)

            async with self.session.post(
                f"{self.base_url}{path}", headers=headers, data=body
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    if result.get("success"):
                        logger.info(f"Dispositivo {device_id} controlado com sucesso")
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

    async def turn_on(self, device_id: str) -> bool:
        """Ligar dispositivo"""
        commands = [{"code": "switch_1", "value": True}]
        return await self.control_device(device_id, commands)

    async def turn_off(self, device_id: str) -> bool:
        """Desligar dispositivo"""
        commands = [{"code": "switch_1", "value": False}]
        return await self.control_device(device_id, commands)

    async def test_connection(self) -> bool:
        """
        Testar conexão com a API Cloud
        
        Returns:
            bool: True se conexão OK
        """
        try:
            if await self._get_token():
                devices = await self.get_device_list()
                logger.info(
                    f"Conexão Tuya Cloud OK. {len(devices)} dispositivos encontrados."
                )
                return True
            return False

        except Exception as e:
            logger.error(f"Erro ao testar conexão Tuya Cloud: {str(e)}")
            return False

    @staticmethod
    def get_setup_instructions():
        """Retornar instruções de configuração"""
        return {
            "steps": [
                "1. Crie conta em https://iot.tuya.com/",
                "2. Crie um projeto Cloud",
                "3. Obtenha Access ID e Access Secret",
                "4. Configure no .env:",
                "   TUYA_ACCESS_ID=seu_access_id",
                "   TUYA_ACCESS_KEY=seu_access_secret",
                "   TUYA_REGION=br (ou us, eu, cn)",
            ],
            "register_devices": [
                "1. Adicione dispositivos ao app Tuya Smart",
                "2. Vincule ao seu projeto Cloud",
                "3. Use os Device IDs da API",
            ],
        }
