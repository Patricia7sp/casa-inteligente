#!/usr/bin/env python3
"""
Script para adicionar seus dispositivos TAPO ao sistema
"""

import subprocess
import json
import sys


def add_device_to_system(name, device_type, ip_address, location, equipment):
    """Adicionar dispositivo via API"""

    device_data = {
        "name": name,
        "type": device_type,
        "ip_address": ip_address,
        "location": location,
        "equipment_connected": equipment,
    }

    curl_command = [
        "curl",
        "-X",
        "POST",
        "http://localhost:8000/devices",
        "-H",
        "Content-Type: application/json",
        "-d",
        json.dumps(device_data),
    ]

    print(f"🔌 Adicionando: {name}")
    print(f"   IP: {ip_address}")
    print(f"   Local: {location}")
    print(f"   Equipamento: {equipment}")
    print()

    try:
        result = subprocess.run(
            curl_command, capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            print("✅ Dispositivo adicionado com sucesso!")
            print(f"   Resposta: {result.stdout}")
        else:
            print("❌ Erro ao adicionar dispositivo")
            print(f"   Erro: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("❌ Timeout - verifique se o sistema está rodando")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

    print("-" * 50)


def main():
    """Função principal"""
    print("🏠 ADICIONANDO SEUS DISPOSITIVOS TAPO")
    print("=" * 60)
    print()

    # Seus dispositivos
    devices = [
        {
            "name": "Tomada Inteligente - Purificador",
            "type": "TAPO",
            "ip_address": "192.168.68.110",
            "location": "Quarto",
            "equipment": "Purificador de Ar",
        },
        {
            "name": "Tomada Inteligente - Notebook",
            "type": "TAPO",
            "ip_address": "192.168.68.108",
            "location": "Escritório",
            "equipment": "Notebook Dell",
        },
    ]

    print("📋 Lista de dispositivos para adicionar:")
    for i, device in enumerate(devices, 1):
        print(f"   {i}. {device['name']} ({device['ip_address']})")
    print()

    # Verificar se o sistema está rodando
    print("🔍 Verificando se o sistema está online...")
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:8000/health"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            print("✅ Sistema online!")
        else:
            print("❌ Sistema offline - inicie com: docker-compose up -d")
            return

    except:
        print("❌ Sistema offline - inicie com: docker-compose up -d")
        return

    print()

    # Adicionar cada dispositivo
    for device in devices:
        add_device_to_system(
            device["name"],
            device["type"],
            device["ip_address"],
            device["location"],
            device["equipment"],
        )

    print()
    print("🎉 PROCESSO CONCLUÍDO!")
    print()
    print("📊 Para verificar os dispositivos adicionados:")
    print("curl http://localhost:8000/devices")
    print()
    print("📈 Para acessar o dashboard:")
    print("http://localhost:8501")
    print()
    print("🔧 Para iniciar o coletor de dados:")
    print("docker-compose restart app")


if __name__ == "__main__":
    main()
