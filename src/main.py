"""
Aplicação principal - Casa Inteligente API
"""

import asyncio
import logging
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.integrations.tapo_client import TapoClient
from src.integrations.nova_digital_client import NovaDigitalClient, DeviceClientFactory
from src.agents.collector import EnergyCollector
from src.services.energy_service import (
    energy_service,
    get_device_weekly_consumption,
    get_device_monthly_stats,
    get_devices_ranking,
    fetch_tapo_devices_and_readings,
    build_energy_overview,
    build_power_history,
    build_daily_totals,
    build_monthly_totals,
    build_projections,
    build_device_detail,
    load_smartlife_snapshot,
)
from src.services.supabase_client import get_supabase_data, save_to_supabase

try:
    from src.services.notification_service import notification_service
except Exception as notification_import_error:
    notification_service = None  # notifications optional
    logging.getLogger(__name__).warning(
        "Serviço de notificação não está disponível: %s",
        notification_import_error,
    )
from src.services.llm_service import llm_service
from src.utils.config import settings
from src.utils.logger import setup_logging

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# Configuração do Supabase e helpers de acesso movidos para
# src/services/supabase_client.py (get_supabase_data / save_to_supabase
# importados no topo deste arquivo) para eliminar duplicação com
# src/services/energy_service.py.


# Inicializar coletor
collector = EnergyCollector()

# Variável global para o coletor
collector_task: Optional[asyncio.Task] = None


async def launch_collector_background() -> None:
    """Inicializar e iniciar coleta contínua em background."""
    try:
        logger.info("Iniciando coletor em background...")
        await asyncio.wait_for(
            collector.initialize(),
            timeout=settings.collector_init_timeout_seconds,
        )
        logger.info("✅ Coletor inicializado com sucesso")
        await collector.start_collection()
    except asyncio.TimeoutError:
        logger.warning(
            "⏱️ Timeout ao inicializar coletor (%ss). Dispositivos podem estar inacessíveis. Continuando sem coleta.",
            settings.collector_init_timeout_seconds,
        )
    except asyncio.CancelledError:
        logger.info("Tarefa do coletor cancelada durante shutdown")
        raise
    except Exception as e:
        logger.warning(f"⚠️ Erro ao iniciar coletor (continuando sem coleta): {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    # Startup
    logger.info("Iniciando Casa Inteligente API...")

    # NOTA: PostgreSQL local removido - usando apenas Supabase
    logger.info("Sistema configurado para usar Supabase como banco de dados principal")

    global collector_task
    if settings.enable_collector:
        logger.info("Coletor habilitado - iniciando tarefa em background")
        collector_task = asyncio.create_task(launch_collector_background())
    else:
        logger.warning(
            "Coletor desabilitado por configuração (ENABLE_COLLECTOR=false). "
            "Aplicação operando apenas com dados existentes no Supabase."
        )

    # Enviar notificação de sistema online
    if notification_service:
        asyncio.create_task(
            notification_service.send_system_notification(
                "🟢 Sistema Casa Inteligente iniciado com sucesso!", "INFO"
            )
        )

    yield

    # Shutdown
    logger.info("Desligando Casa Inteligente API...")

    # Parar coletor
    if collector_task and not collector_task.done():
        collector.stop_collection()
        collector_task.cancel()
        try:
            await collector_task
        except asyncio.CancelledError:
            pass

    # Enviar notificação de sistema offline
    if notification_service:
        asyncio.create_task(
            notification_service.send_system_notification(
                "🔴 Sistema Casa Inteligente desligado", "WARNING"
            )
        )


# Criar aplicação FastAPI
app = FastAPI(
    title="Casa Inteligente API",
    description="API para monitoramento inteligente de consumo de energia residencial",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoints da API
@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Casa Inteligente API",
        "version": "1.0.0",
        "status": "online",
        "timestamp": datetime.utcnow(),
    }


@app.get("/health")
async def health_check():
    """Verificar saúde da API - resposta rápida para Cloud Run"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "collector_enabled": settings.enable_collector,
        "collector_running": collector.running if settings.enable_collector else False,
    }


@app.get("/devices")
async def get_devices():
    """Obter todos os dispositivos cadastrados do Supabase"""
    try:
        devices = get_supabase_data("devices")

        # Filtrar apenas dispositivos ativos
        active_devices = [d for d in devices if d.get("is_active") is not False]

        return {"devices": active_devices, "count": len(active_devices)}

    except Exception as e:
        logger.error(f"Erro ao obter dispositivos: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter dispositivos")


# NOTA: Endpoint temporariamente desabilitado - migração para Supabase
# @app.post("/devices")
# async def add_device(device_data: Dict, background_tasks: BackgroundTasks):
#     """Adicionar novo dispositivo"""
#     # TODO: Reimplementar usando Supabase REST API
#     raise HTTPException(status_code=501, detail="Endpoint em manutenção - use o Supabase diretamente")


# NOTA: Endpoint temporariamente desabilitado - migração para Supabase
# @app.get("/devices/{device_id}/status")
# async def get_device_status(device_id: int):
#     # TODO: Reimplementar usando Supabase REST API
#     pass


@app.get("/status/realtime")
async def get_realtime_status():
    """Obter status em tempo real de todos os dispositivos"""
    try:
        status = energy_service.get_realtime_status()
        return status
    except Exception as e:
        logger.error(f"Erro ao obter status em tempo real: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Erro ao obter status em tempo real"
        )


@app.get("/reports/daily")
async def get_daily_report(date: str = None):
    """Obter relatório diário"""
    try:
        if date:
            report_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            report_date = datetime.utcnow()

        report = energy_service.generate_daily_report(report_date)
        return report

    except ValueError:
        raise HTTPException(
            status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD"
        )
    except Exception as e:
        logger.error(f"Erro ao gerar relatório diário: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao gerar relatório diário")


@app.post("/reports/daily/send")
async def send_daily_report(background_tasks: BackgroundTasks, date: str = None):
    """Enviar relatório diário via notificações"""
    try:
        if date:
            report_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            report_date = datetime.utcnow()

        # Gerar relatório
        report = energy_service.generate_daily_report(report_date)

        if "error" in report:
            raise HTTPException(status_code=500, detail=report["error"])

        # Enviar em background
        background_tasks.add_task(notification_service.send_daily_report, report)

        return {"message": "Relatório sendo enviado", "report_data": report}

    except ValueError:
        raise HTTPException(
            status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao enviar relatório diário: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao enviar relatório diário")


@app.get("/devices/{device_id}/trends")
async def get_device_trends(device_id: int, days: int = 30):
    """Obter tendências de consumo de um dispositivo"""
    try:
        trends = energy_service.get_consumption_trends(device_id, days)

        if trends is None:
            raise HTTPException(
                status_code=404, detail="Nenhum dado encontrado para este dispositivo"
            )

        return trends

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter tendências: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter tendências")


# NOTA: Endpoint temporariamente desabilitado - migração para Supabase
# @app.post("/devices/{device_id}/control")
# async def control_device(device_id: int, action: str, background_tasks: BackgroundTasks):
#     # TODO: Reimplementar usando Supabase REST API
#     pass


@app.post("/devices/{device_id}/control")
async def control_device(
    device_id: int, action: str, background_tasks: BackgroundTasks
):
    """Controlar dispositivo (ligar/desligar)"""
    try:
        # Buscar dispositivo do Supabase
        devices = get_supabase_data("devices", params={"id": f"eq.{device_id}"})

        if not devices:
            raise HTTPException(status_code=404, detail="Dispositivo não encontrado")

        device = devices[0]

        if device.get("type", "").upper() != "TAPO":
            raise HTTPException(
                status_code=400,
                detail="Controle não disponível para este tipo de dispositivo",
            )

        device_name = device.get("name")

        # Executar ação em background
        if action.lower() == "on":
            background_tasks.add_task(collector.tapo_client.turn_on, device_name)
            message = f"Comando de ligar enviado para {device_name}"
        elif action.lower() == "off":
            background_tasks.add_task(collector.tapo_client.turn_off, device_name)
            message = f"Comando de desligar enviado para {device_name}"
        else:
            raise HTTPException(
                status_code=400, detail="Ação inválida. Use 'on' ou 'off'"
            )

        return {"message": message}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao controlar dispositivo: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao controlar dispositivo")


@app.post("/notifications/test")
async def test_notifications():
    """Testar configurações de notificação"""
    try:
        results = notification_service.test_notifications()
        return {"test_results": results}
    except Exception as e:
        logger.error(f"Erro ao testar notificações: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao testar notificações")


# Endpoints do LLM
@app.post("/ai/ask")
async def ask_ai_assistant(question_data: Dict):
    """
    Fazer pergunta ao assistente inteligente LLM

    Args:
        question_data: {"question": "sua pergunta", "provider": "openai|gemini|auto"}

    Returns:
        Resposta do assistente com contexto do sistema
    """
    try:
        question = question_data.get("question", "")
        provider = question_data.get("provider", "auto")

        if not question:
            raise HTTPException(status_code=400, detail="Pergunta não fornecida")

        response = await llm_service.ask_question(question, provider)

        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar pergunta LLM: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar pergunta")


@app.get("/ai/insights")
async def get_energy_insights(days: int = 7):
    """
    Obter insights automáticos sobre consumo de energia

    Args:
        days: Número de dias para análise (padrão: 7)

    Returns:
        Insights e recomendações automáticas
    """
    try:
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=400, detail="Período deve estar entre 1 e 365 dias"
            )

        insights = llm_service.get_energy_insights(days)

        if "error" in insights:
            raise HTTPException(status_code=500, detail=insights["error"])

        return insights

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao gerar insights")


@app.get("/ai/context")
async def get_ai_context():
    """
    Obter contexto atual do sistema para o LLM

    Returns:
        Contexto completo do sistema
    """
    try:
        context = llm_service.get_system_context()
        return {"context": context, "timestamp": datetime.utcnow()}

    except Exception as e:
        logger.error(f"Erro ao obter contexto LLM: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter contexto")


@app.post("/ai/recommendations")
async def get_personalized_recommendations(device_data: Dict):
    """
    Obter recomendações personalizadas para um dispositivo específico

    Args:
        device_data: {"device_id": 1, "days": 30}

    Returns:
        Recomendações personalizadas
    """
    try:
        device_id = device_data.get("device_id")
        days = device_data.get("days", 30)

        if not device_id:
            raise HTTPException(
                status_code=400, detail="ID do dispositivo não fornecido"
            )

        # Obter informações do dispositivo do Supabase
        devices = get_supabase_data("devices", params={"id": f"eq.{device_id}"})

        if not devices:
            raise HTTPException(status_code=404, detail="Dispositivo não encontrado")

        device = devices[0]

        # Obter tendências do dispositivo
        trends = energy_service.get_consumption_trends(device_id, days)

        if not trends:
            raise HTTPException(
                status_code=404, detail="Nenhum dado encontrado para este dispositivo"
            )

        # Gerar recomendações personalizadas
        question = f"""
Baseado nos dados do dispositivo '{device.get('name')}' ({device.get('location')}) nos últimos {days} dias:
- Consumo total: {trends['total_energy_kwh']:.3f} kWh
- Custo total: R$ {trends['total_cost']:.2f}
- Média diária: {trends['average_daily_energy_kwh']:.3f} kWh
- Pico: {trends['max_daily_energy_kwh']:.3f} kWh

Forneça recomendações específicas para otimizar o consumo deste dispositivo.
"""

        response = await llm_service.ask_question(question, "auto")

        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])

        return {
            "device_info": {
                "name": device.get("name"),
                "location": device.get("location"),
                "equipment": device.get("equipment_connected"),
            },
            "trends": trends,
            "recommendations": response["response"],
            "generated_at": datetime.utcnow(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar recomendações: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao gerar recomendações")


# Endpoints de Histórico e Estatísticas
@app.get("/devices/{device_id}/weekly")
async def get_device_weekly(device_id: int, weeks: int = 1):
    """Obter consumo semanal de um dispositivo"""
    try:
        data = get_device_weekly_consumption(device_id, weeks)
        if not data:
            raise HTTPException(
                status_code=404, detail="Nenhum dado encontrado para este dispositivo"
            )
        return {"device_id": device_id, "weeks": weeks, "data": data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter consumo semanal: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter consumo semanal")


@app.get("/devices/{device_id}/monthly")
async def get_device_monthly(device_id: int):
    """Obter estatísticas mensais de um dispositivo"""
    try:
        data = get_device_monthly_stats(device_id)
        if not data:
            raise HTTPException(
                status_code=404, detail="Nenhum dado encontrado para este dispositivo"
            )
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas mensais: {e}")
        raise HTTPException(
            status_code=500, detail="Erro ao obter estatísticas mensais"
        )


@app.get("/devices/ranking")
async def get_ranking(period_days: int = 30):
    """Obter ranking de dispositivos por consumo"""
    try:
        data = get_devices_ranking(period_days)
        if not data:
            raise HTTPException(
                status_code=404, detail="Nenhum dado disponível para ranking"
            )
        return {"period_days": period_days, "ranking": data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter ranking: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter ranking")


# Endpoints de Teste de Conexão
@app.post("/devices/test-connection")
async def test_device_connection(connection_data: Dict):
    """
    Testar conexão com dispositivo antes de adicionar

    Args:
        connection_data: {
            "type": "TAPO" | "NOVA_DIGITAL",
            "ip_address": "192.168.1.100" (para TAPO),
            "api_key": "sua_api_key" (para Nova Digital)
        }
    """
    try:
        device_type = connection_data.get("type", "").upper()

        if device_type == "TAPO":
            ip_address = connection_data.get("ip_address")
            if not ip_address:
                raise HTTPException(
                    status_code=400, detail="IP address required for TAPO devices"
                )

            # Testar conexão TAPO
            tapo_client = TapoClient(
                username=settings.tapo_username, password=settings.tapo_password
            )

            success = await tapo_client.add_device(ip_address, "test_device")

            if success:
                return {
                    "success": True,
                    "message": "Conexão TAPO estabelecida com sucesso",
                    "device_type": "TAPO",
                    "ip_address": ip_address,
                }
            else:
                return {
                    "success": False,
                    "message": "Falha na conexão TAPO - verifique IP e credenciais",
                    "device_type": "TAPO",
                    "ip_address": ip_address,
                }

        elif device_type == "NOVA_DIGITAL":
            api_key = connection_data.get("api_key")
            if not api_key:
                raise HTTPException(
                    status_code=400, detail="API key required for Nova Digital devices"
                )

            # Testar conexão Nova Digital
            async with NovaDigitalClient(api_key=api_key) as nova_client:
                success = await nova_client.test_connection()

                if success:
                    devices = await nova_client.get_devices()
                    return {
                        "success": True,
                        "message": "Conexão Nova Digital estabelecida com sucesso",
                        "device_type": "NOVA_DIGITAL",
                        "available_devices": len(devices),
                        "devices": devices[:5],  # Primeiros 5 dispositivos
                    }
                else:
                    return {
                        "success": False,
                        "message": "Falha na conexão Nova Digital - verifique API key",
                        "device_type": "NOVA_DIGITAL",
                    }

        else:
            raise HTTPException(
                status_code=400, detail=f"Device type {device_type} not supported"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao testar conexão: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao testar conexão: {str(e)}")


@app.get("/devices/supported-types")
async def get_supported_device_types():
    """
    Obter lista de tipos de dispositivos suportados
    """
    return {
        "supported_types": [
            {
                "type": "TAPO",
                "description": "TP-Link TAPO smart plugs",
                "connection_type": "Local IP",
                "required_fields": ["ip_address"],
                "auth_method": "Email + Password",
            },
            {
                "type": "NOVA_DIGITAL",
                "description": "Nova Digital smart plugs",
                "connection_type": "Cloud API",
                "required_fields": ["api_key"],
                "auth_method": "API Key",
            },
        ]
    }


@app.post("/devices/discover-cloud")
async def discover_cloud_devices():
    """
    Descobrir dispositivos TAPO via TP-Link Cloud
    """
    try:
        from src.integrations.tapo_cloud_client import TapoCloudClient

        discovered_devices = []

        async with TapoCloudClient(
            settings.tapo_username, settings.tapo_password
        ) as cloud_client:
            # Login na cloud
            if await cloud_client.login():
                logger.info("Login TP-Link Cloud bem-sucedido")

                # Obter lista de dispositivos
                devices = await cloud_client.get_device_list()

                for device in devices:
                    device_id = device.get("deviceId")
                    device_name = device.get("alias", f"TAPO_{device_id[:8]}")
                    device_model = device.get("deviceModel", "Unknown")
                    device_mac = device.get("deviceMac", "")

                    # Tentar obter IP do dispositivo
                    device_info = await cloud_client.get_device_info(device_id)
                    ip_address = None
                    if device_info:
                        ip_address = device_info.get("ip", device_info.get("ipAddress"))

                    discovered_devices.append(
                        {
                            "device_id": device_id,
                            "name": device_name,
                            "type": "TAPO",
                            "model": device_model,
                            "mac_address": device_mac,
                            "ip_address": ip_address,
                            "status": device.get("status", "unknown"),
                            "data_source": "tapo_cloud",
                        }
                    )

                logger.info(
                    f"Descobertos {len(discovered_devices)} dispositivos via Cloud"
                )
                return {
                    "discovered_devices": discovered_devices,
                    "total_found": len(discovered_devices),
                    "scan_type": "tapo_cloud",
                }
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Falha ao fazer login na TP-Link Cloud. Verifique credenciais.",
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao descobrir dispositivos via Cloud: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao descobrir dispositivos: {str(e)}"
        )


@app.post("/devices/discover-local")
async def discover_local_devices():
    """
    Descobrir dispositivos TAPO na rede local
    """
    try:
        # Esta é uma implementação básica - em produção, usaríamos um scanner de rede
        common_ips = [
            "192.168.1.100",
            "192.168.1.101",
            "192.168.1.102",
            "192.168.0.100",
            "192.168.0.101",
            "192.168.0.102",
            "192.168.68.100",
            "192.168.68.101",
        ]

        discovered_devices = []
        tapo_client = TapoClient(
            username=settings.tapo_username, password=settings.tapo_password
        )

        for ip in common_ips:
            try:
                # Tentativa rápida de conexão
                success = await tapo_client.add_device(ip, f"discovered_{ip}")
                if success:
                    discovered_devices.append(
                        {
                            "ip_address": ip,
                            "type": "TAPO",
                            "status": "online",
                            "suggested_name": f"TAPO_Device_{ip.split('.')[-1]}",
                        }
                    )
            except:
                continue

        return {
            "discovered_devices": discovered_devices,
            "total_found": len(discovered_devices),
            "scan_type": "basic_ip_range",
        }

    except Exception as e:
        logger.error(f"Erro ao descobrir dispositivos: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao descobrir dispositivos: {str(e)}"
        )


# ---------------------------------------------------------------------------
# Endpoints de Energia (novos - namespace /energy/*)
#
# Substituem, para a nova SPA React, a lógica de agregação que hoje só
# existe em dashboard.py. Não afetam os endpoints legados já stubados
# (/status/realtime, /reports/daily, /devices/{id}/trends|weekly|monthly,
# /devices/ranking), que permanecem como estão.
# ---------------------------------------------------------------------------


@app.get("/energy/overview")
async def get_energy_overview(tariff: Optional[float] = None):
    """Obter visão geral em tempo real dos dispositivos TAPO (resumo + lista)."""
    try:
        tapo_devices, tapo_readings, raw_devices = fetch_tapo_devices_and_readings(
            days=7
        )
        return build_energy_overview(tapo_devices, tapo_readings, raw_devices)
    except Exception as e:
        logger.error(f"Erro ao obter visão geral de energia: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Erro ao obter visão geral de energia"
        )


@app.get("/energy/history")
async def get_energy_history(days: int = 30):
    """Obter histórico de potência instantânea por dispositivo TAPO."""
    try:
        tapo_devices, tapo_readings, _ = fetch_tapo_devices_and_readings(days=days)
        series = build_power_history(tapo_devices, tapo_readings)
        return {"days": days, "series": series}
    except Exception as e:
        logger.error(f"Erro ao obter histórico de energia: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Erro ao obter histórico de energia"
        )


@app.get("/energy/daily")
async def get_energy_daily(days: int = 90, tariff: Optional[float] = None):
    """Obter consumo e custo diário agregados entre todos os dispositivos TAPO."""
    try:
        _, tapo_readings, _ = fetch_tapo_devices_and_readings(days=days)
        return build_daily_totals(tapo_readings, tariff)
    except Exception as e:
        logger.error(f"Erro ao obter consumo diário de energia: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Erro ao obter consumo diário de energia"
        )


@app.get("/energy/monthly")
async def get_energy_monthly(tariff: Optional[float] = None):
    """Obter consumo e custo mensal agregados entre todos os dispositivos TAPO."""
    try:
        # Mesma janela de 90 dias usada em dashboard.py para os gráficos
        # agregados (a busca ao Supabase já era limitada a 90 dias ali).
        _, tapo_readings, _ = fetch_tapo_devices_and_readings(days=90)
        return build_monthly_totals(tapo_readings, tariff)
    except Exception as e:
        logger.error(f"Erro ao obter consumo mensal de energia: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Erro ao obter consumo mensal de energia"
        )


@app.get("/energy/projections")
async def get_energy_projections(tariff: Optional[float] = None):
    """Obter projeções diária/semanal/mensal de consumo e custo por dispositivo TAPO."""
    try:
        tapo_devices, tapo_readings, _ = fetch_tapo_devices_and_readings(days=90)
        return build_projections(tapo_devices, tapo_readings, tariff)
    except Exception as e:
        logger.error(f"Erro ao obter projeções de energia: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Erro ao obter projeções de energia"
        )


@app.get("/energy/devices/{device_id}")
async def get_energy_device_detail(
    device_id: int, days: int = 30, tariff: Optional[float] = None
):
    """Obter detalhes, séries e detecção de anomalia de um dispositivo TAPO."""
    try:
        tapo_devices, tapo_readings, _ = fetch_tapo_devices_and_readings(days=days)
        device = next((d for d in tapo_devices if d["id"] == device_id), None)

        if device is None:
            raise HTTPException(
                status_code=404,
                detail="Dispositivo TAPO não encontrado ou não classificado",
            )

        return build_device_detail(device, tapo_readings, days, tariff)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter detalhes do dispositivo de energia: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Erro ao obter detalhes do dispositivo"
        )


@app.get("/smartlife/latest")
async def get_smartlife_latest():
    """Obter o snapshot mais recente de dados SmartLife (gerado pelo polling do Gmail)."""
    try:
        return load_smartlife_snapshot()
    except Exception as e:
        logger.error(f"Erro ao carregar dados SmartLife: {str(e)}")
        return {}


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",  # nosec B104 - Bind all interfaces is intentional for container deployment
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
