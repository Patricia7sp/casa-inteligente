"""
Script para descobrir dispositivos TAPO reais via Cloud API
"""
import asyncio
import logging
from src.integrations.tapo_cloud_client import TapoCloudClient
from src.utils.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def discover_tapo_devices():
    """Descobrir dispositivos TAPO conectados à conta"""
    logger.info("🔍 Iniciando descoberta de dispositivos TAPO...")
    logger.info(f"📧 Usuário: {settings.tapo_username}")
    
    async with TapoCloudClient(settings.tapo_username, settings.tapo_password) as client:
        # Login na cloud
        if await client.login():
            logger.info("✅ Login bem-sucedido!")
            
            # Obter lista de dispositivos
            devices = await client.get_device_list()
            
            if devices:
                logger.info(f"\n📱 Encontrados {len(devices)} dispositivos:")
                for idx, device in enumerate(devices, 1):
                    logger.info(f"\n--- Dispositivo {idx} ---")
                    logger.info(f"  Nome: {device.get('alias', 'N/A')}")
                    logger.info(f"  Device ID: {device.get('deviceId', 'N/A')}")
                    logger.info(f"  Modelo: {device.get('deviceModel', 'N/A')}")
                    logger.info(f"  Tipo: {device.get('deviceType', 'N/A')}")
                    logger.info(f"  MAC: {device.get('deviceMac', 'N/A')}")
                    logger.info(f"  Status: {device.get('status', 'N/A')}")
                    
                    # Tentar obter informações detalhadas
                    device_id = device.get('deviceId')
                    if device_id:
                        info = await client.get_device_info(device_id)
                        if info:
                            logger.info(f"  Info adicional: {info}")
                        
                        # Tentar obter dados de energia
                        energy = await client.get_energy_usage(device_id)
                        if energy:
                            logger.info(f"  ⚡ Energia:")
                            logger.info(f"    Potência: {energy.get('power_watts', 0)}W")
                            logger.info(f"    Hoje: {energy.get('energy_today_kwh', 0)}kWh")
                            logger.info(f"    Total: {energy.get('energy_total_kwh', 0)}kWh")
                
                return devices
            else:
                logger.warning("⚠️  Nenhum dispositivo encontrado")
                return []
        else:
            logger.error("❌ Falha no login")
            return []


if __name__ == "__main__":
    asyncio.run(discover_tapo_devices())
