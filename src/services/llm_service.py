"""
Serviço de LLM para assistente inteligente da Casa Inteligente
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from openai import AsyncOpenAI
import google.generativeai as genai
import requests

from src.utils.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Serviço de LLM para assistente inteligente"""

    def __init__(self):
        self.openai_client = None
        self.gemini_client = None

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

        # Inicializar OpenAI com nova API v1.0+
        if settings.openai_api_key:
            try:
                self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info("Cliente OpenAI inicializado (API v1.0+)")
            except Exception as e:
                logger.error(f"Erro ao inicializar OpenAI: {str(e)}")

        # Inicializar Google Gemini
        if settings.google_ai_api_key:
            try:
                genai.configure(api_key=settings.google_ai_api_key)
                preferred_models = [
                    "models/gemini-2.5-pro",
                    "models/gemini-1.5-flash",
                    "models/gemini-1.5-pro",
                    "gemini-pro",
                ]
                for model_name in preferred_models:
                    try:
                        self.gemini_client = genai.GenerativeModel(model_name)
                        self.gemini_model_name = model_name
                        logger.info(
                            "Cliente Google Gemini inicializado com o modelo %s",
                            model_name,
                        )
                        break
                    except Exception as model_error:  # tentar próximo modelo
                        logger.warning(
                            "Falha ao inicializar modelo Gemini %s: %s",
                            model_name,
                            model_error,
                        )
                        self.gemini_client = None
                if not self.gemini_client:
                    logger.error("Nenhum modelo Gemini pôde ser inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar Google Gemini: {str(e)}")
        else:
            self.gemini_model_name = None

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
                logger.error(
                    f"Erro ao buscar {endpoint} do Supabase: {response.status_code}"
                )
                return []
        except Exception as e:
            logger.error(f"Erro ao conectar ao Supabase: {str(e)}")
            return []

    def get_system_context(self) -> str:
        """Obter contexto do sistema para o LLM usando dados do Supabase"""
        try:
            # Buscar dispositivos do Supabase
            devices = self._get_supabase_data("devices")
            if not devices:
                return "Não foi possível acessar os dados dos dispositivos. Tente novamente."

            # Buscar todas as leituras recentes (últimas 1000) ordenadas por timestamp
            all_readings = self._get_supabase_data(
                "energy_readings",
                params={"order": "timestamp.desc", "limit": "1000"},
            )

            # Buscar leituras de hoje para cálculo de energia
            today_start = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            readings_today = [
                r
                for r in all_readings
                if datetime.fromisoformat(r.get("timestamp", "").replace("Z", "+00:00"))
                >= today_start
            ]

            context = f"""
Você é o assistente inteligente da Casa Inteligente, um sistema de monitoramento de consumo de energia residencial do usuário.

IMPORTANTE: Quando o usuário perguntar sobre "dispositivos", "consumo" ou "gastos" SEM especificar contexto externo, 
SEMPRE se refira aos dispositivos DESTE SISTEMA listados abaixo. Estes são OS DISPOSITIVOS DO USUÁRIO.

CONTEXTO ATUAL DO SISTEMA:
- Data/Hora: {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}
- Dispositivos Monitorados: {len(devices)}

DISPOSITIVOS DO USUÁRIO (MONITORADOS NESTE SISTEMA):
"""

            # Processar dados de cada dispositivo
            device_consumption = []
            total_power = 0
            active_count = 0

            for device in devices:
                device_id = device.get("id")
                device_name = device.get("name", "Dispositivo")
                equipment = device.get("equipment_connected", "N/A")
                location = device.get("location", "N/A")
                device_type = device.get("type", "N/A")

                # Buscar última leitura deste dispositivo (de todas as leituras)
                device_all_readings = [
                    r for r in all_readings if r.get("device_id") == device_id
                ]

                # Buscar leituras de hoje deste dispositivo
                device_readings_today = [
                    r for r in readings_today if r.get("device_id") == device_id
                ]

                current_power = 0
                energy_today = 0
                last_reading_time = None

                # Usar a última leitura disponível (não apenas de hoje)
                if device_all_readings:
                    latest = device_all_readings[0]
                    current_power = latest.get("power_watts", 0)
                    last_reading_time = latest.get("timestamp", "")

                    total_power += current_power
                    if current_power > 0:
                        active_count += 1

                # Calcular energia apenas de hoje
                if device_readings_today:
                    energy_today = sum(
                        r.get("energy_kwh", 0) for r in device_readings_today
                    )

                device_consumption.append(
                    {
                        "name": device_name,
                        "equipment": equipment,
                        "location": location,
                        "type": device_type,
                        "current_power": current_power,
                        "energy_today": energy_today,
                    }
                )

                status_icon = "🟢 Ligado" if current_power > 0 else "🔴 Desligado"

                # Formatar tempo da última leitura
                last_reading_info = ""
                if last_reading_time:
                    try:
                        last_time = datetime.fromisoformat(
                            last_reading_time.replace("Z", "+00:00")
                        )
                        time_diff = (
                            datetime.utcnow().replace(tzinfo=last_time.tzinfo)
                            - last_time
                        )
                        if time_diff.total_seconds() < 3600:
                            last_reading_info = (
                                f" (há {int(time_diff.total_seconds() / 60)} min)"
                            )
                        elif time_diff.total_seconds() < 86400:
                            last_reading_info = (
                                f" (há {int(time_diff.total_seconds() / 3600)} h)"
                            )
                        else:
                            last_reading_info = (
                                f" (há {int(time_diff.total_seconds() / 86400)} dias)"
                            )
                    except:
                        pass

                context += f"""
- {device_name}:
  • Equipamento: {equipment}
  • Local: {location}
  • Tipo: {device_type}
  • Consumo Atual: {current_power:.2f} W{last_reading_info}
  • Energia Hoje: {energy_today:.3f} kWh
  • Status: {status_icon}
"""

            # Adicionar totais
            context += f"""

TOTAIS DO SISTEMA:
- Consumo Total Atual: {total_power:.2f} W
- Dispositivos Ativos Agora: {active_count} de {len(devices)}
"""

            # Ranking de consumo
            device_consumption.sort(key=lambda x: x["energy_today"], reverse=True)
            if device_consumption and device_consumption[0]["energy_today"] > 0:
                context += """

RANKING DE CONSUMO HOJE (maior para menor):
"""
                for idx, dev in enumerate(device_consumption[:5], 1):
                    if dev["energy_today"] > 0:
                        context += f"{idx}. {dev['equipment']} ({dev['name']}): {dev['energy_today']:.3f} kWh\n"

                # Calcular custo total
                total_energy = sum(d["energy_today"] for d in device_consumption)
                total_cost = total_energy * settings.energy_cost_per_kwh
                context += f"""

RELATÓRIO DE HOJE:
- Consumo Total: {total_energy:.3f} kWh
- Custo Estimado: R$ {total_cost:.2f}
"""

            context += """

CUSTO DE ENERGIA:
- Tarifa: R$ {:.2f} por kWh

REGRAS CRÍTICAS:
1. SEMPRE use os dados reais dos dispositivos listados acima
2. Quando perguntarem "qual dispositivo gasta mais", responda com base no RANKING DE CONSUMO
3. Se não houver dados suficientes, explique o motivo técnico de forma clara
4. Seja específico: cite nomes de dispositivos, valores numéricos e locais
5. Use linguagem clara, objetiva e amigável
6. Priorize economia de energia e detecção de anomalias
7. NUNCA invente dados - use apenas informações fornecidas neste contexto

EXEMPLOS DE PERGUNTAS QUE VOCÊ DEVE RESPONDER COM DADOS REAIS:
- "Qual dispositivo gasta mais?" → Responda com o 1º do ranking
- "Qual o consumo de hoje?" → Use o valor do RELATÓRIO DE HOJE
- "Como está meu consumo?" → Compare com dados históricos se disponíveis
- "Quanto estou gastando?" → Calcule com base na tarifa e consumo
""".format(
                settings.energy_cost_per_kwh
            )

            return context

        except Exception as e:
            logger.error(f"Erro ao obter contexto do sistema: {str(e)}")
            return "Erro ao obter dados do sistema. Tente novamente em instantes."

    async def ask_openai(self, question: str) -> Optional[str]:
        """Fazer pergunta ao OpenAI GPT usando nova API v1.0+"""
        if not self.openai_client:
            return "OpenAI não configurado"

        try:
            context = self.get_system_context()

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Modelo moderno e eficiente
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": question},
                ],
                max_tokens=800,
                temperature=0.7,
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
            if hasattr(response, "text") and response.text:
                return response.text

            return "Nenhuma resposta retornada pelo modelo Gemini."

        except Exception as e:
            logger.error(f"Erro ao consultar Gemini: {str(e)}")
            model_hint = (
                f" (modelo: {getattr(self, 'gemini_model_name', 'desconhecido')})"
            )
            return f"Erro ao processar pergunta: {str(e)}{model_hint}"

    async def ask_question(
        self, question: str, preferred_provider: str = "openai"
    ) -> Dict[str, Any]:
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
                        "provider": None,
                    }

            return {
                "response": response,
                "provider": provider,
                "question": question,
                "timestamp": datetime.utcnow(),
                "context_available": True,
            }

        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {str(e)}")
            return {
                "error": str(e),
                "response": None,
                "provider": preferred_provider,
                "question": question,
            }

    def get_energy_insights(self, days: int = 7) -> Dict[str, Any]:
        """
        Gerar insights automáticos sobre consumo de energia
        NOTA: Temporariamente desabilitado - será reimplementado com Supabase

        Args:
            days: Número de dias para análise

        Returns:
            Dict com insights e recomendações
        """
        try:
            # TODO: Reimplementar usando Supabase
            devices = self._get_supabase_data("devices")

            insights = {
                "period_days": days,
                "total_devices": len(devices),
                "top_consumers": [],
                "anomalies_detected": [],
                "recommendations": [],
                "summary": "",
            }

            # Retornar insights básicos por enquanto
            insights["recommendations"] = [
                "Monitore regularmente o consumo através do dashboard",
                "Verifique dispositivos que ficam ligados desnecessariamente",
            ]
            insights["summary"] = f"Sistema monitorando {len(devices)} dispositivos."

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

        recommendations.extend(
            [
                "Considere programar o desligamento de dispositivos não essenciais durante a noite.",
                "Monitore regularmente o consumo para identificar padrões e oportunidades de economia.",
                "Verifique se há equipamentos antigos que poderiam ser substituídos por modelos mais eficientes.",
            ]
        )

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
