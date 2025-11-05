"""
Prometheus Exporter para métricas do SmartLife e outros dispositivos
"""

from prometheus_client import start_http_server, Gauge, Counter, Info
import json
import time
from pathlib import Path
from datetime import datetime


class SmartLifePrometheusExporter:
    """Exportador de métricas do SmartLife para Prometheus"""

    def __init__(self, port=9090):
        self.port = port

        # Métricas SmartLife
        self.smartlife_consumption_daily = Gauge(
            "smartlife_consumption_daily_kwh", "Consumo diário da geladeira em kWh"
        )

        self.smartlife_consumption_monthly_projection = Gauge(
            "smartlife_consumption_monthly_projection_kwh",
            "Projeção de consumo mensal em kWh",
        )

        self.smartlife_cost_monthly = Gauge(
            "smartlife_cost_monthly_brl", "Custo mensal estimado em R$"
        )

        self.smartlife_status = Gauge(
            "smartlife_status", "Status do dispositivo (1=normal, 0=alert)"
        )

        self.smartlife_last_update = Gauge(
            "smartlife_last_update_timestamp", "Timestamp da última atualização"
        )

        # Info sobre o dispositivo
        self.smartlife_info = Info(
            "smartlife_device", "Informações do dispositivo SmartLife"
        )

        # Contador de relatórios processados
        self.smartlife_reports_processed = Counter(
            "smartlife_reports_processed_total",
            "Total de relatórios SmartLife processados",
        )

        self.data_file = Path("data/smartlife/latest.json")

    def update_metrics(self):
        """Atualizar métricas com dados mais recentes"""

        if not self.data_file.exists():
            print(f"Arquivo de dados não encontrado: {self.data_file}")
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            metrics = data.get("metrics", {})

            # Atualizar gauges
            self.smartlife_consumption_daily.set(metrics.get("daily_average_kwh", 0))

            self.smartlife_consumption_monthly_projection.set(
                metrics.get("monthly_projection_kwh", 0)
            )

            self.smartlife_cost_monthly.set(
                metrics.get("estimated_monthly_cost_brl", 0)
            )

            # Status (1 = normal, 0 = alert)
            status = 1 if metrics.get("status") == "normal" else 0
            self.smartlife_status.set(status)

            # Timestamp
            timestamp = datetime.fromisoformat(
                data.get("timestamp", datetime.now().isoformat())
            )
            self.smartlife_last_update.set(timestamp.timestamp())

            # Info
            self.smartlife_info.info(
                {
                    "device_id": data.get("device_id", "unknown"),
                    "device_name": data.get("device_name", "unknown"),
                    "source": data.get("source", "unknown"),
                }
            )

            print(f"[{datetime.now()}] Métricas atualizadas:")
            print(f"  Consumo diário: {metrics.get('daily_average_kwh', 0):.2f} kWh")
            print(
                f"  Projeção mensal: {metrics.get('monthly_projection_kwh', 0):.1f} kWh"
            )
            print(
                f"  Custo mensal: R$ {metrics.get('estimated_monthly_cost_brl', 0):.2f}"
            )
            print(f"  Status: {metrics.get('status', 'unknown')}")

        except Exception as e:
            print(f"Erro ao atualizar métricas: {e}")

    def run(self, update_interval=60):
        """Iniciar servidor Prometheus e loop de atualização"""

        print(f"Iniciando Prometheus Exporter na porta {self.port}")
        print(f"Métricas disponíveis em: http://localhost:{self.port}/metrics")
        print(f"Intervalo de atualização: {update_interval}s")
        print()

        # Iniciar servidor HTTP
        start_http_server(self.port)

        # Loop de atualização
        try:
            while True:
                self.update_metrics()
                time.sleep(update_interval)

        except KeyboardInterrupt:
            print("\nExporter parado pelo usuário")


def main():
    """Função principal"""

    import argparse

    parser = argparse.ArgumentParser(description="Prometheus Exporter para SmartLife")

    parser.add_argument(
        "--port",
        type=int,
        default=9090,
        help="Porta do servidor Prometheus (padrão: 9090)",
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Intervalo de atualização em segundos (padrão: 60)",
    )

    args = parser.parse_args()

    exporter = SmartLifePrometheusExporter(port=args.port)
    exporter.run(update_interval=args.interval)


if __name__ == "__main__":
    main()
