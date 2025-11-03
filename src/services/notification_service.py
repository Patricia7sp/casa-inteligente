"""
Serviço de notificações via Email e Telegram
"""

import logging
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional

from telegram import Bot
from telegram.error import TelegramError

from src.utils.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Serviço responsável por enviar notificações"""
    
    def __init__(self):
        self.telegram_bot = None
        if settings.telegram_bot_token:
            try:
                self.telegram_bot = Bot(token=settings.telegram_bot_token)
                logger.info("Bot Telegram inicializado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar bot Telegram: {str(e)}")
    
    async def send_telegram_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """
        Enviar mensagem via Telegram
        
        Args:
            message: Mensagem para enviar
            parse_mode: Modo de parse (Markdown, HTML, None)
            
        Returns:
            bool: True se enviado com sucesso
        """
        if not self.telegram_bot or not settings.telegram_chat_id:
            logger.warning("Bot Telegram não configurado")
            return False
        
        try:
            await self.telegram_bot.send_message(
                chat_id=settings.telegram_chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info("Mensagem Telegram enviada com sucesso")
            return True
            
        except TelegramError as e:
            logger.error(f"Erro ao enviar mensagem Telegram: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar mensagem Telegram: {str(e)}")
            return False
    
    def send_email(self, subject: str, body: str, is_html: bool = False) -> bool:
        """
        Enviar email
        
        Args:
            subject: Assunto do email
            body: Corpo do email
            is_html: Se o corpo é HTML
            
        Returns:
            bool: True se enviado com sucesso
        """
        if not settings.email_username or not settings.email_password:
            logger.warning("Email não configurado")
            return False
        
        if not settings.email_recipients:
            logger.warning("Nenhum destinatário de email configurado")
            return False
        
        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = settings.email_username
            msg['To'] = ", ".join(settings.email_recipients)
            msg['Subject'] = subject
            
            # Adicionar corpo
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Conectar e enviar
            server = smtplib.SMTP(settings.email_smtp_server, settings.email_smtp_port)
            server.starttls()
            server.login(settings.email_username, settings.email_password)
            
            text = msg.as_string()
            server.sendmail(settings.email_username, settings.email_recipients, text)
            server.quit()
            
            logger.info(f"Email enviado com sucesso para {len(settings.email_recipients)} destinatários")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            return False
    
    async def send_daily_report(self, report_data: Dict) -> bool:
        """
        Enviar relatório diário
        
        Args:
            report_data: Dados do relatório diário
            
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            # Formatar mensagem para Telegram
            telegram_message = f"""⚡ *Relatório Diário de Consumo - Casa Inteligente*
📅 *Data:* {report_data['date'].strftime('%d/%m/%Y')}

💰 *Resumo do Dia:*
• Consumo Total: {report_data['total_energy_kwh']:.3f} kWh
• Custo Total: R$ {report_data['total_cost']:.2f}
• Dispositivos Monitorados: {len(report_data['devices'])}

📊 *Dispositivos:*
"""
            
            for device in report_data['devices']:
                status_emoji = "🟢" if device['average_power_watts'] > 0 else "🔴"
                anomaly_emoji = "⚠️" if device.get('anomaly') else ""
                
                telegram_message += f"""
{status_emoji} *{device['device_name']}* ({device['location']})
• Equipamento: {device['equipment']}
• Consumo: {device['total_energy_kwh']:.3f} kWh
• Custo: R$ {device['total_cost']:.2f}
• Média: {device['average_power_watts']:.1f}W
• Pico: {device['peak_power_watts']:.1f}W {anomaly_emoji}
"""
            
            if report_data['anomalies']:
                telegram_message += f"""
⚠️ *Anomalias Detectadas:*
"""
                for anomaly in report_data['anomalies']:
                    telegram_message += f"• {anomaly['description']}\n"
            
            telegram_message += f"""
🔋 *Dica do Dia:* Monitore equipamentos com consumo acima da média para identificar possíveis problemas!

_Casa Inteligente - Seu assistente de energia_"""
            
            # Enviar Telegram
            telegram_success = await self.send_telegram_message(telegram_message)
            
            # Formatar email
            email_subject = f"Relatório Diário de Consumo - {report_data['date'].strftime('%d/%m/%Y')}"
            
            email_body = f"""
<html>
<body>
    <h2>⚡ Relatório Diário de Consumo - Casa Inteligente</h2>
    <h3>📅 Data: {report_data['date'].strftime('%d/%m/%Y')}</h3>
    
    <h3>💰 Resumo do Dia:</h3>
    <ul>
        <li><strong>Consumo Total:</strong> {report_data['total_energy_kwh']:.3f} kWh</li>
        <li><strong>Custo Total:</strong> R$ {report_data['total_cost']:.2f}</li>
        <li><strong>Dispositivos Monitorados:</strong> {len(report_data['devices'])}</li>
    </ul>
    
    <h3>📊 Dispositivos:</h3>
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr>
            <th><strong>Dispositivo</strong></th>
            <th><strong>Local</strong></th>
            <th><strong>Equipamento</strong></th>
            <th><strong>Consumo (kWh)</strong></th>
            <th><strong>Custo (R$)</strong></th>
            <th><strong>Média (W)</strong></th>
            <th><strong>Pico (W)</strong></th>
        </tr>
"""
            
            for device in report_data['devices']:
                status_color = "#90EE90" if device['average_power_watts'] > 0 else "#FFB6C1"
                anomaly_note = f"<br><small>⚠️ {device.get('anomaly', {}).get('description', '')}</small>" if device.get('anomaly') else ""
                
                email_body += f"""
        <tr style="background-color: {status_color};">
            <td>{device['device_name']}</td>
            <td>{device['location']}</td>
            <td>{device['equipment']}</td>
            <td>{device['total_energy_kwh']:.3f}</td>
            <td>R$ {device['total_cost']:.2f}</td>
            <td>{device['average_power_watts']:.1f}</td>
            <td>{device['peak_power_watts']:.1f}{anomaly_note}</td>
        </tr>
"""
            
            email_body += """
    </table>
    
    <br>
    <p><em>🔋 Dica do Dia: Monitore equipamentos com consumo acima da média para identificar possíveis problemas!</em></p>
    <hr>
    <p><small><em>Casa Inteligente - Seu assistente de energia</em></small></p>
</body>
</html>
"""
            
            # Enviar Email
            email_success = self.send_email(email_subject, email_body, is_html=True)
            
            logger.info(f"Relatório diário enviado - Telegram: {telegram_success}, Email: {email_success}")
            return telegram_success or email_success
            
        except Exception as e:
            logger.error(f"Erro ao enviar relatório diário: {str(e)}")
            return False
    
    async def send_alert(self, alert_data: Dict) -> bool:
        """
        Enviar alerta de anomalia
        
        Args:
            alert_data: Dados do alerta
            
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            # Formatar mensagem de alerta
            alert_message = f"""🚨 *Alerta de Consumo Anômalo - Casa Inteligente*

⚠️ *{alert_data.get('alert_type', 'ANOMALY DETECTED')}*

📍 *Dispositivo:* {alert_data.get('device_name', 'Desconhecido')}
🏠 *Local:* {alert_data.get('location', 'Não informado')}
🔌 *Equipamento:* {alert_data.get('equipment', 'Não informado')}

📊 *Dados do Alerta:*
{alert_data.get('message', 'Mensagem não disponível')}

⏰ *Horário:* {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}

_Verifique o dispositivo e tome as ações necessárias!_

_Casa Inteligente - Monitoramento 24/7_"""
            
            # Enviar Telegram
            telegram_success = await self.send_telegram_message(alert_message)
            
            # Enviar Email
            email_subject = f"🚨 Alerta de Consumo Anômalo - {alert_data.get('device_name', 'Dispositivo')}"
            email_success = self.send_email(email_subject, alert_message.replace('*', '').replace('_', ''))
            
            logger.info(f"Alerta enviado - Telegram: {telegram_success}, Email: {email_success}")
            return telegram_success or email_success
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta: {str(e)}")
            return False
    
    async def send_system_notification(self, message: str, level: str = "INFO") -> bool:
        """
        Enviar notificação do sistema
        
        Args:
            message: Mensagem do sistema
            level: Nível (INFO, WARNING, ERROR)
            
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            level_emoji = {
                "INFO": "ℹ️",
                "WARNING": "⚠️",
                "ERROR": "❌"
            }.get(level, "ℹ️")
            
            system_message = f"""{level_emoji} *Notificação do Sistema - Casa Inteligente*

{message}

⏰ *Horário:* {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}

_Casa Inteligente - Sistema de Monitoramento_"""
            
            return await self.send_telegram_message(system_message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação do sistema: {str(e)}")
            return False
    
    def test_notifications(self) -> Dict[str, bool]:
        """
        Testar configurações de notificação
        
        Returns:
            Dict com resultados dos testes
        """
        results = {}
        
        # Testar Telegram
        if self.telegram_bot:
            try:
                # Usar asyncio.run para testar método assíncrono
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results["telegram"] = loop.run_until_complete(
                    self.send_telegram_message("🧪 Teste de notificação - Casa Inteligente")
                )
                loop.close()
            except Exception as e:
                logger.error(f"Erro no teste Telegram: {str(e)}")
                results["telegram"] = False
        else:
            results["telegram"] = False
        
        # Testar Email
        results["email"] = self.send_email(
            "🧪 Teste de Notificação - Casa Inteligente",
            "Este é um email de teste do sistema Casa Inteligente.\n\nSe você recebeu este email, as configurações estão corretas!"
        )
        
        logger.info(f"Testes de notificação concluídos: {results}")
        return results


# Instância global do serviço
notification_service = NotificationService()
