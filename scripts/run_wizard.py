#!/usr/bin/env python3
"""
Executar tinytuya wizard automaticamente com as credenciais
"""

import subprocess
import os
from pathlib import Path


def setup_tinytuya_wizard():
    """Configurar tinytuya wizard automaticamente"""
    print("🧙 CONFIGURANDO TINYTUYA WIZARD")
    print("=" * 60)

    # Credenciais Cloud
    api_id = "nwykv3tnwx5na9kvyjvu"
    api_secret = "021747b14008401f9f173dc693113aef"
    region = "us"
    device_id = "eb0254d3ac39b4d2740fwq"

    print("📋 Credenciais Cloud:")
    print(f"   API ID: {api_id}")
    print(f"   API Secret: {api_secret[:10]}...")
    print(f"   Region: {region}")
    print(f"   Device ID: {device_id}")
    print()

    print("🔄 Executando wizard...")
    print("   (Isso pode levar alguns minutos)")
    print()

    # Preparar input para o wizard
    wizard_input = f"{api_id}\n{api_secret}\n{region}\n"

    try:
        # Executar wizard
        result = subprocess.run(
            ["python", "-m", "tinytuya", "wizard"],
            input=wizard_input,
            capture_output=True,
            text=True,
            timeout=120,
        )

        print(result.stdout)

        if result.returncode == 0:
            print("\n✅ Wizard concluído!")

            # Verificar se criou arquivo de dispositivos
            devices_file = Path("devices.json")
            if devices_file.exists():
                print(f"✅ Arquivo devices.json criado!")

                import json

                with open(devices_file, "r") as f:
                    devices = json.load(f)

                print(f"\n📱 Dispositivos encontrados: {len(devices)}")

                for device in devices:
                    print(f"\n   📱 {device.get('name', 'Unknown')}")
                    print(f"      ID: {device.get('id')}")
                    print(f"      IP: {device.get('ip')}")
                    print(f"      Key: {device.get('key', 'N/A')}")

                    if device.get("id") == device_id:
                        local_key = device.get("key")
                        if local_key:
                            print(f"\n🎉 LOCAL KEY ENCONTRADA!")
                            print(f"✅ Key: {local_key}")
                            return local_key
            else:
                print(f"⏳ Arquivo devices.json não criado")
        else:
            print(f"\n❌ Erro no wizard:")
            print(result.stderr)

    except subprocess.TimeoutExpired:
        print(f"❌ Wizard timeout (120s)")
    except Exception as e:
        print(f"❌ Erro: {e}")

    return None


def main():
    """Função principal"""
    print("🎯 TINYTUYA WIZARD AUTOMÁTICO")
    print("=" * 60)

    local_key = setup_tinytuya_wizard()

    if local_key:
        print(f"\n🎉 SUCESSO!")
        print(f"✅ Local Key: {local_key}")
        print(f"\n📋 Configure no .env:")
        print(f"TUYA_LOCAL_KEY={local_key}")
        print(f"\n📋 Execute:")
        print(f"   python scripts/monitor_energy.py")
    else:
        print(f"\n⏳ Wizard não conseguiu obter Local Key")
        print(f"\n💡 ALTERNATIVA FINAL:")
        print(f"   1. Acesse: https://iot.tuya.com/")
        print(f"   2. Login: paty7sp@gmail.com")
        print(f"   3. Cloud > Development > Casa Inteligente")
        print(f"   4. Devices > sua tomada > Device Details")
        print(f"   5. Copie Local Key (32 caracteres)")
        print(f"\n   Depois execute:")
        print(f"   python scripts/configure_manual_key.py")


if __name__ == "__main__":
    main()
