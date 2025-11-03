"""
Aplicação principal - Casa Inteligente API
"""

import asyncio
import logging
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from typing import List, Dict

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.models.database import Device, EnergyReading, DailyReport, get_db, create_tables
from src.agents.collector import collector
from src.services.energy_service import energy_service
from src.services.notification_service import notification_service
from src.services.llm_service import llm_service
from src.utils.config import settings
from src.utils.logger import setup_logging

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# Variável global para o coletor
collector_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    # Startup
    logger.info("Iniciando Casa Inteligente API...")
    
    # Criar tabelas do banco de dados
    try:
        create_tables()
        logger.info("Tabelas do banco de dados criadas/atualizadas")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}")
    
    # Inicializar coletor
    try:
        await collector.initialize()
        logger.info("Coletor de dados inicializado")
    except Exception as e:
        logger.error(f"Erro ao inicializar coletor: {str(e)}")
    
    # Iniciar coleta em background
    global collector_task
    collector_task = asyncio.create_task(collector.start_collection())
    logger.info("Coleta de dados iniciada em background")
    
    # Enviar notificação de sistema online
    await notification_service.send_system_notification("🟢 Sistema Casa Inteligente iniciado com sucesso!", "INFO")
    
    yield
    
    # Shutdown
    logger.info("Desligando Casa Inteligente API...")
    
    # Parar coletor
    if collector_task:
        collector.stop_collection()
        collector_task.cancel()
        try:
            await collector_task
        except asyncio.CancelledError:
            pass
    
    # Enviar notificação de sistema offline
    await notification_service.send_system_notification("🔴 Sistema Casa Inteligente desligado", "WARNING")


# Criar aplicação FastAPI
app = FastAPI(
    title="Casa Inteligente API",
    description="API para monitoramento inteligente de consumo de energia residencial",
    version="1.0.0",
    lifespan=lifespan
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
        "timestamp": datetime.utcnow()
    }


@app.get("/health")
async def health_check():
    """Verificar saúde da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "collector_running": collector.running
    }


@app.get("/devices")
async def get_devices():
    """Obter todos os dispositivos cadastrados"""
    try:
        db = next(get_db())
        devices = db.query(Device).filter(Device.is_active == True).all()
        
        device_list = []
        for device in devices:
            device_list.append({
                "id": device.id,
                "name": device.name,
                "type": device.type,
                "ip_address": device.ip_address,
                "location": device.location,
                "equipment_connected": device.equipment_connected,
                "created_at": device.created_at
            })
        
        db.close()
        return {"devices": device_list, "count": len(device_list)}
        
    except Exception as e:
        logger.error(f"Erro ao obter dispositivos: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter dispositivos")


@app.post("/devices")
async def add_device(device_data: Dict, background_tasks: BackgroundTasks):
    """Adicionar novo dispositivo"""
    try:
        db = next(get_db())
        
        # Verificar se dispositivo já existe
        existing = db.query(Device).filter(Device.ip_address == device_data["ip_address"]).first()
        if existing:
            db.close()
            raise HTTPException(status_code=400, detail="Dispositivo com este IP já existe")
        
        # Criar novo dispositivo
        device = Device(
            name=device_data["name"],
            type=device_data["type"],
            ip_address=device_data["ip_address"],
            mac_address=device_data.get("mac_address"),
            model=device_data.get("model"),
            location=device_data.get("location"),
            equipment_connected=device_data.get("equipment_connected")
        )
        
        db.add(device)
        db.commit()
        db.refresh(device)
        
        # Adicionar ao coletor em background
        if device.type.upper() == "TAPO":
            background_tasks.add_task(
                collector.tapo_client.add_device,
                device.ip_address,
                device.name
            )
        
        db.close()
        
        logger.info(f"Dispositivo {device.name} adicionado com sucesso")
        return {"message": "Dispositivo adicionado com sucesso", "device_id": device.id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao adicionar dispositivo: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao adicionar dispositivo")


@app.get("/devices/{device_id}/status")
async def get_device_status(device_id: int):
    """Obter status atual de um dispositivo"""
    try:
        db = next(get_db())
        device = db.query(Device).filter(Device.id == device_id).first()
        
        if not device:
            db.close()
            raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
        
        # Obter última leitura
        latest_reading = db.query(EnergyReading).filter(
            EnergyReading.device_id == device_id
        ).order_by(EnergyReading.timestamp.desc()).first()
        
        status = {
            "device_id": device.id,
            "device_name": device.name,
            "type": device.type,
            "ip_address": device.ip_address,
            "location": device.location,
            "equipment_connected": device.equipment_connected,
            "is_active": device.is_active
        }
        
        if latest_reading:
            status.update({
                "current_power_watts": latest_reading.power_watts,
                "voltage": latest_reading.voltage,
                "current": latest_reading.current,
                "energy_today_kwh": latest_reading.energy_today_kwh,
                "energy_total_kwh": latest_reading.energy_total_kwh,
                "last_reading": latest_reading.timestamp,
                "is_on": latest_reading.power_watts > 0
            })
        else:
            status.update({
                "current_power_watts": 0,
                "is_on": False,
                "last_reading": None,
                "message": "Nenhuma leitura encontrada"
            })
        
        db.close()
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status do dispositivo: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter status do dispositivo")


@app.get("/status/realtime")
async def get_realtime_status():
    """Obter status em tempo real de todos os dispositivos"""
    try:
        status = energy_service.get_realtime_status()
        return status
    except Exception as e:
        logger.error(f"Erro ao obter status em tempo real: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter status em tempo real")


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
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
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
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
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
            raise HTTPException(status_code=404, detail="Nenhum dado encontrado para este dispositivo")
        
        return trends
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter tendências: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter tendências")


@app.post("/devices/{device_id}/control")
async def control_device(device_id: int, action: str, background_tasks: BackgroundTasks):
    """Controlar dispositivo (ligar/desligar)"""
    try:
        db = next(get_db())
        device = db.query(Device).filter(Device.id == device_id).first()
        
        if not device:
            db.close()
            raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
        
        if device.type.upper() != "TAPO":
            db.close()
            raise HTTPException(status_code=400, detail="Controle não disponível para este tipo de dispositivo")
        
        # Executar ação em background
        if action.lower() == "on":
            background_tasks.add_task(collector.tapo_client.turn_on, device.name)
            message = f"Comando de ligar enviado para {device.name}"
        elif action.lower() == "off":
            background_tasks.add_task(collector.tapo_client.turn_off, device.name)
            message = f"Comando de desligar enviado para {device.name}"
        else:
            db.close()
            raise HTTPException(status_code=400, detail="Ação inválida. Use 'on' ou 'off'")
        
        db.close()
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
            raise HTTPException(status_code=400, detail="Período deve estar entre 1 e 365 dias")
        
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
            raise HTTPException(status_code=400, detail="ID do dispositivo não fornecido")
        
        # Obter informações do dispositivo
        db = next(get_db())
        device = db.query(Device).filter(Device.id == device_id).first()
        
        if not device:
            db.close()
            raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
        
        # Obter tendências do dispositivo
        trends = energy_service.get_consumption_trends(device_id, days)
        
        if not trends:
            db.close()
            raise HTTPException(status_code=404, detail="Nenhum dado encontrado para este dispositivo")
        
        # Gerar recomendações personalizadas
        question = f"""
Baseado nos dados do dispositivo '{device.name}' ({device.location}) nos últimos {days} dias:
- Consumo total: {trends['total_energy_kwh']:.3f} kWh
- Custo total: R$ {trends['total_cost']:.2f}
- Média diária: {trends['average_daily_energy_kwh']:.3f} kWh
- Pico: {trends['max_daily_energy_kwh']:.3f} kWh

Forneça recomendações específicas para otimizar o consumo deste dispositivo.
"""
        
        response = await llm_service.ask_question(question, "auto")
        
        db.close()
        
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        
        return {
            "device_info": {
                "name": device.name,
                "location": device.location,
                "equipment": device.equipment_connected
            },
            "trends": trends,
            "recommendations": response["response"],
            "generated_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar recomendações: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao gerar recomendações")


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
