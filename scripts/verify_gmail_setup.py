#!/usr/bin/env python3
"""
Verificar se a configuração do Gmail API está completa
"""

import os
import json
from pathlib import Path


def verify_setup():
    """Verificar configuração"""

    print("🔍 VERIFICANDO CONFIGURAÇÃO DO GMAIL API")
    print("=" * 60)
    print()

    all_ok = True

    # 1. Verificar diretórios
    print("1️⃣ VERIFICANDO DIRETÓRIOS")
    print("-" * 40)

    directories = ["config", "data/reports", "data/parsed", "data/analysis", "logs"]

    for dir_path in directories:
        if Path(dir_path).exists():
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ❌ {dir_path} (faltando)")
            all_ok = False

    # 2. Verificar credenciais
    print("\n2️⃣ VERIFICANDO CREDENCIAIS")
    print("-" * 40)

    credentials_file = Path("config/gmail_credentials.json")

    if credentials_file.exists():
        print(f"   ✅ Arquivo de credenciais existe")

        try:
            with open(credentials_file, "r") as f:
                creds = json.load(f)

            if "installed" in creds or "web" in creds:
                print(f"   ✅ Arquivo JSON válido")

                # Mostrar informações
                if "installed" in creds:
                    client_id = creds["installed"].get("client_id", "N/A")
                    print(f"   📋 Client ID: {client_id[:20]}...")
                elif "web" in creds:
                    client_id = creds["web"].get("client_id", "N/A")
                    print(f"   📋 Client ID: {client_id[:20]}...")
            else:
                print(f"   ⚠️ Arquivo JSON não parece ser de credenciais OAuth")
                all_ok = False

        except json.JSONDecodeError:
            print(f"   ❌ Arquivo JSON inválido")
            all_ok = False
    else:
        print(f"   ❌ Arquivo de credenciais não encontrado")
        print(f"   📁 Esperado em: {credentials_file.absolute()}")
        all_ok = False

    # 3. Verificar token (se existir)
    print("\n3️⃣ VERIFICANDO TOKEN DE AUTENTICAÇÃO")
    print("-" * 40)

    token_file = Path("config/gmail_token.pickle")

    if token_file.exists():
        print(f"   ✅ Token existe (já autenticado)")
    else:
        print(f"   ⚠️ Token não existe (precisa autenticar)")
        print(f"   💡 Execute: python src/integrations/gmail_client.py")

    # 4. Verificar dependências
    print("\n4️⃣ VERIFICANDO DEPENDÊNCIAS")
    print("-" * 40)

    required_packages = [
        "google.oauth2",
        "googleapiclient",
        "bs4",
        "pandas",
        "schedule",
    ]

    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (não instalado)")
            all_ok = False

    # 5. Verificar scripts
    print("\n5️⃣ VERIFICANDO SCRIPTS")
    print("-" * 40)

    scripts = [
        "src/integrations/gmail_client.py",
        "src/integrations/smartlife_parser.py",
        "src/agents/energy_analyzer.py",
        "src/agents/weekly_energy_agent.py",
    ]

    for script in scripts:
        if Path(script).exists():
            print(f"   ✅ {script}")
        else:
            print(f"   ❌ {script} (faltando)")
            all_ok = False

    # Resultado final
    print("\n" + "=" * 60)

    if all_ok:
        print("✅ CONFIGURAÇÃO COMPLETA!")
        print("=" * 60)
        print()
        print("📋 PRÓXIMOS PASSOS:")
        print()

        if not token_file.exists():
            print("1. Autenticar com Gmail:")
            print("   python src/integrations/gmail_client.py")
            print()
            print("2. Testar sistema:")
            print("   python src/agents/weekly_energy_agent.py --now")
        else:
            print("1. Testar sistema:")
            print("   python src/agents/weekly_energy_agent.py --now")
            print()
            print("2. Agendar execução semanal:")
            print("   python src/agents/weekly_energy_agent.py --schedule")
    else:
        print("⚠️ CONFIGURAÇÃO INCOMPLETA")
        print("=" * 60)
        print()
        print("💡 AÇÕES NECESSÁRIAS:")
        print()

        if not credentials_file.exists():
            print("1. Configurar Gmail API:")
            print("   python scripts/open_gmail_setup.py")
            print()
            print("2. Baixar credenciais e salvar em:")
            print(f"   {credentials_file.absolute()}")

        print()
        print("3. Verificar novamente:")
        print("   python scripts/verify_gmail_setup.py")

    print()

    return all_ok


if __name__ == "__main__":
    verify_setup()
