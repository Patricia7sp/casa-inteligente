#!/usr/bin/env python3
"""
Testar se a LLM está acessando o Supabase corretamente
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.llm_service import llm_service

def main():
    print("🧪 Testando acesso da LLM ao Supabase...")
    print()
    
    # Obter contexto do sistema
    context = llm_service.get_system_context()
    
    print("=" * 80)
    print("📊 CONTEXTO DO SISTEMA")
    print("=" * 80)
    print(context)
    print()
    
    # Verificar se tem dados
    if "Dispositivos Monitorados: 0" in context:
        print("❌ PROBLEMA: Nenhum dispositivo encontrado!")
    elif "Total de Leituras no Banco: 0" in context:
        print("❌ PROBLEMA: Nenhuma leitura encontrada!")
    else:
        print("✅ LLM tem acesso aos dados do Supabase!")
        
        # Contar dispositivos e leituras
        import re
        devices_match = re.search(r'Dispositivos Monitorados: (\d+)', context)
        readings_match = re.search(r'Total de Leituras no Banco: (\d+)', context)
        
        if devices_match and readings_match:
            devices = int(devices_match.group(1))
            readings = int(readings_match.group(1))
            print(f"   📱 {devices} dispositivos")
            print(f"   📊 {readings} leituras")

if __name__ == "__main__":
    main()
