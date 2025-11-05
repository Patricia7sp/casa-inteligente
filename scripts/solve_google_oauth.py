#!/usr/bin/env python3
"""
Solução para contas Tuya criadas com Google OAuth
Obter Local Key sem acesso direto à plataforma IoT
"""

import requests
import json
import time
from datetime import datetime


class TuyaGoogleAccountHelper:
    """Helper para contas Tuya com login Google"""
    
    def __init__(self):
        self.device_id = "eb0254d3ac39b4d2740fwq"
        self.device_ip = "192.168.68.100"
    
    def solution_1_create_traditional_account(self):
        """Solução 1: Criar conta tradicional e transferir dispositivo"""
        print("🔐 SOLUÇÃO 1: CRIAR CONTA TRADICIONAL")
        print("=" * 60)
        print()
        print("Passos para criar conta com email/senha:")
        print()
        print("1️⃣ NO APP TUYA SMART:")
        print("   a) Abra Configurações/Settings")
        print("   b) Vá em 'Account and Security'")
        print("   c) Procure por 'Bind Email' ou 'Add Email'")
        print("   d) Adicione um email e senha")
        print("   e) Confirme o email")
        print()
        print("2️⃣ DEPOIS DE VINCULAR EMAIL:")
        print("   a) Acesse: https://iot.tuya.com/")
        print("   b) Faça login com o EMAIL vinculado")
        print("   c) Vá em Devices > Device Details")
        print("   d) Copie a Local Key")
        print()
        print("✅ Isso permite acesso à plataforma IoT!")
        print()
    
    def solution_2_share_device(self):
        """Solução 2: Compartilhar dispositivo com outra conta"""
        print("👥 SOLUÇÃO 2: COMPARTILHAR DISPOSITIVO")
        print("=" * 60)
        print()
        print("Compartilhe o dispositivo com uma conta tradicional:")
        print()
        print("1️⃣ CRIAR NOVA CONTA TUYA:")
        print("   a) Baixe app Tuya Smart em outro celular")
        print("   b) Crie conta com EMAIL e SENHA (não Google)")
        print("   c) Anote email e senha")
        print()
        print("2️⃣ COMPARTILHAR DISPOSITIVO:")
        print("   a) No seu app (conta Google)")
        print("   b) Vá no dispositivo > Configurações")
        print("   c) Procure 'Share' ou 'Compartilhar'")
        print("   d) Compartilhe com o email da nova conta")
        print()
        print("3️⃣ ACESSAR IOT PLATFORM:")
        print("   a) Acesse: https://iot.tuya.com/")
        print("   b) Login com a NOVA conta (email/senha)")
        print("   c) Dispositivo aparecerá compartilhado")
        print("   d) Copie a Local Key")
        print()
    
    def solution_3_api_with_google_token(self):
        """Solução 3: Usar API com token Google"""
        print("🔑 SOLUÇÃO 3: API COM TOKEN GOOGLE")
        print("=" * 60)
        print()
        print("Tentar obter Local Key via API usando token Google:")
        print()
        print("1️⃣ OBTER TOKEN DO APP:")
        print("   a) Instale: pip install mitmproxy")
        print("   b) Configure proxy no celular")
        print("   c) Abra app Tuya Smart")
        print("   d) Capture requisições")
        print("   e) Procure por 'access_token' nos headers")
        print()
        print("2️⃣ USAR TOKEN NA API:")
        print("   Execute: python scripts/api_with_google_token.py")
        print()
    
    def solution_4_reset_and_reconfigure(self):
        """Solução 4: Resetar dispositivo e reconfigurar"""
        print("🔄 SOLUÇÃO 4: RESETAR E RECONFIGURAR")
        print("=" * 60)
        print()
        print("Resetar dispositivo e configurar com conta tradicional:")
        print()
        print("1️⃣ CRIAR CONTA TRADICIONAL:")
        print("   a) Desinstale app Tuya Smart")
        print("   b) Reinstale app")
        print("   c) Crie conta com EMAIL e SENHA (não Google)")
        print()
        print("2️⃣ RESETAR DISPOSITIVO:")
        print("   a) Pressione botão da tomada por 5-10 segundos")
        print("   b) LED deve piscar rapidamente")
        print("   c) Dispositivo volta ao modo de configuração")
        print()
        print("3️⃣ RECONFIGURAR:")
        print("   a) No app, adicione dispositivo")
        print("   b) Siga processo de configuração")
        print("   c) Dispositivo será vinculado à nova conta")
        print()
        print("4️⃣ OBTER LOCAL KEY:")
        print("   a) Acesse: https://iot.tuya.com/")
        print("   b) Login com email/senha")
        print("   c) Copie Local Key")
        print()
        print("⚠️ ATENÇÃO: Você perderá automações configuradas!")
        print()
    
    def solution_5_contact_support(self):
        """Solução 5: Contatar suporte Tuya"""
        print("📞 SOLUÇÃO 5: SUPORTE TUYA")
        print("=" * 60)
        print()
        print("Solicitar Local Key diretamente ao suporte:")
        print()
        print("1️⃣ CONTATO:")
        print("   Email: support@tuya.com")
        print("   Website: https://service.tuya.com/")
        print()
        print("2️⃣ INFORMAÇÕES NECESSÁRIAS:")
        print(f"   Device ID: {self.device_id}")
        print(f"   Device IP: {self.device_ip}")
        print("   Conta: Criada com Google OAuth")
        print("   Problema: Não consigo acessar IoT Platform")
        print()
        print("3️⃣ SOLICITAR:")
        print("   - Local Key do dispositivo")
        print("   - Ou instruções para vincular email")
        print()
    
    def solution_6_alternative_firmware(self):
        """Solução 6: Firmware alternativo"""
        print("⚡ SOLUÇÃO 6: FIRMWARE ALTERNATIVO")
        print("=" * 60)
        print()
        print("Substituir firmware Tuya por alternativa open-source:")
        print()
        print("🔧 TASMOTA:")
        print("   - Firmware open-source para dispositivos ESP")
        print("   - Não precisa de Local Key")
        print("   - Controle total local")
        print("   - Requer flash via serial/OTA")
        print()
        print("🔧 ESPHOME:")
        print("   - Integração com Home Assistant")
        print("   - Configuração via YAML")
        print("   - Totalmente local")
        print()
        print("⚠️ ATENÇÃO:")
        print("   - Requer conhecimento técnico")
        print("   - Pode anular garantia")
        print("   - Risco de brick do dispositivo")
        print()
        print("📚 Guias:")
        print("   - https://tasmota.github.io/")
        print("   - https://esphome.io/")
        print()
    
    def show_all_solutions(self):
        """Mostrar todas as soluções"""
        print("🎯 SOLUÇÕES PARA CONTA GOOGLE OAUTH")
        print("=" * 60)
        print()
        print("Você criou conta com Google e não consegue acessar")
        print("a plataforma IoT para obter a Local Key.")
        print()
        print("Aqui estão TODAS as soluções possíveis:")
        print()
        
        solutions = [
            ("VINCULAR EMAIL", self.solution_1_create_traditional_account, "⭐⭐⭐⭐⭐", "5 min", "Fácil"),
            ("COMPARTILHAR DISPOSITIVO", self.solution_2_share_device, "⭐⭐⭐⭐", "10 min", "Fácil"),
            ("API COM TOKEN", self.solution_3_api_with_google_token, "⭐⭐⭐", "30 min", "Média"),
            ("RESETAR E RECONFIGURAR", self.solution_4_reset_and_reconfigure, "⭐⭐⭐⭐", "15 min", "Fácil"),
            ("CONTATAR SUPORTE", self.solution_5_contact_support, "⭐⭐", "1-3 dias", "Fácil"),
            ("FIRMWARE ALTERNATIVO", self.solution_6_alternative_firmware, "⭐⭐", "2-4 horas", "Difícil")
        ]
        
        print("📊 COMPARAÇÃO:")
        print()
        for i, (name, _, rating, time, difficulty) in enumerate(solutions, 1):
            print(f"{i}. {name}")
            print(f"   Sucesso: {rating}")
            print(f"   Tempo: {time}")
            print(f"   Dificuldade: {difficulty}")
            print()
        
        print("=" * 60)
        print()
        
        # Executar cada solução
        for i, (name, func, _, _, _) in enumerate(solutions, 1):
            print(f"\n{'='*60}")
            print(f"SOLUÇÃO {i}: {name}")
            print(f"{'='*60}\n")
            func()
            input("\nPressione ENTER para ver próxima solução...")


def create_step_by_step_guide():
    """Criar guia passo a passo"""
    guide = """
# 🎯 GUIA PASSO A PASSO - CONTA GOOGLE OAUTH

## ⭐ SOLUÇÃO MAIS RÁPIDA: VINCULAR EMAIL

### **Passo 1: Abrir App Tuya Smart**
```
1. Abra o app Tuya Smart no celular
2. Toque no ícone de perfil (canto inferior direito)
3. Vá em "Account and Security" ou "Conta e Segurança"
```

### **Passo 2: Vincular Email**
```
1. Procure opção "Bind Email" ou "Vincular Email"
2. Digite um email (pode ser qualquer email seu)
3. Crie uma senha forte
4. Confirme o email (verifique caixa de entrada)
```

### **Passo 3: Acessar IoT Platform**
```
1. Acesse: https://iot.tuya.com/
2. Clique em "Sign In"
3. Use o EMAIL que você acabou de vincular
4. Use a SENHA que você criou
5. NÃO use "Sign in with Google"
```

### **Passo 4: Obter Local Key**
```
1. No menu lateral, vá em "Cloud"
2. Clique em "Development"
3. Selecione projeto "Casa Inteligente"
4. Vá em "Devices"
5. Encontre sua tomada (ID: eb0254d3ac39b4d2740fwq)
6. Clique em "Device Details"
7. Role para baixo até "Local Key"
8. Copie os 32 caracteres
```

### **Passo 5: Configurar no Sistema**
```bash
# Edite o .env
nano .env

# Adicione:
TUYA_LOCAL_KEY=sua_local_key_aqui

# Salve e teste:
python scripts/test_novadigital_final.py
```

---

## 🔄 ALTERNATIVA: RESETAR E RECONFIGURAR

Se não conseguir vincular email:

### **Passo 1: Criar Nova Conta**
```
1. Desinstale app Tuya Smart
2. Reinstale app
3. Crie conta com EMAIL e SENHA
4. NÃO use Google OAuth
```

### **Passo 2: Resetar Tomada**
```
1. Pressione botão da tomada por 10 segundos
2. LED deve piscar rapidamente
3. Solte o botão
4. Tomada está resetada
```

### **Passo 3: Reconfigurar**
```
1. No app, toque em "+"
2. Selecione "Electrical" > "Socket"
3. Siga instruções de configuração
4. Conecte à sua rede WiFi
5. Dispositivo será adicionado
```

### **Passo 4: Obter Local Key**
```
Siga Passo 3 e 4 da solução anterior
```

---

## 📞 SE NADA FUNCIONAR:

### **Contate Suporte Tuya:**
```
Email: support@tuya.com
Assunto: Cannot access IoT Platform - Google OAuth account

Mensagem:
"Hello,

I created my Tuya Smart account using Google OAuth.
I cannot access the IoT Platform (iot.tuya.com) because 
it doesn't accept Google login.

I need the Local Key for my device:
- Device ID: eb0254d3ac39b4d2740fwq
- Device IP: 192.168.68.100

Could you please:
1. Provide the Local Key, or
2. Help me bind an email to my Google account

Thank you!"
```

---

## 🎉 DEPOIS DE OBTER A LOCAL KEY:

```bash
# Configure no .env
TUYA_LOCAL_KEY=sua_local_key_de_32_caracteres

# Teste conexão
python scripts/test_novadigital_final.py

# Inicie monitoramento
python scripts/monitor_novadigital_final.py
```

**Você está muito perto! Escolha uma solução e execute!** 🎯
"""
    
    with open('GUIA_CONTA_GOOGLE_OAUTH.md', 'w') as f:
        f.write(guide)
    
    print("✅ Guia criado: GUIA_CONTA_GOOGLE_OAUTH.md")


def main():
    """Função principal"""
    helper = TuyaGoogleAccountHelper()
    
    print("\n🎯 PROBLEMA IDENTIFICADO:")
    print("=" * 60)
    print("✅ Conta criada com Google OAuth")
    print("❌ IoT Platform não aceita login Google")
    print("❌ Não consegue acessar Local Key")
    print()
    
    helper.show_all_solutions()
    
    print("\n" + "=" * 60)
    print("📋 RECOMENDAÇÃO:")
    print("=" * 60)
    print()
    print("🥇 MELHOR OPÇÃO: Vincular email no app")
    print("   - Mais rápido (5 minutos)")
    print("   - Não perde configurações")
    print("   - Mantém conta Google")
    print()
    print("🥈 SEGUNDA OPÇÃO: Resetar e reconfigurar")
    print("   - Rápido (15 minutos)")
    print("   - Perde automações")
    print("   - Conta nova com email/senha")
    print()
    
    # Criar guia
    create_step_by_step_guide()
    
    print("\n✅ Guia detalhado criado!")
    print("📁 Arquivo: GUIA_CONTA_GOOGLE_OAUTH.md")


if __name__ == "__main__":
    main()
