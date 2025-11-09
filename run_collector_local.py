#!/usr/bin/env python3
"""
Serviço de coleta LOCAL - Roda na sua máquina para coletar dados dos dispositivos TAPO
e enviar para o Supabase.

Este serviço deve rodar continuamente na sua máquina local, pois os dispositivos TAPO
estão na sua rede doméstica e não são acessíveis pelo Cloud Run.

USO:
    python run_collector_local.py

O serviço vai:
1. Conectar aos dispositivos TAPO na sua rede local
2. Coletar dados de energia a cada 15 minutos
3. Salvar os dados no Supabase
4. A API no Cloud Run vai ler esses dados do Supabase
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.collector import EnergyCollector
from src.utils.config import settings
from src.utils.logger import setup_logging

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)


async def main():
    """Executar coletor local continuamente"""
    logger.info("=" * 80)
    logger.info("🏠 COLETOR LOCAL - Casa Inteligente")
    logger.info("=" * 80)
    logger.info("")
    logger.info("📡 Este serviço coleta dados dos dispositivos TAPO na sua rede local")
    logger.info("💾 Os dados são salvos no Supabase em tempo real")
    logger.info("🌐 A API no Cloud Run acessa esses dados do Supabase")
    logger.info("")
    logger.info(f"⏱️  Intervalo de coleta: {settings.collection_interval_minutes} minutos")
    logger.info(f"🔑 Usuário TAPO: {settings.tapo_username}")
    logger.info(f"🗄️  Supabase URL: {settings.supabase_url}")
    logger.info("")
    logger.info("=" * 80)
    logger.info("")
    
    # Inicializar coletor
    collector = EnergyCollector()
    
    try:
        logger.info("🔄 Inicializando coletor...")
        await collector.initialize()
        logger.info("✅ Coletor inicializado com sucesso!")
        logger.info("")
        logger.info("🚀 Iniciando coleta contínua...")
        logger.info("   (Pressione Ctrl+C para parar)")
        logger.info("")
        
        # Iniciar coleta contínua
        await collector.start_collection()
        
    except KeyboardInterrupt:
        logger.info("")
        logger.info("⏹️  Parando coletor...")
        logger.info("👋 Coletor finalizado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal no coletor: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Até logo!")
