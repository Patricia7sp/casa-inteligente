#!/usr/bin/env python3
"""
Analisador de Consumo de Energia
Detecta anomalias, calcula custos e gera insights
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import statistics


class EnergyAnalyzer:
    """Analisador de consumo de energia com detecção de anomalias"""

    def __init__(self, tariff_kwh: float = 0.85):
        """
        Args:
            tariff_kwh: Tarifa por kWh em R$ (padrão: R$ 0,85)
        """
        self.tariff_kwh = tariff_kwh
        self.device_name = "Geladeira"

        # Parâmetros de consumo normal para geladeira
        self.normal_daily_range = (0.8, 2.5)  # kWh por dia
        self.normal_monthly_range = (24, 75)  # kWh por mês

    def analyze_report(self, parsed_data: Dict) -> Dict:
        """
        Analisar relatório completo
        
        Args:
            parsed_data: Dados parseados do relatório
            
        Returns:
            Análise completa com insights
        """
        print("🔍 ANALISANDO CONSUMO DE ENERGIA")
        print("=" * 60)
        print(f"📱 Dispositivo: {self.device_name}")
        print(f"💰 Tarifa: R$ {self.tariff_kwh:.2f}/kWh")
        print()

        analysis = {
            "device": self.device_name,
            "analyzed_at": datetime.now().isoformat(),
            "tariff_kwh": self.tariff_kwh,
            "consumption_analysis": self._analyze_consumption(parsed_data),
            "cost_analysis": self._analyze_costs(parsed_data),
            "anomaly_detection": self._detect_anomalies(parsed_data),
            "peak_hours_analysis": self._analyze_peak_hours(parsed_data),
            "trends": self._analyze_trends(parsed_data),
            "recommendations": [],
        }

        # Gerar recomendações
        analysis["recommendations"] = self._generate_recommendations(analysis)

        # Imprimir resumo
        self._print_analysis_summary(analysis)

        return analysis

    def _analyze_consumption(self, data: Dict) -> Dict:
        """Analisar padrões de consumo"""

        total_kwh = data["total_consumption"].get("total_kwh", 0)
        daily_data = data.get("daily_consumption", [])

        if not daily_data:
            return {
                "total_kwh": total_kwh,
                "daily_average": None,
                "status": "insufficient_data",
            }

        # Calcular médias
        daily_consumptions = [d["consumption"] for d in daily_data]

        daily_avg = statistics.mean(daily_consumptions)
        daily_median = statistics.median(daily_consumptions)
        daily_std = (
            statistics.stdev(daily_consumptions) if len(daily_consumptions) > 1 else 0
        )

        # Projetar consumo mensal
        monthly_projection = daily_avg * 30

        # Verificar se está normal
        is_normal = (
            self.normal_daily_range[0] <= daily_avg <= self.normal_daily_range[1]
        )

        return {
            "total_kwh": total_kwh,
            "days_analyzed": len(daily_data),
            "daily_average": round(daily_avg, 2),
            "daily_median": round(daily_median, 2),
            "daily_std": round(daily_std, 2),
            "monthly_projection": round(monthly_projection, 2),
            "is_normal": is_normal,
            "status": "normal" if is_normal else "high_consumption",
        }

    def _analyze_costs(self, data: Dict) -> Dict:
        """Analisar custos"""

        consumption = self._analyze_consumption(data)

        if not consumption["daily_average"]:
            return {"daily_cost": None, "monthly_cost": None, "yearly_cost": None}

        # Calcular custos
        daily_cost = consumption["daily_average"] * self.tariff_kwh
        monthly_cost = consumption["monthly_projection"] * self.tariff_kwh
        yearly_cost = monthly_cost * 12

        return {
            "daily_cost": round(daily_cost, 2),
            "monthly_cost": round(monthly_cost, 2),
            "yearly_cost": round(yearly_cost, 2),
            "currency": "BRL",
        }

    def _detect_anomalies(self, data: Dict) -> Dict:
        """Detectar anomalias no consumo"""

        daily_data = data.get("daily_consumption", [])

        if len(daily_data) < 3:
            return {
                "anomalies_found": [],
                "anomaly_count": 0,
                "status": "insufficient_data",
            }

        consumptions = [d["consumption"] for d in daily_data]

        # Calcular limites usando IQR (Interquartile Range)
        q1 = np.percentile(consumptions, 25)
        q3 = np.percentile(consumptions, 75)
        iqr = q3 - q1

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        # Detectar anomalias
        anomalies = []
        for d in daily_data:
            consumption = d["consumption"]

            if consumption < lower_bound:
                anomalies.append(
                    {
                        "date": d["date"],
                        "consumption": consumption,
                        "type": "low",
                        "severity": "warning",
                        "message": f"Consumo muito baixo: {consumption} kWh",
                    }
                )

            elif consumption > upper_bound:
                anomalies.append(
                    {
                        "date": d["date"],
                        "consumption": consumption,
                        "type": "high",
                        "severity": "critical"
                        if consumption > upper_bound * 1.5
                        else "warning",
                        "message": f"Consumo muito alto: {consumption} kWh",
                    }
                )

        return {
            "anomalies_found": anomalies,
            "anomaly_count": len(anomalies),
            "lower_bound": round(lower_bound, 2),
            "upper_bound": round(upper_bound, 2),
            "status": "anomalies_detected" if anomalies else "normal",
        }

    def _analyze_peak_hours(self, data: Dict) -> Dict:
        """Analisar horários de pico"""

        hourly_data = data.get("hourly_consumption", [])

        if not hourly_data:
            return {"peak_hours": [], "status": "no_hourly_data"}

        # Ordenar por consumo
        sorted_hours = sorted(hourly_data, key=lambda x: x["consumption"], reverse=True)

        # Top 3 horários de pico
        peak_hours = sorted_hours[:3]

        return {
            "peak_hours": peak_hours,
            "peak_count": len(peak_hours),
            "status": "analyzed",
        }

    def _analyze_trends(self, data: Dict) -> Dict:
        """Analisar tendências de consumo"""

        daily_data = data.get("daily_consumption", [])

        if len(daily_data) < 5:
            return {"trend": "unknown", "status": "insufficient_data"}

        # Calcular tendência simples (primeira vs segunda metade)
        mid_point = len(daily_data) // 2

        first_half = [d["consumption"] for d in daily_data[:mid_point]]
        second_half = [d["consumption"] for d in daily_data[mid_point:]]

        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)

        # Determinar tendência
        diff_percent = ((avg_second - avg_first) / avg_first) * 100

        if abs(diff_percent) < 5:
            trend = "stable"
            trend_message = "Consumo estável"
        elif diff_percent > 0:
            trend = "increasing"
            trend_message = f"Consumo aumentando ({diff_percent:.1f}%)"
        else:
            trend = "decreasing"
            trend_message = f"Consumo diminuindo ({abs(diff_percent):.1f}%)"

        return {
            "trend": trend,
            "trend_percent": round(diff_percent, 2),
            "message": trend_message,
            "avg_first_period": round(avg_first, 2),
            "avg_second_period": round(avg_second, 2),
            "status": "analyzed",
        }

    def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Gerar recomendações baseadas na análise"""

        recommendations = []

        # Recomendações baseadas em consumo
        consumption = analysis["consumption_analysis"]

        if consumption["status"] == "high_consumption":
            recommendations.append(
                {
                    "type": "high_consumption",
                    "priority": "high",
                    "title": "Consumo acima do normal",
                    "message": f'Geladeira consumindo {consumption["daily_average"]} kWh/dia (normal: {self.normal_daily_range[0]}-{self.normal_daily_range[1]} kWh)',
                    "actions": [
                        "Verificar vedação da porta",
                        "Limpar serpentinas",
                        "Verificar temperatura configurada",
                        "Considerar manutenção técnica",
                    ],
                }
            )

        # Recomendações baseadas em anomalias
        anomalies = analysis["anomaly_detection"]

        if anomalies["anomaly_count"] > 0:
            critical_anomalies = [
                a for a in anomalies["anomalies_found"] if a["severity"] == "critical"
            ]

            if critical_anomalies:
                recommendations.append(
                    {
                        "type": "critical_anomaly",
                        "priority": "critical",
                        "title": "Anomalias críticas detectadas",
                        "message": f"{len(critical_anomalies)} dias com consumo anormal",
                        "actions": [
                            "Verificar funcionamento da geladeira",
                            "Checar se porta está fechando corretamente",
                            "Verificar se há gelo excessivo no freezer",
                            "Considerar chamar técnico",
                        ],
                    }
                )

        # Recomendações baseadas em tendências
        trends = analysis["trends"]

        if trends["trend"] == "increasing" and trends["trend_percent"] > 10:
            recommendations.append(
                {
                    "type": "increasing_trend",
                    "priority": "medium",
                    "title": "Consumo em tendência de alta",
                    "message": f'Consumo aumentou {trends["trend_percent"]:.1f}% no período',
                    "actions": [
                        "Monitorar consumo nas próximas semanas",
                        "Verificar se há problemas mecânicos",
                        "Avaliar necessidade de manutenção preventiva",
                    ],
                }
            )

        # Recomendações de economia
        costs = analysis["cost_analysis"]

        if costs["monthly_cost"] and costs["monthly_cost"] > 50:
            recommendations.append(
                {
                    "type": "cost_optimization",
                    "priority": "low",
                    "title": "Oportunidade de economia",
                    "message": f'Custo mensal estimado: R$ {costs["monthly_cost"]:.2f}',
                    "actions": [
                        "Ajustar temperatura para nível adequado (3-5°C)",
                        "Evitar abrir porta desnecessariamente",
                        "Manter geladeira afastada da parede",
                        "Não colocar alimentos quentes",
                    ],
                }
            )

        return recommendations

    def _print_analysis_summary(self, analysis: Dict):
        """Imprimir resumo da análise"""

        print("=" * 60)
        print("📊 RESUMO DA ANÁLISE")
        print("=" * 60)

        # Consumo
        consumption = analysis["consumption_analysis"]
        print(f"\n⚡ CONSUMO:")
        print(f"   Média diária: {consumption.get('daily_average', 'N/A')} kWh")
        print(f"   Projeção mensal: {consumption.get('monthly_projection', 'N/A')} kWh")
        print(f"   Status: {consumption['status']}")

        # Custos
        costs = analysis["cost_analysis"]
        if costs["monthly_cost"]:
            print(f"\n💰 CUSTOS:")
            print(f"   Diário: R$ {costs['daily_cost']:.2f}")
            print(f"   Mensal: R$ {costs['monthly_cost']:.2f}")
            print(f"   Anual: R$ {costs['yearly_cost']:.2f}")

        # Anomalias
        anomalies = analysis["anomaly_detection"]
        if anomalies["anomaly_count"] > 0:
            print(f"\n⚠️ ANOMALIAS:")
            print(f"   Detectadas: {anomalies['anomaly_count']}")
            for anomaly in anomalies["anomalies_found"][:3]:
                print(f"   - {anomaly['message']}")

        # Tendências
        trends = analysis["trends"]
        if trends["status"] == "analyzed":
            print(f"\n📈 TENDÊNCIA:")
            print(f"   {trends['message']}")

        # Recomendações
        recommendations = analysis["recommendations"]
        if recommendations:
            print(f"\n💡 RECOMENDAÇÕES:")
            for rec in recommendations[:3]:
                print(f"\n   [{rec['priority'].upper()}] {rec['title']}")
                print(f"   {rec['message']}")

        print("\n" + "=" * 60)

    def save_analysis(self, analysis: Dict, output_dir: str = "data/analysis"):
        """Salvar análise em arquivo"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"energy_analysis_{timestamp}.json"
        filepath = Path(output_dir) / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Análise salva: {filepath}")

        return str(filepath)


def main():
    """Função de teste"""
    print("🎯 TESTE - ANÁLISE DE CONSUMO DE ENERGIA")
    print("=" * 60)
    print()

    # Procurar dados parseados mais recentes
    parsed_dir = Path("data/parsed")

    if not parsed_dir.exists():
        print("❌ Diretório de dados parseados não encontrado")
        print("💡 Execute primeiro: python src/integrations/smartlife_parser.py")
        return

    # Pegar JSON mais recente
    json_files = sorted(parsed_dir.glob("*.json"), reverse=True)

    if not json_files:
        print("❌ Nenhum dado parseado encontrado")
        return

    latest_json = json_files[0]
    print(f"📄 Analisando: {latest_json.name}")
    print()

    # Carregar dados
    with open(latest_json, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

    # Analisar
    analyzer = EnergyAnalyzer(tariff_kwh=0.85)
    analysis = analyzer.analyze_report(parsed_data)

    # Salvar análise
    analyzer.save_analysis(analysis)

    print(f"\n✅ Análise completa!")


if __name__ == "__main__":
    main()
