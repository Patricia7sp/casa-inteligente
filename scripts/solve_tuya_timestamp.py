#!/usr/bin/env python3
"""
Solução final para erro de timestamp Tuya
"""

import asyncio
import aiohttp
import json
import hashlib
import time
import hmac
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from utils.config import settings


async def test_adaptive_timestamp():
    """Testar com timestamp adaptativo"""
    print("🎯 SOLUÇÃO ADAPTATIVA TIMESTAMP")
    print("=" * 50)

    access_id = getattr(settings, "tuya_access_id", None)
    access_key = getattr(settings, "tuya_access_key", None)
    region = getattr(settings, "tuya_region", "us")

    if not all([access_id, access_key]):
        print("❌ Configurações não encontradas")
        return

    base_url = f"https://openapi.tuya{region}.com"

    try:
        async with aiohttp.ClientSession() as session:

            # Testar diferentes offsets de forma adaptativa
            offsets = [-3000, -2000, -1500, -1000, -500, 0, 500, 1000, 1500, 2000, 3000]

            print("🔍 Testando offsets adaptativos...")

            for offset in offsets:
                for attempt in range(2):  # 2 tentativas por offset
                    corrected_time = int(time.time() * 1000) + offset
                    timestamp = str(corrected_time)
                    path = "/v1.0/token?grant_type=1"
                    string_to_sign = f"GET\napplication/json\n{timestamp}\n{path}"

                    signature = hmac.new(
                        access_key.encode("utf-8"),
                        string_to_sign.encode("utf-8"),
                        hashlib.sha256,
                    ).hexdigest()

                    headers = {
                        "Content-Type": "application/json",
                        "X-T": timestamp,
                        "client_id": access_id,
                        "sign": signature.upper(),
                        "sign_method": "HMAC-SHA256",
                    }

                    async with session.get(
                        f"{base_url}{path}", headers=headers, timeout=10
                    ) as response:
                        result = await response.json()

                        if result.get("success"):
                            print(f"   ✅ SUCESSO com offset {offset}ms!")
                            print(
                                f"   🎉 Token: {result['result']['access_token'][:20]}..."
                            )

                            # Salvar offset funcionando
                            print(f"\n💡 SOLUÇÃO ENCONTRADA:")
                            print(f"   Offset ideal: {offset}ms")
                            print(f"   Aplicar correção: timestamp + {offset}ms")

                            # Atualizar o cliente automaticamente
                            await update_client_with_offset(offset)

                            return True
                        else:
                            server_time = result.get("t", 0)
                            diff = server_time - corrected_time
                            print(
                                f"   Offset {offset:>5}: diff={diff:>5}ms - {result.get('msg')}"
                            )

                await asyncio.sleep(0.2)  # Pequena pausa entre offsets

    except Exception as e:
        print(f"❌ Erro: {e}")

    return False


async def update_client_with_offset(offset):
    """Atualizar o cliente com o offset funcionando"""
    try:
        client_file = (
            Path(__file__).parent.parent
            / "src"
            / "integrations"
            / "tuya_cloud_client.py"
        )

        # Ler arquivo atual
        with open(client_file, "r") as f:
            content = f.read()

        # Encontrar e substituir o método _get_timestamp
        old_method = '''    def _get_timestamp(self) -> str:
        """
        Obter timestamp corrigido para API Tuya
        
        Returns:
            str: Timestamp em milissegundos
        """
        # Baseado nos testes: o servidor Tuya consistentemente rejeita timestamps
        # Vou usar uma correção fixa de +2000ms que funcionou nos testes
        return str(int(time.time() * 1000) + 2000)'''

        new_method = f'''    def _get_timestamp(self) -> str:
        """
        Obter timestamp corrigido para API Tuya
        
        Returns:
            str: Timestamp em milissegundos
        """
        # Correção automática baseada em testes adaptativos
        return str(int(time.time() * 1000) + {offset})'''

        if old_method in content:
            content = content.replace(old_method, new_method)

            # Salvar arquivo atualizado
            with open(client_file, "w") as f:
                f.write(content)

            print(f"   ✅ Cliente atualizado com offset {offset}ms")
        else:
            print(f"   ⚠️  Método _get_timestamp não encontrado no formato esperado")

    except Exception as e:
        print(f"   ❌ Erro ao atualizar cliente: {e}")


async def main():
    success = await test_adaptive_timestamp()

    if success:
        print(f"\n✅ PROBLEMA RESOLVIDO!")
        print(f"   🎯 Erro 1013 corrigido")
        print(f"   ⏰ Timestamp sincronizado")
        print(f"   🔄 Cliente atualizado automaticamente")
        print(f"\n📋 Próximos passos:")
        print(f"   1. Execute: python scripts/test_tuya_cloud.py")
        print(f"   2. Confirme que funciona")
        print(f"   3. Integre com seus dispositivos")
    else:
        print(f"\n❌ SOLUÇÃO NÃO ENCONTRADA")
        print(f"   Pode ser necessário:")
        print(f"   1. Verificar configurações do projeto Tuya")
        print(f"   2. Entrar em contato com suporte Tuya")
        print(f"   3. Usar API local como alternativa")


if __name__ == "__main__":
    asyncio.run(main())
