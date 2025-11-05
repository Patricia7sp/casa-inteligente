#!/usr/bin/env python3
"""
Cliente Gmail para buscar relatórios de consumo SmartLife
Busca emails semanalmente e extrai relatórios HTML
"""

import os
import base64
import pickle
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class GmailSmartLifeClient:
    """Cliente para buscar relatórios SmartLife no Gmail"""
    
    # Escopos necessários para ler emails
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self):
        self.service = None
        self.user_email = os.getenv('SMARTLIFE_USERNAME', 'paty7sp@gmail.com')
        
        # Informações do remetente (baseado no print)
        self.sender_email = 'notice.2.ismartlife.me'
        self.sender_domain = 'us-west-2.amazonses.com'
        self.subject_pattern = 'Verifique o relatório de consumo de energia da sua casa'
        
    def authenticate(self):
        """Autenticar com Gmail API"""
        creds = None
        token_path = 'config/gmail_token.pickle'
        credentials_path = 'config/gmail_credentials.json'
        
        # Carregar token salvo se existir
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Se não há credenciais válidas, fazer login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    print("❌ Arquivo de credenciais não encontrado!")
                    print(f"📁 Crie o arquivo: {credentials_path}")
                    print("🔗 Veja: https://developers.google.com/gmail/api/quickstart/python")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Salvar credenciais para próxima execução
            os.makedirs('config', exist_ok=True)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        return True
    
    def search_smartlife_reports(self, days_back: int = 7) -> List[Dict]:
        """
        Buscar relatórios SmartLife dos últimos N dias
        
        Args:
            days_back: Quantos dias para trás buscar (padrão: 7)
            
        Returns:
            Lista de relatórios encontrados
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        print(f"🔍 BUSCANDO RELATÓRIOS SMARTLIFE")
        print("=" * 60)
        print(f"📧 Email: {self.user_email}")
        print(f"📅 Período: Últimos {days_back} dias")
        print()
        
        # Construir query de busca
        # Baseado no print: de "notice.2.ismartlife.me"
        query_parts = [
            f'from:{self.sender_email}',
            f'subject:"{self.subject_pattern}"',
            f'newer_than:{days_back}d'
        ]
        
        query = ' '.join(query_parts)
        
        try:
            # Buscar mensagens
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=50
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print("⚠️ Nenhum relatório encontrado")
                print(f"Query usada: {query}")
                return []
            
            print(f"✅ Encontrados {len(messages)} relatórios")
            print()
            
            # Processar cada mensagem
            reports = []
            for msg in messages:
                report = self._process_message(msg['id'])
                if report:
                    reports.append(report)
            
            return reports
        
        except HttpError as error:
            print(f"❌ Erro ao buscar emails: {error}")
            return []
    
    def _process_message(self, msg_id: str) -> Optional[Dict]:
        """Processar uma mensagem individual"""
        try:
            # Obter mensagem completa
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            # Extrair headers
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            
            # Extrair corpo HTML
            html_content = self._get_html_content(message['payload'])
            
            if not html_content:
                print(f"⚠️ Email sem conteúdo HTML: {subject}")
                return None
            
            print(f"📧 Relatório encontrado:")
            print(f"   Assunto: {subject}")
            print(f"   Data: {date_str}")
            print(f"   De: {sender}")
            print()
            
            return {
                'id': msg_id,
                'subject': subject,
                'date': date_str,
                'sender': sender,
                'html_content': html_content,
                'received_at': datetime.now().isoformat()
            }
        
        except HttpError as error:
            print(f"❌ Erro ao processar mensagem {msg_id}: {error}")
            return None
    
    def _get_html_content(self, payload: Dict) -> Optional[str]:
        """Extrair conteúdo HTML do payload"""
        
        # Se tem partes (multipart)
        if 'parts' in payload:
            for part in payload['parts']:
                # Procurar parte HTML
                if part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                
                # Recursivo para partes aninhadas
                if 'parts' in part:
                    html = self._get_html_content(part)
                    if html:
                        return html
        
        # Se é HTML direto
        elif payload['mimeType'] == 'text/html':
            if 'data' in payload['body']:
                return base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8')
        
        return None
    
    def save_report(self, report: Dict, output_dir: str = 'data/reports'):
        """Salvar relatório em arquivo"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Nome do arquivo baseado na data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"smartlife_report_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)
        
        # Salvar HTML
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report['html_content'])
        
        print(f"💾 Relatório salvo: {filepath}")
        
        return filepath
    
    def get_latest_report(self) -> Optional[Dict]:
        """Obter o relatório mais recente"""
        reports = self.search_smartlife_reports(days_back=7)
        
        if not reports:
            return None
        
        # Retornar o primeiro (mais recente)
        return reports[0]


def main():
    """Função de teste"""
    print("🎯 TESTE - BUSCAR RELATÓRIOS SMARTLIFE NO GMAIL")
    print("=" * 60)
    print()
    
    client = GmailSmartLifeClient()
    
    # Buscar relatórios
    reports = client.search_smartlife_reports(days_back=30)
    
    if reports:
        print(f"\n✅ Total de relatórios: {len(reports)}")
        
        # Salvar o mais recente
        latest = reports[0]
        filepath = client.save_report(latest)
        
        print(f"\n📋 PRÓXIMO PASSO:")
        print(f"   Execute: python src/integrations/smartlife_parser.py")
        print(f"   Para extrair dados do relatório salvo")
    else:
        print("\n⚠️ Nenhum relatório encontrado")
        print("\n💡 VERIFIQUE:")
        print("   1. Credenciais Gmail configuradas")
        print("   2. Relatórios recebidos no email")
        print("   3. Período de busca (padrão: 30 dias)")


if __name__ == "__main__":
    main()
