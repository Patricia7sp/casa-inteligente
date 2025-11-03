"""
Serviço de LLM para assistente inteligente da Casa Inteligente
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import openai
import google.generativeai as genai

from src.utils.config import settings
from src.services.energy_service import energy_service
from src.models.database import Device, DailyReport, get_db

logger = logging.getLogger(__name__)


class LLMService:
    """Serviço de LLM para assistente inteligente"""
    
    def __init__(self):
        self.openai_client = None
        self.gemini_client = None
        
        # Inicializar OpenAI
        if settings.openai_api_key:
            try:
                openai.api_key = settings.openai_api_key
                self.openai_client = openai
                logger.info("Cliente OpenAI inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar OpenAI: {str(e)}")
        
        # Inicializar Google Gemini
        if settings.google_ai_api_key:
            try:
                genai.configure(api_key=settings.google_ai_api_key)
                self.gemini_client = genai.GenerativeModel('gemini-pro')
                logger.info("Cliente Google Gemini inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar Google Gemini: {str(e)}")
    
    def get_system_context(self) -> str:
        """Obter contexto do sistema para o LLM"""
        try:
            # Obter status atual
            status = energy_service.get_realtime_status()
            
            # Obter dispositivos
            db = next(get_db())
            devices = db.query(Device).filter(Device.is_active == True).all()
            
            context = f"""
Você é o assistente inteligente da Casa Inteligente, um sistema de monitoramento de consumo de energia residencial.

CONTEXTO ATUAL DO SISTEMA:
- Data/Hora: {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}
- Consumo Total Atual: {status.get('total_current_power_watts', 0):.2f} W
- Dispositivos Ativos: {status.get('active_devices', 0)} de {len(devices)}

DISPOSITIVOS MONITORADOS:
"""
            
            for device in devices:
                device_status = next((d for d in status.get('devices', []) if d['device_id'] == device.id), {})
                current_power = device_status.get('current_power_watts', 0)
                
                context += f"""
- {device.name}:
  • Local: {device.location}
  • Equipamento: {device.equipment_connected}
  • Tipo: {device.type}
  • Consumo Atual: {current_power:.2f} W
  • Status: {'Ativo' if current_power > 0 else 'Inativo'}
"""
            
            # Obter relatório de hoje
            today_report = energy_service.generate_daily_report()
            if today_report and 'error' not in today_report:
                context += f"""

RELATÓRIO DE HOJE:
- Consumo Total: {today_report.get('total_energy_kwh', 0):.3f} kWh
- Custo Estimado: R$ {today_report.get('total_cost', 0):.2f}
- Dispositivos com Anomalias: {len(today_report.get('anomalies', []))}
"""
            
            context += """

CUSTO DE ENERGIA:
- Valor por kWh: R$ {:.2f}

REGRAS IMPORTANTES:
1. Sempre baseie suas respostas nos dados reais do sistema
2. Se não tiver dados suficientes, informe o usuário
3. Forneça recomendações práticas para economia de energia
4. Alerte sobre consumos anômalos quando detectados
5. Use linguagem clara e objetiva
6. Seja proativo em identificar problemas potenciais

EXEMPLOS DE PERGUNTAS QUE VOCÊ PODE RESPONDER:
- "Qual equipamento está consumindo mais energia agora?"
- "Meu consumo hoje está normal?"
- "Como posso reduzir o consumo de energia?"
- "Existe algum dispositivo com comportamento estranho?"
- "Qual foi o custo total ontem?"
- "Recomende ações para economizar energia"
""".format(settings.energy_cost_per_kwh)
            
            db.close()
            return context
            
        except Exception as e:
            logger.error(f"Erro ao obter contexto do sistema: {str(e)}")
            return "Erro ao obter dados do sistema. Tente novamente em instantes."
    
    async def ask_openai(self, question: str) -> Optional[str]:
        """Fazer pergunta ao OpenAI GPT"""
        if not self.openai_client:
            return "OpenAI não configurado"
        
        try:
            context = self.get_system_context()
            
            response = await self.openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": question}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro ao consultar OpenAI: {str(e)}")
            return f"Erro ao processar pergunta: {str(e)}"
    
    def ask_gemini(self, question: str) -> Optional[str]:
        """Fazer pergunta ao Google Gemini"""
        if not self.gemini_client:
            return "Google Gemini não configurado"
        
        try:
            context = self.get_system_context()
            
            prompt = f"{context}\n\nPERGUNTA DO USUÁRIO: {question}"
            
            response = self.gemini_client.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Erro ao consultar Gemini: {str(e)}")
            return f"Erro ao processar pergunta: {str(e)}"
    
    async def ask_question(self, question: str, preferred_provider: str = "openai") -> Dict[str, Any]:
        """
        Fazer pergunta ao assistente LLM
        
        Args:
            question: Pergunta do usuário
            preferred_provider: "openai", "gemini" ou "auto"
            
        Returns:
            Dict com resposta e metadados
        """
        try:
            # Escolher provedor
            if preferred_provider == "openai" and self.openai_client:
                response = await self.ask_openai(question)
                provider = "openai"
            elif preferred_provider == "gemini" and self.gemini_client:
                response = self.ask_gemini(question)
                provider = "gemini"
            else:
                # Auto: tentar OpenAI primeiro, depois Gemini
                if self.openai_client:
                    response = await self.ask_openai(question)
                    provider = "openai"
                elif self.gemini_client:
                    response = self.ask_gemini(question)
                    provider = "gemini"
                else:
                    return {
                        "error": "Nenhum provedor LLM configurado",
                        "response": None,
                        "provider": None
                    }
            
            return {
                "response": response,
                "provider": provider,
                "question": question,
                "timestamp": datetime.utcnow(),
                "context_available": True
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {str(e)}")
            return {
                "error": str(e),
                "response": None,
                "provider": preferred_provider,
                "question": question
            }
    
    def get_energy_insights(self, days: int = 7) -> Dict[str, Any]:
        """
        Gerar insights automáticos sobre consumo de energia
        
        Args:
            days: Número de dias para análise
            
        Returns:
            Dict com insights e recomendações
        """
        try:
            db = next(get_db())
            devices = db.query(Device).filter(Device.is_active == True).all()
            
            insights = {
                "period_days": days,
                "total_devices": len(devices),
                "top_consumers": [],
                "anomalies_detected": [],
                "recommendations": [],
                "summary": ""
            }
            
            # Analisar cada dispositivo
            for device in devices:
                trends = energy_service.get_consumption_trends(device.id, days)
                
                if trends:
                    # Top consumidores
                    if trends["total_energy_kwh"] > 0:
                        insights["top_consumers"].append({
                            "device_name": device.name,
                            "location": device.location,
                            "total_energy_kwh": trends["total_energy_kwh"],
                            "average_daily_cost": trends["average_daily_cost"]
                        })
                    
                    # Detectar anomalias
                    if trends["max_daily_energy_kwh"] > trends["average_daily_energy_kwh"] * 2:
                        insights["anomalies_detected"].append({
                            "device_name": device.name,
                            "issue": f"Pico de consumo detectado: {trends['max_daily_energy_kwh']:.3f} kWh",
                            "recommendation": "Verifique se o equipamento está funcionando corretamente"
                        })
            
            # Ordenar top consumidores
            insights["top_consumers"].sort(key=lambda x: x["total_energy_kwh"], reverse=True)
            
            # Gerar recomendações
            insights["recommendations"] = self._generate_recommendations(insights)
            
            # Gerar resumo
            insights["summary"] = self._generate_summary(insights)
            
            db.close()
            return insights
            
        except Exception as e:
            logger.error(f"Erro ao gerar insights: {str(e)}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, insights: Dict) -> List[str]:
        """Gerar recomendações baseadas nos insights"""
        recommendations = []
        
        if insights["top_consumers"]:
            top_device = insights["top_consumers"][0]
            recommendations.append(
                f"O dispositivo '{top_device['device_name']}' em '{top_device['location']}' "
                f"é o maior consumidor de energia ({top_device['total_energy_kwh']:.3f} kWh em {insights['period_days']} dias). "
                f"Considere verificar se há oportunidades de otimização."
            )
        
        if insights["anomalies_detected"]:
            recommendations.append(
                f"Foram detectadas {len(insights['anomalies_detected'])} anomalias de consumo. "
                f"É recomendável investigar esses dispositivos para evitar custos excessivos."
            )
        
        recommendations.extend([
            "Considere programar o desligamento de dispositivos não essenciais durante a noite.",
            "Monitore regularmente o consumo para identificar padrões e oportunidades de economia.",
            "Verifique se há equipamentos antigos que poderiam ser substituídos por modelos mais eficientes."
        ])
        
        return recommendations
    
    def _generate_summary(self, insights: Dict) -> str:
        """Gerar resumo dos insights"""
        if "error" in insights:
            return "Não foi possível gerar o resumo no momento."
        
        total_energy = sum(d["total_energy_kwh"] for d in insights["top_consumers"])
        total_cost = total_energy * settings.energy_cost_per_kwh
        
        summary = f"""
Nos últimos {insights['period_days']} dias, seus {insights['total_devices']} dispositivos consumiram aproximadamente {total_energy:.3f} kWh, 
resultando em um custo estimado de R$ {total_cost:.2f}.
"""
        
        if insights["anomalies_detected"]:
            summary += f"Foram detectadas {len(insights['anomalies_detected'])} anomalias que merecem atenção. "
        
        if insights["top_consumers"]:
            summary += f"O maior consumidor foi '{insights['top_consumers'][0]['device_name']}'."
        
        return summary.strip()


# Instância global do serviço
llm_service = LLMService()
