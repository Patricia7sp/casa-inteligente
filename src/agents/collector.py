"""
Agente coletor de dados de consumo de energia
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session

from src.integrations.tapo_client import TapoClient
from src.models.database import Device, EnergyReading, get_db
from src.utils.config import settings

logger = logging.getLogger(__name__)


class EnergyCollector:
    """Agente responsável por coletar dados de consumo de energia"""
    
    def __init__(self):
        self.tapo_client = TapoClient(
            username=settings.tapo_username,
            password=settings.tapo_password
        )
        self.running = False
        self.devices: List[Device] = []
    
    async def initialize(self):
        """Inicializar o coletor e carregar dispositivos"""
        try:
            # Carregar dispositivos do banco de dados
            db = next(get_db())
            self.devices = db.query(Device).filter(Device.is_active == True).all()
            db.close()
            
            # Adicionar dispositivos ao cliente TAPO
            for device in self.devices:
                if device.type.upper() == "TAPO":
                    await self.tapo_client.add_device(device.ip_address, device.name)
            
            logger.info(f"Coletor inicializado com {len(self.devices)} dispositivos")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar coletor: {str(e)}")
    
    async def collect_device_data(self, device: Device) -> bool:
        """
        Coletar dados de um dispositivo específico
        
        Args:
            device: Dispositivo para coletar dados
            
        Returns:
            bool: True se coletado com sucesso
        """
        try:
            if device.type.upper() == "TAPO":
                data = await self.tapo_client.get_energy_usage(device.name)
                
                if data:
                    # Salvar no banco de dados
                    db = next(get_db())
                    
                    reading = EnergyReading(
                        device_id=device.id,
                        timestamp=data["timestamp"],
                        power_watts=data["power_watts"],
                        voltage=data["voltage"],
                        current=data["current"],
                        energy_today_kwh=data["energy_today_kwh"],
                        energy_total_kwh=data["energy_total_kwh"]
                    )
                    
                    db.add(reading)
                    db.commit()
                    db.close()
                    
                    logger.info(f"Dados coletados do dispositivo {device.name}: {data['power_watts']:.2f}W")
                    return True
                else:
                    logger.warning(f"Não foi possível obter dados do dispositivo {device.name}")
                    return False
                    
            else:
                logger.warning(f"Tipo de dispositivo não suportado: {device.type}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao coletar dados do dispositivo {device.name}: {str(e)}")
            return False
    
    async def collect_all_devices(self) -> Dict[str, bool]:
        """
        Coletar dados de todos os dispositivos
        
        Returns:
            Dict com resultados por dispositivo
        """
        results = {}
        
        for device in self.devices:
            results[device.name] = await self.collect_device_data(device)
        
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
                logger.info(f"Coleta concluída: {success_count}/{len(results)} dispositivos bem-sucedidos em {execution_time:.2f}s")
                
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
            try:
                if device.type.upper() == "TAPO":
                    device_info = await self.tapo_client.get_device_info(device.name)
                    status[device.name] = {
                        "device_id": device.id,
                        "ip_address": device.ip_address,
                        "location": device.location,
                        "equipment": device.equipment_connected,
                        "is_online": device_info is not None,
                        "is_on": device_info.get("device_on", False) if device_info else False
                    }
                else:
                    status[device.name] = {
                        "device_id": device.id,
                        "ip_address": device.ip_address,
                        "location": device.location,
                        "equipment": device.equipment_connected,
                        "is_online": False,
                        "is_on": False
                    }
            except Exception as e:
                logger.error(f"Erro ao obter status do dispositivo {device.name}: {str(e)}")
                status[device.name] = {
                    "device_id": device.id,
                    "ip_address": device.ip_address,
                    "location": device.location,
                    "equipment": device.equipment_connected,
                    "is_online": False,
                    "is_on": False
                }
        
        return status


# Instância global do coletor
collector = EnergyCollector()
