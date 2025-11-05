#!/usr/bin/env python3
"""
Agente Semanal de Monitoramento de Energia
Roda automaticamente toda sexta-feira para processar relatórios SmartLife
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import schedule
import time

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.gmail_client import GmailSmartLifeClient
from integrations.smartlife_parser import SmartLifeReportParser
from agents.energy_analyzer import EnergyAnalyzer


class WeeklyEnergyAgent:
    """Agente que processa relatórios de energia semanalmente"""

    def __init__(self):
        self.gmail_client = GmailSmartLifeClient()
        self.parser = SmartLifeReportParser()
        self.analyzer = EnergyAnalyzer(tariff_kwh=0.85)

        self.log_file = Path("logs/weekly_agent.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message: str):
        """Registrar log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"

        print(log_message)

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")

    def run_weekly_analysis(self):
        """Executar análise semanal completa"""

        self.log("=" * 60)
        self.log("🤖 AGENTE SEMANAL - INICIANDO")
        self.log("=" * 60)

        try:
            # 1. Buscar relatórios no Gmail
            self.log("📧 Buscando relatórios no Gmail...")

            reports = self.gmail_client.search_smartlife_reports(days_back=7)

            if not reports:
                self.log("⚠️ Nenhum relatório encontrado nos últimos 7 dias")
                self.log("💡 Verifique se os relatórios estão sendo enviados")
                return False

            self.log(f"✅ Encontrados {len(reports)} relatórios")

            # 2. Processar o relatório mais recente
            latest_report = reports[0]
            self.log(f"📄 Processando relatório mais recente...")

            # Salvar HTML
            html_path = self.gmail_client.save_report(latest_report)
            self.log(f"💾 HTML salvo: {html_path}")

            # 3. Parsear dados
            self.log("📊 Extraindo dados do relatório...")

            parsed_data = self.parser.parse_html_report(latest_report["html_content"])

            json_path = self.parser.save_parsed_data(parsed_data)
            self.log(f"💾 Dados parseados salvos: {json_path}")

            # 4. Analisar consumo
            self.log("🔍 Analisando consumo de energia...")

            analysis = self.analyzer.analyze_report(parsed_data)

            analysis_path = self.analyzer.save_analysis(analysis)
            self.log(f"💾 Análise salva: {analysis_path}")

            # 5. Gerar resumo
            self.log("\n" + "=" * 60)
            self.log("📋 RESUMO DA ANÁLISE SEMANAL")
            self.log("=" * 60)

            self._log_summary(analysis)

            # 6. Verificar alertas críticos
            self._check_critical_alerts(analysis)

            self.log("\n✅ Análise semanal concluída com sucesso!")
            self.log("=" * 60)

            return True

        except Exception as e:
            self.log(f"❌ ERRO na análise semanal: {e}")
            import traceback

            self.log(traceback.format_exc())
            return False

    def _log_summary(self, analysis: dict):
        """Registrar resumo da análise"""

        # Consumo
        consumption = analysis["consumption_analysis"]
        self.log(f"\n⚡ CONSUMO:")
        self.log(f"   Média diária: {consumption.get('daily_average', 'N/A')} kWh")
        self.log(
            f"   Projeção mensal: {consumption.get('monthly_projection', 'N/A')} kWh"
        )
        self.log(f"   Status: {consumption['status']}")

        # Custos
        costs = analysis["cost_analysis"]
        if costs["monthly_cost"]:
            self.log(f"\n💰 CUSTOS:")
            self.log(f"   Mensal estimado: R$ {costs['monthly_cost']:.2f}")
            self.log(f"   Anual estimado: R$ {costs['yearly_cost']:.2f}")

        # Anomalias
        anomalies = analysis["anomaly_detection"]
        if anomalies["anomaly_count"] > 0:
            self.log(f"\n⚠️ ANOMALIAS DETECTADAS: {anomalies['anomaly_count']}")
            for anomaly in anomalies["anomalies_found"]:
                self.log(f"   - {anomaly['message']}")

        # Tendências
        trends = analysis["trends"]
        if trends["status"] == "analyzed":
            self.log(f"\n📈 TENDÊNCIA: {trends['message']}")

        # Recomendações
        recommendations = analysis["recommendations"]
        if recommendations:
            self.log(f"\n💡 RECOMENDAÇÕES ({len(recommendations)}):")
            for rec in recommendations:
                self.log(f"\n   [{rec['priority'].upper()}] {rec['title']}")
                self.log(f"   {rec['message']}")

    def _check_critical_alerts(self, analysis: dict):
        """Verificar alertas críticos"""

        critical_alerts = []

        # Verificar anomalias críticas
        anomalies = analysis["anomaly_detection"]
        for anomaly in anomalies.get("anomalies_found", []):
            if anomaly["severity"] == "critical":
                critical_alerts.append(anomaly["message"])

        # Verificar recomendações críticas
        for rec in analysis.get("recommendations", []):
            if rec["priority"] == "critical":
                critical_alerts.append(rec["title"])

        if critical_alerts:
            self.log("\n" + "🚨" * 30)
            self.log("⚠️ ALERTAS CRÍTICOS DETECTADOS!")
            self.log("🚨" * 30)

            for alert in critical_alerts:
                self.log(f"   ⚠️ {alert}")

            self.log("\n💡 AÇÃO NECESSÁRIA:")
            self.log("   Verifique a geladeira imediatamente!")
            self.log("🚨" * 30)

    def schedule_weekly_run(self):
        """Agendar execução semanal (sextas-feiras às 18:00)"""

        self.log("📅 Agendando execução semanal...")
        self.log("⏰ Toda sexta-feira às 18:00")

        # Agendar para sexta-feira às 18:00
        schedule.every().friday.at("18:00").do(self.run_weekly_analysis)

        self.log("✅ Agendamento configurado!")
        self.log("\n🤖 Agente em execução. Aguardando próxima sexta-feira...")
        self.log("   Pressione Ctrl+C para parar")

        # Loop principal
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto

        except KeyboardInterrupt:
            self.log("\n⏹️ Agente parado pelo usuário")

    def run_now(self):
        """Executar análise imediatamente (para testes)"""

        self.log("🚀 Executando análise imediatamente (modo teste)")
        return self.run_weekly_analysis()


def main():
    """Função principal"""

    import argparse

    parser = argparse.ArgumentParser(
        description="Agente Semanal de Monitoramento de Energia"
    )

    parser.add_argument(
        "--now",
        action="store_true",
        help="Executar análise imediatamente (não agendar)",
    )

    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Agendar execução semanal (sextas-feiras 18:00)",
    )

    args = parser.parse_args()

    agent = WeeklyEnergyAgent()

    if args.now:
        # Executar imediatamente
        agent.run_now()

    elif args.schedule:
        # Agendar execução semanal
        agent.schedule_weekly_run()

    else:
        # Padrão: executar agora
        print("🎯 AGENTE SEMANAL DE MONITORAMENTO DE ENERGIA")
        print("=" * 60)
        print()
        print("Opções:")
        print("  --now       Executar análise imediatamente")
        print("  --schedule  Agendar execução semanal (sextas 18:00)")
        print()
        print("Executando análise imediatamente...")
        print()

        agent.run_now()


if __name__ == "__main__":
    main()
