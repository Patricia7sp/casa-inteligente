"""
Agente coletor de dados de consumo de energia
"""

import asyncio
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict

from src.integrations.tapo_client import TapoClient
from src.utils.config import settings

logger = logging.getLogger(__name__)


class EnergyCollector:
    """Agente responsável por coletar dados de consumo de energia"""

    def __init__(self):
        self.tapo_client = TapoClient(
            username=settings.tapo_username, password=settings.tapo_password
        )
        self.running = False
        self.devices: List[Dict] = []

        # Configuração do Supabase
        self.supabase_url = getattr(
            settings,
            "supabase_url",
            "https://pqqrodiuuhckvdqawgeg.supabase.co",
        )
        self.supabase_key = getattr(
            settings,
            "supabase_anon_key",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxcXJvZGl1dWhja3ZkcWF3Z2VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0OTI0MTIsImV4cCI6MjA3ODA2ODQxMn0.ve7NIbFcZdTGa16O3Pttmpx2mxWgklvbPwwTSCHuDFs",
        )

    def _get_supabase_data(self, endpoint: str, params: dict = None) -> list:
        """Buscar dados do Supabase via REST API"""
        try:
            url = f"{self.supabase_url}/rest/v1/{endpoint}"
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json",
            }
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao buscar {endpoint}: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Erro ao conectar ao Supabase: {str(e)}")
            return []

    def _save_to_supabase(self, endpoint: str, data: dict) -> bool:
        """Salvar dados no Supabase via REST API"""
        try:
            url = f"{self.supabase_url}/rest/v1/{endpoint}"
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            }
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code in [200, 201]:
                return True
            else:
                logger.error(
                    f"Erro ao salvar em {endpoint}: {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Erro ao salvar no Supabase: {str(e)}")
            return False

    async def initialize(self):
        """Inicializar o coletor e carregar dispositivos do Supabase"""
        try:
            # Carregar dispositivos do Supabase
            self.devices = self._get_supabase_data("devices")

            # Filtrar apenas dispositivos ativos ou com is_active=None (TAPO)
            self.devices = [d for d in self.devices if d.get("is_active") is not False]

            # Adicionar dispositivos TAPO ao cliente
            for device in self.devices:
                if device.get("type", "").upper() == "TAPO":
                    ip_address = device.get("ip_address")
                    name = device.get("name")
                    if ip_address and name:
                        await self.tapo_client.add_device(ip_address, name)

            logger.info(
                f"Coletor inicializado com {len(self.devices)} dispositivos do Supabase"
            )

        except Exception as e:
            logger.error(f"Erro ao inicializar coletor: {str(e)}")

    async def collect_device_data(self, device: Dict) -> bool:
        """
        Coletar dados de um dispositivo específico e salvar no Supabase

        Args:
            device: Dicionário com dados do dispositivo

        Returns:
            bool: True se coletado com sucesso
        """
        try:
            device_type = device.get("type", "").upper()
            device_name = device.get("name", "Unknown")
            device_id = device.get("id")

            if device_type == "TAPO":
                data = await self.tapo_client.get_energy_usage(device_name)

                if data:
                    # Preparar dados para salvar no Supabase
                    reading_data = {
                        "device_id": device_id,
                        "timestamp": (
                            data["timestamp"].isoformat()
                            if isinstance(data["timestamp"], datetime)
                            else data["timestamp"]
                        ),
                        "power_watts": float(data["power_watts"]),
                        "voltage": float(data.get("voltage", 0)),
                        "current": float(data.get("current", 0)),
                        "energy_kwh": float(data.get("energy_today_kwh", 0)),
                    }

                    # Salvar no Supabase
                    success = self._save_to_supabase("energy_readings", reading_data)

                    if success:
                        logger.info(
                            f"✅ Dados coletados e salvos no Supabase - {device_name}: {data['power_watts']:.2f}W"
                        )
                        return True
                    else:
                        logger.error(
                            f"❌ Falha ao salvar dados no Supabase - {device_name}"
                        )
                        return False
                else:
                    logger.warning(
                        f"⚠️ Não foi possível obter dados do dispositivo {device_name}"
                    )
                    return False

            else:
                logger.warning(f"⚠️ Tipo de dispositivo não suportado: {device_type}")
                return False

        except Exception as e:
            logger.error(
                f"❌ Erro ao coletar dados do dispositivo {device.get('name', 'Unknown')}: {str(e)}"
            )
            return False

    async def collect_all_devices(self) -> Dict[str, bool]:
        """
        Coletar dados de todos os dispositivos

        Returns:
            Dict com resultados por dispositivo
        """
        results = {}

        for device in self.devices:
            device_name = device.get("name", "Unknown")
            results[device_name] = await self.collect_device_data(device)

        return results

    async def start_collection(self):
        """Iniciar coleta contínua de dados"""
        self.running = True
        logger.info("Iniciando coleta contínua de dados")

        while self.running:
            try:
                start_time = datetime.utcnow()

                # Coletar dados de todos os dispositivos
                results = await self.collect_all_devices()

                # Calcular tempo de execução
                execution_time = (datetime.utcnow() - start_time).total_seconds()

                # Log de resultados
                success_count = sum(1 for success in results.values() if success)
                logger.info(
                    f"Coleta concluída: {success_count}/{len(results)} dispositivos bem-sucedidos em {execution_time:.2f}s"
                )

                # Esperar pelo próximo intervalo
                wait_time = settings.collection_interval_minutes * 60
                await asyncio.sleep(wait_time)

            except Exception as e:
                logger.error(f"Erro na coleta contínua: {str(e)}")
                await asyncio.sleep(60)  # Esperar 1 minuto antes de tentar novamente

    def stop_collection(self):
        """Parar coleta contínua de dados"""
        self.running = False
        logger.info("Coleta contínua de dados parada")

    async def get_current_status(self) -> Dict:
        """Obter status atual de todos os dispositivos"""
        status = {}

        for device in self.devices:
            device_name = device.get("name", "Unknown")
            device_type = device.get("type", "").upper()

            try:
                if device_type == "TAPO":
                    device_info = await self.tapo_client.get_device_info(device_name)
                    status[device_name] = {
                        "device_id": device.get("id"),
                        "ip_address": device.get("ip_address"),
                        "location": device.get("location"),
                        "equipment": device.get("equipment_connected"),
                        "is_online": device_info is not None,
                        "is_on": (
                            device_info.get("device_on", False)
                            if device_info
                            else False
                        ),
                    }
                else:
                    status[device_name] = {
                        "device_id": device.get("id"),
                        "ip_address": device.get("ip_address"),
                        "location": device.get("location"),
                        "equipment": device.get("equipment_connected"),
                        "is_online": False,
                        "is_on": False,
                    }
            except Exception as e:
                logger.error(
                    f"Erro ao obter status do dispositivo {device_name}: {str(e)}"
                )
                status[device_name] = {
                    "device_id": device.get("id"),
                    "ip_address": device.get("ip_address"),
                    "location": device.get("location"),
                    "equipment": device.get("equipment_connected"),
                    "is_online": False,
                    "is_on": False,
                }

        return status


# Instância global do coletor
collector = EnergyCollector()
