"""
Cliente para integração com dispositivos Tuya (NovaDigital usa plataforma Tuya)
Baseado em tinytuya - biblioteca Python para dispositivos Tuya
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
try:
    import tinytuya
except ImportError:
    tinytuya = None

logger = logging.getLogger(__name__)


class TuyaClient:
    """Cliente para comunicação com dispositivos Tuya/NovaDigital"""
    
    def __init__(self, device_id: str = None, local_key: str = None, ip_address: str = None):
        """
        Inicializar cliente Tuya
        
        Args:
            device_id: ID do dispositivo Tuya
            local_key: Chave local do dispositivo
            ip_address: Endereço IP do dispositivo
        """
        self.device_id = device_id
        self.local_key = local_key
        self.ip_address = ip_address
        self.device = None
        
        if tinytuya and all([device_id, local_key, ip_address]):
            self.device = tinytuya.OutletDevice(device_id, ip_address, local_key)
            # Configurar versão 3.3 (mais comum para dispositivos modernos)
            self.device.set_version(3.3)
    
    async def test_connection(self) -> bool:
        """
        Testar conexão com dispositivo Tuya
        
        Returns:
            bool: True se conexão bem-sucedida
        """
        if not tinytuya:
            logger.error("Biblioteca tinytuya não instalada")
            return False
        
        if not all([self.device_id, self.local_key, self.ip_address]):
            logger.error("Parâmetros incompletos: device_id, local_key, ip_address")
            return False
        
        try:
            # Testar status
            data = await asyncio.get_event_loop().run_in_executor(
                None, self.device.status
            )
            
            if data and 'Error' not in str(data):
                logger.info(f"Conexão Tuya bem-sucedida com dispositivo {self.device_id}")
                return True
            else:
                logger.error(f"Erro na conexão Tuya: {data}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao testar conexão Tuya: {str(e)}")
            return False
    
    async def get_device_info(self) -> Optional[Dict]:
        """
        Obter informações do dispositivo
        
        Returns:
            Dict: Informações do dispositivo
        """
        if not self.device:
            return None
        
        try:
            data = await asyncio.get_event_loop().run_in_executor(
                None, self.device.status
            )
            
            if data and 'Error' not in str(data):
                return {
                    'device_id': self.device_id,
                    'ip_address': self.ip_address,
                    'status': data,
                    'timestamp': datetime.utcnow()
                }
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do dispositivo: {str(e)}")
            return None
    
    async def get_energy_usage(self) -> Optional[Dict]:
        """
        Obter dados de consumo de energia (se disponível)
        
        Returns:
            Dict: Dados de energia
        """
        if not self.device:
            return None
        
        try:
            # Para dispositivos com monitoramento de energia
            data = await asyncio.get_event_loop().run_in_executor(
                None, self.device.status
            )
            
            if data and 'Error' not in str(data):
                energy_data = {
                    'timestamp': datetime.utcnow(),
                    'device_id': self.device_id,
                    'power_watts': 0,
                    'voltage': 220.0,
                    'current': 0,
                    'energy_today_kwh': 0,
                    'energy_total_kwh': 0,
                    'data_source': 'tuya_local'
                }
                
                # Verificar DPS (Data Points) que podem conter dados de energia
                dps = data.get('dps', {})
                
                # DPS comuns para energia em dispositivos Tuya
                if '18' in dps:  # Potência atual em W
                    energy_data['power_watts'] = float(dps['18']) / 10  # Geralmente é valor *10
                
                if '19' in dps:  # Voltagem
                    energy_data['voltage'] = float(dps['19']) / 10
                
                if '20' in dps:  # Corrente
                    energy_data['current'] = float(dps['20']) / 1000
                
                if '17' in dps:  # Consumo hoje
                    energy_data['energy_today_kwh'] = float(dps['17']) / 100
                
                if '23' in dps:  # Consumo total
                    energy_data['energy_total_kwh'] = float(dps['23']) / 100
                
                # Status do dispositivo
                if '1' in dps:  # DPS 1 geralmente é o estado on/off
                    energy_data['device_on'] = dps['1'] == True
                
                return energy_data
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de energia: {str(e)}")
            return None
    
    async def turn_on(self) -> bool:
        """Ligar dispositivo"""
        if not self.device:
            return False
        
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.device.turn_on()
            )
            logger.info(f"Dispositivo {self.device_id} ligado")
            return True
        except Exception as e:
            logger.error(f"Erro ao ligar dispositivo: {str(e)}")
            return False
    
    async def turn_off(self) -> bool:
        """Desligar dispositivo"""
        if not self.device:
            return False
        
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.device.turn_off()
            )
            logger.info(f"Dispositivo {self.device_id} desligado")
            return True
        except Exception as e:
            logger.error(f"Erro ao desligar dispositivo: {str(e)}")
            return False
    
    async def send_command(self, command: Dict) -> Optional[Dict]:
        """
        Enviar comando personalizado para o dispositivo
        
        Args:
            command: Dicionário com comando DPS
            
        Returns:
            Dict: Resposta do dispositivo
        """
        if not self.device:
            return None
        
        try:
            payload = {
                'devId': self.device_id,
                'uid': '',
                't': int(datetime.now().timestamp())
            }
            payload.update(command)
            
            data = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.device.send_payload(payload)
            )
            
            return data
            
        except Exception as e:
            logger.error(f"Erro ao enviar comando: {str(e)}")
            return None
    
    @staticmethod
    async def discover_devices(ip_range: str = "192.168.1") -> List[Dict]:
        """
        Descobrir dispositivos Tuya na rede
        
        Args:
            ip_range: Range de IP para escanear
            
        Returns:
            List[Dict]: Lista de dispositivos encontrados
        """
        if not tinytuya:
            logger.error("Biblioteca tinytuya não instalada")
            return []
        
        try:
            devices = await asyncio.get_event_loop().run_in_executor(
                None, lambda: tinytuya.scan() or []
            )
            
            if devices:
                logger.info(f"Encontrados {len(devices)} dispositivos Tuya")
                return devices
            else:
                logger.info("Nenhum dispositivo Tuya encontrado")
                return []
            
        except Exception as e:
            logger.error(f"Erro ao descobrir dispositivos: {str(e)}")
            return []
    
    @staticmethod
    def get_install_instructions():
        """Retornar instruções de instalação e configuração"""
        return {
            'install': 'pip install tinytuya',
            'setup': [
                '1. Instale o app Tuya Smart',
                '2. Configure seu dispositivo NovaDigital no app',
                '3. Obtenha o Device ID, Local Key e IP:',
                '   - Use ferramentas como Tuya-Convert ou',
                '   - Extraia do app com ferramentas de depuração',
                '4. Configure no arquivo .env:',
                '   TUYA_DEVICE_ID=seu_device_id',
                '   TUYA_LOCAL_KEY=sua_local_key',
                '   TUYA_IP_ADDRESS=ip_do_dispositivo'
            ],
            'alternative': 'Use Tuya Cloud API para controle via nuvem'
        }
