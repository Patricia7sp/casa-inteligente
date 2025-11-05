#!/usr/bin/env python3
"""
Parser de relatórios HTML SmartLife
Extrai dados de consumo de energia dos relatórios
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path


class SmartLifeReportParser:
    """Parser para relatórios HTML do SmartLife"""
    
    def __init__(self):
        self.device_name = "Tomada Inteligente-Geladeira"
        
    def parse_html_report(self, html_content: str) -> Dict:
        """
        Parsear relatório HTML e extrair dados de consumo
        
        Args:
            html_content: Conteúdo HTML do relatório
            
        Returns:
            Dicionário com dados extraídos
        """
        print("📊 PARSEANDO RELATÓRIO HTML")
        print("=" * 60)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extrair dados
        report_data = {
            'device_name': self.device_name,
            'parsed_at': datetime.now().isoformat(),
            'period': self._extract_period(soup),
            'total_consumption': self._extract_total_consumption(soup),
            'daily_consumption': self._extract_daily_consumption(soup),
            'hourly_consumption': self._extract_hourly_consumption(soup),
            'cost_data': self._extract_cost_data(soup),
            'statistics': self._extract_statistics(soup),
            'raw_tables': self._extract_all_tables(soup)
        }
        
        print("✅ Dados extraídos com sucesso!")
        print()
        self._print_summary(report_data)
        
        return report_data
    
    def _extract_period(self, soup: BeautifulSoup) -> Dict:
        """Extrair período do relatório"""
        # Procurar por datas no texto
        text = soup.get_text()
        
        # Padrões de data comuns
        date_patterns = [
            r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',  # 10 de novembro de 2025
            r'(\d{2})/(\d{2})/(\d{4})',  # 10/11/2025
            r'(\d{4})-(\d{2})-(\d{2})',  # 2025-11-10
        ]
        
        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates_found.extend(matches)
        
        return {
            'dates_found': dates_found,
            'raw_text': text[:500]  # Primeiros 500 chars para debug
        }
    
    def _extract_total_consumption(self, soup: BeautifulSoup) -> Dict:
        """Extrair consumo total"""
        # Procurar por valores de kWh
        text = soup.get_text()
        
        # Padrões: "123.45 kWh", "123,45kWh", etc
        kwh_pattern = r'(\d+[.,]\d+)\s*kWh'
        kwh_matches = re.findall(kwh_pattern, text, re.IGNORECASE)
        
        # Padrões de consumo total
        total_patterns = [
            r'total[:\s]+(\d+[.,]\d+)\s*kWh',
            r'consumo\s+total[:\s]+(\d+[.,]\d+)',
            r'(\d+[.,]\d+)\s*kWh\s+total'
        ]
        
        total_consumption = None
        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                total_consumption = float(match.group(1).replace(',', '.'))
                break
        
        return {
            'total_kwh': total_consumption,
            'all_kwh_values': kwh_matches
        }
    
    def _extract_daily_consumption(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrair consumo diário"""
        daily_data = []
        
        # Procurar tabelas
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 2:
                    # Tentar extrair data e consumo
                    cell_texts = [cell.get_text().strip() for cell in cells]
                    
                    # Procurar por padrões de data
                    for i, text in enumerate(cell_texts):
                        # Se parece com data
                        if re.search(r'\d{1,2}/\d{1,2}|\d{1,2}\s+de\s+\w+', text):
                            # Próxima célula pode ser consumo
                            if i + 1 < len(cell_texts):
                                consumption_text = cell_texts[i + 1]
                                
                                # Extrair número
                                match = re.search(r'(\d+[.,]\d+)', consumption_text)
                                if match:
                                    daily_data.append({
                                        'date': text,
                                        'consumption': float(match.group(1).replace(',', '.')),
                                        'unit': 'kWh' if 'kWh' in consumption_text else 'unknown'
                                    })
        
        return daily_data
    
    def _extract_hourly_consumption(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrair consumo por hora (se disponível)"""
        hourly_data = []
        
        # Procurar por padrões de hora
        text = soup.get_text()
        
        # Padrão: "14:00 - 123.45 kWh"
        hourly_pattern = r'(\d{1,2}:\d{2})[:\s-]+(\d+[.,]\d+)'
        matches = re.findall(hourly_pattern, text)
        
        for hour, consumption in matches:
            hourly_data.append({
                'hour': hour,
                'consumption': float(consumption.replace(',', '.'))
            })
        
        return hourly_data
    
    def _extract_cost_data(self, soup: BeautifulSoup) -> Dict:
        """Extrair dados de custo"""
        text = soup.get_text()
        
        # Padrões de moeda: R$ 123,45 ou 123.45
        currency_patterns = [
            r'R\$\s*(\d+[.,]\d+)',
            r'(\d+[.,]\d+)\s*reais',
            r'custo[:\s]+R?\$?\s*(\d+[.,]\d+)'
        ]
        
        costs_found = []
        for pattern in currency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            costs_found.extend(matches)
        
        # Converter para float
        costs_float = [float(c.replace(',', '.')) for c in costs_found]
        
        return {
            'costs_found': costs_float,
            'total_cost': max(costs_float) if costs_float else None,
            'currency': 'BRL'
        }
    
    def _extract_statistics(self, soup: BeautifulSoup) -> Dict:
        """Extrair estatísticas gerais"""
        text = soup.get_text()
        
        stats = {
            'peak_hours': [],
            'average_daily': None,
            'max_consumption': None,
            'min_consumption': None
        }
        
        # Procurar por "pico", "máximo", "mínimo"
        peak_pattern = r'pico[:\s]+(\d{1,2}:\d{2})'
        peak_matches = re.findall(peak_pattern, text, re.IGNORECASE)
        stats['peak_hours'] = peak_matches
        
        # Média diária
        avg_pattern = r'média[:\s]+(\d+[.,]\d+)'
        avg_match = re.search(avg_pattern, text, re.IGNORECASE)
        if avg_match:
            stats['average_daily'] = float(avg_match.group(1).replace(',', '.'))
        
        return stats
    
    def _extract_all_tables(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrair todas as tabelas do HTML"""
        tables_data = []
        
        tables = soup.find_all('table')
        
        for idx, table in enumerate(tables):
            table_data = {
                'table_index': idx,
                'headers': [],
                'rows': []
            }
            
            # Extrair headers
            headers = table.find_all('th')
            table_data['headers'] = [h.get_text().strip() for h in headers]
            
            # Extrair linhas
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if cells:
                    table_data['rows'].append([
                        cell.get_text().strip() for cell in cells
                    ])
            
            tables_data.append(table_data)
        
        return tables_data
    
    def _print_summary(self, data: Dict):
        """Imprimir resumo dos dados extraídos"""
        print("📋 RESUMO DOS DADOS EXTRAÍDOS:")
        print("-" * 60)
        
        if data['total_consumption']['total_kwh']:
            print(f"⚡ Consumo Total: {data['total_consumption']['total_kwh']} kWh")
        
        if data['cost_data']['total_cost']:
            print(f"💰 Custo Total: R$ {data['cost_data']['total_cost']:.2f}")
        
        if data['daily_consumption']:
            print(f"📅 Dias com dados: {len(data['daily_consumption'])}")
        
        if data['hourly_consumption']:
            print(f"🕐 Horas com dados: {len(data['hourly_consumption'])}")
        
        if data['statistics']['peak_hours']:
            print(f"⏰ Horários de pico: {', '.join(data['statistics']['peak_hours'])}")
        
        print()
    
    def save_parsed_data(self, data: Dict, output_dir: str = 'data/parsed'):
        """Salvar dados parseados em JSON"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"parsed_report_{timestamp}.json"
        filepath = Path(output_dir) / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Dados salvos: {filepath}")
        
        return str(filepath)
    
    def convert_to_dataframe(self, data: Dict) -> pd.DataFrame:
        """Converter dados para DataFrame pandas"""
        
        if not data['daily_consumption']:
            print("⚠️ Sem dados diários para converter")
            return pd.DataFrame()
        
        df = pd.DataFrame(data['daily_consumption'])
        
        # Tentar converter data
        try:
            df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')
        except:
            print("⚠️ Não foi possível converter datas")
        
        return df


def main():
    """Função de teste"""
    print("🎯 TESTE - PARSER DE RELATÓRIOS SMARTLIFE")
    print("=" * 60)
    print()
    
    # Procurar relatório mais recente
    reports_dir = Path('data/reports')
    
    if not reports_dir.exists():
        print("❌ Diretório de relatórios não encontrado")
        print("💡 Execute primeiro: python src/integrations/gmail_client.py")
        return
    
    # Pegar HTML mais recente
    html_files = sorted(reports_dir.glob('*.html'), reverse=True)
    
    if not html_files:
        print("❌ Nenhum relatório HTML encontrado")
        return
    
    latest_html = html_files[0]
    print(f"📄 Processando: {latest_html.name}")
    print()
    
    # Ler HTML
    with open(latest_html, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parsear
    parser = SmartLifeReportParser()
    data = parser.parse_html_report(html_content)
    
    # Salvar dados parseados
    json_path = parser.save_parsed_data(data)
    
    # Converter para DataFrame
    df = parser.convert_to_dataframe(data)
    
    if not df.empty:
        print(f"\n📊 DataFrame criado:")
        print(df.head())
    
    print(f"\n📋 PRÓXIMO PASSO:")
    print(f"   Execute: python src/agents/energy_analyzer.py")
    print(f"   Para analisar os dados extraídos")


if __name__ == "__main__":
    main()
