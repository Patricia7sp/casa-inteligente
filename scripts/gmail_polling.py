#!/usr/bin/env python3
"""
Polling inteligente para processar emails SmartLife em tempo real
Roda continuamente, verificando novos emails a cada 5 minutos
"""

import sys
import os
from pathlib import Path
import json
import pickle
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
import re
import base64

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

print("🔄 POLLING INTELIGENTE - SMARTLIFE")
print("=" * 60)
print()

# Carregar token
token_file = Path("config/gmail_token.pickle")

with open(token_file, "rb") as f:
    creds = pickle.load(f)

service = build("gmail", "v1", credentials=creds)

# Arquivo para rastrear emails processados
processed_file = Path("data/smartlife/processed_emails.json")
processed_file.parent.mkdir(parents=True, exist_ok=True)

if processed_file.exists():
    with open(processed_file, "r") as f:
        processed_ids = set(json.load(f))
else:
    processed_ids = set()

print(f"📋 Emails já processados: {len(processed_ids)}")
print()
print("🔄 Iniciando monitoramento...")
print("   Verificando a cada 5 minutos")
print("   Pressione Ctrl+C para parar")
print()


def get_html_content(payload):
    """Extrair HTML do payload"""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/html":
                if "data" in part["body"]:
                    return base64.urlsafe_b64decode(part["body"]["data"]).decode(
                        "utf-8"
                    )
            elif "parts" in part:
                html = get_html_content(part)
                if html:
                    return html
    elif payload.get("mimeType") == "text/html" and "data" in payload.get("body", {}):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
    return None


def process_email(msg_id):
    """Processar email SmartLife"""

    try:
        # Obter email
        message = (
            service.users()
            .messages()
            .get(userId="me", id=msg_id, format="full")
            .execute()
        )

        # Headers
        headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}
        subject = headers.get("Subject", "")
        date = headers.get("Date", "")

        print(f"   📧 Novo email: {subject[:50]}...")
        print(f"   📅 Data: {date}")

        # Extrair HTML
        html_content = get_html_content(message["payload"])

        if not html_content:
            print(f"   ⚠️  Sem HTML")
            return False

        soup = BeautifulSoup(html_content, "html.parser")

        # Extrair link
        link = None
        for a in soup.find_all("a", href=True):
            if "airtake-private-data" in a["href"] or "smartenergy" in a["href"]:
                link = a["href"]
                break

        if not link:
            print(f"   ⚠️  Link não encontrado")
            return False

        print(f"   🔗 Link encontrado")

        # Baixar relatório
        print(f"   ⬇️  Baixando relatório...")

        response = requests.get(link, timeout=30)
        response.raise_for_status()

        report_html = response.text

        print(f"   ✅ Baixado ({len(report_html)} bytes)")

        # Salvar HTML
        data_dir = Path("data/smartlife")
        html_file = data_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(report_html)

        print(f"   💾 Salvo: {html_file}")

        # Parsear dados
        soup = BeautifulSoup(report_html, "html.parser")
        text = soup.get_text()

        # Extrair consumo
        kwh_matches = re.findall(r"(\d+\.?\d*)\s*kWh", text, re.IGNORECASE)
        cost_matches = re.findall(r"R\$\s*(\d+[.,]?\d*)", text)

        consumption = float(kwh_matches[0]) if kwh_matches else 0
        cost = float(cost_matches[0].replace(",", ".")) if cost_matches else 0

        # Salvar dados
        system_data = {
            "source": "smartlife_email",
            "device_id": "nova_digital_refrigerator",
            "device_name": "Geladeira Nova Digital",
            "timestamp": datetime.now().isoformat(),
            "email_date": date,
            "metrics": {
                "total_consumption_kwh": consumption,
                "total_cost_brl": cost,
                "daily_average_kwh": round(consumption / 7, 2),
                "status": "normal",
            },
            "html_file": str(html_file),
        }

        data_file = data_dir / f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(system_data, f, indent=2, ensure_ascii=False)

        # Atualizar latest
        latest_file = data_dir / "latest.json"
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(system_data, f, indent=2, ensure_ascii=False)

        print(f"   ✅ Dados salvos: {data_file}")

        if consumption > 0:
            print(f"   ⚡ Consumo: {consumption} kWh")
        if cost > 0:
            print(f"   💰 Custo: R$ {cost:.2f}")

        print(f"   ✅ PROCESSADO COM SUCESSO!")

        return True

    except Exception as e:
        print(f"   ❌ Erro: {e}")
        import traceback

        traceback.print_exc()
        return False


try:
    while True:
        # Buscar novos emails
        results = (
            service.users()
            .messages()
            .list(
                userId="me",
                q='from:notice.2.ismartlife.me subject:"consumo de energia"',
                maxResults=5,
            )
            .execute()
        )

        messages = results.get("messages", [])

        # Processar novos
        new_count = 0

        for msg in messages:
            msg_id = msg["id"]

            if msg_id not in processed_ids:
                print(f"\n🆕 NOVO EMAIL DETECTADO!")
                print("-" * 60)

                if process_email(msg_id):
                    processed_ids.add(msg_id)
                    new_count += 1

                print("-" * 60)

        # Salvar IDs processados
        with open(processed_file, "w") as f:
            json.dump(list(processed_ids), f)

        if new_count > 0:
            print(f"\n✅ {new_count} novo(s) email(s) processado(s)")

        # Aguardar 5 minutos
        print(
            f"\n⏰ Próxima verificação em 5 minutos... ({datetime.now().strftime('%H:%M:%S')})"
        )
        time.sleep(300)  # 5 minutos

except KeyboardInterrupt:
    print("\n\n⏹️  Polling parado pelo usuário")
    print(f"📊 Total processados: {len(processed_ids)}")
