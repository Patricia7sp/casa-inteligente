# 📋 RESUMO DAS APIs - CASA INTELIGENTE

## 🎯 **O QUE VOCÊ PRECISA SABER**

### **1. Como o Sistema Identifica VOCÊ?**
✅ **CREDENCIAIS EXCLUSIVAS**
- **TP-Link TAPO:** Seu email + senha pessoal da conta TP-Link
- **Nova Digital:** Sua API Key única do portal Nova Digital
- **Isolamento Total:** Seus dados ficam no seu banco PostgreSQL local

### **2. Como a Extração de Dados Funciona?**
🔄 **PROCESSO AUTOMÁTICO**
```
1. Coletor roda a cada 15 minutos
2. Conecta em cada dispositivo cadastrado
3. Extrai: Potência (W), Tensão (V), Corrente (A), Energia (kWh)
4. Salva no banco PostgreSQL
5. Processa anomalias e alertas
6. Envia notificações se necessário
```

---

## 🔌 **TP-LINK TAPO**

### **📦 Biblioteca Usada:** `pytapo==3.3.12`

### **🔧 Como Funciona:**
- **Conexão Local:** Na sua rede WiFi
- **Protocolo:** Direto com a tomada (sem nuvem)
- **Segurança:** Suas credenciais TP-Link

### **📋 Passos para Configurar:**

#### **PASSO 1: App TAPO**
1. Baixe **"Tapo"** na App Store/Google Play
2. Crie conta TP-Link (ou use existente)
3. Conecte suas tomadas na rede WiFi
4. Adicione as tomadas no app

#### **PASSO 2: Encontrar IPs**
```bash
# Opção 1: App Tapo
Configurações → Informações de Rede → Anotar IP

# Opção 2: Roteador
192.168.1.1 → Dispositivos Conectados → Procurar "Tapo"

# Opção 3: Scanner
nmap -sn 192.168.1.0/24
```

#### **PASSO 3: Configurar Sistema**
No `.env`:
```bash
TAPO_USERNAME=seu_email@exemplo.com
TAPO_PASSWORD=sua_senha_tapo
```

#### **PASSO 4: Adicionar Dispositivo**
```bash
curl -X POST http://localhost:8000/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Geladeira",
    "type": "TAPO",
    "ip_address": "192.168.1.100",
    "location": "Cozinha",
    "equipment_connected": "Geladeira Consul"
  }'
```

---

## 🏠 **NOVA DIGITAL**

### **📦 Biblioteca Usada:** `aiohttp` (API REST)

### **🔧 Como Funciona:**
- **Conexão Cloud:** Via internet (API Nova Digital)
- **Protocolo:** HTTP/HTTPS REST
- **Segurança:** Sua API Key exclusiva

### **📋 Passos para Configurar:**

#### **PASSO 1: Portal Nova Digital**
1. Acesse: https://portal.novadigital.com.br
2. Crie conta de desenvolvedor
3. Verifique email

#### **PASSO 2: Gerar API Key**
1. Login no portal
2. Desenvolvedores → API Keys
3. "Gerar Nova API Key"
4. Nome: "Casa Inteligente"
5. **COPIE A KEY** (não aparecerá novamente)

#### **PASSO 3: Registrar Dispositivos**
1. Portal → Meus Dispositivos
2. Adicione suas tomadas Nova Digital
3. Anote o **Device ID** de cada uma

#### **PASSO 4: Configurar Sistema**
No `.env`:
```bash
NOVA_DIGITAL_API_KEY=sua_api_key_aqui
NOVA_DIGITAL_BASE_URL=https://api.novadigital.com.br
```

#### **PASSO 5: Adicionar Dispositivo**
```bash
curl -X POST http://localhost:8000/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ar Condicionado",
    "type": "NOVA_DIGITAL",
    "ip_address": "NOVA_DEVICE_12345",
    "location": "Quarto",
    "equipment_connected": "Ar Condicionado 12000BTU"
  }'
```

---

## 🧪 **TESTAR CONEXÕES**

### **Testar TAPO:**
```bash
curl -X POST http://localhost:8000/devices/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "type": "TAPO",
    "ip_address": "192.168.1.100"
  }'
```

### **Testar Nova Digital:**
```bash
curl -X POST http://localhost:8000/devices/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "type": "NOVA_DIGITAL",
    "api_key": "sua_api_key"
  }'
```

### **Descobrir Dispositivos Locais:**
```bash
curl -X POST http://localhost:8000/devices/discover-local
```

---

## 📊 **EXEMPLO DE DADOS EXTRAÍDOS**

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "device_id": 1,
  "device_name": "Geladeira",
  "power_watts": 125.5,
  "voltage": 220.0,
  "current": 0.57,
  "energy_today_kwh": 2.34,
  "location": "Cozinha"
}
```

---

## 🚨 **PROBLEMAS COMUNS**

### **TAPO não conecta?**
- ✅ Verifique se está na mesma rede WiFi
- ✅ Confirme email e senha TP-Link
- ✅ Teste no app oficial primeiro
- ✅ Verifique firewall do roteador

### **Nova Digital não funciona?**
- ✅ Verifique se API Key está correta
- ✅ Confirme se dispositivos estão registrados no portal
- ✅ Teste conexão com internet
- ✅ Verifique status do portal Nova Digital

### **Dispositivos não aparecem no dashboard?**
- ✅ Reinicie o coletor: `docker-compose restart app`
- ✅ Verifique logs: `docker-compose logs app`
- ✅ Confirme configurações no `.env`
- ✅ Teste conexões individuais

---

## 🔄 **FLUXO COMPLETO**

```
1. Configure suas credenciais no .env
2. Ligue o sistema: docker-compose up -d
3. Teste conexões: /devices/test-connection
4. Adicione dispositivos: POST /devices
5. Inicie coleta automática
6. Monitore no dashboard: http://localhost:8501
```

---

## 📱 **APPS NECESSÁRIOS**

### **Obrigatórios:**
- **Tapo** (App Store/Google Play)
- **Portal Nova Digital** (navegador)

### **Recomendados:**
- **Fing** (scanner de rede)
- **iNet** (ferramentas de rede)

---

## 💡 **DICAS IMPORTANTES**

🔒 **SEGURANÇA:**
- Nunca compartilhe suas credenciais
- Salve API Keys em local seguro
- Use senhas fortes

🔧 **CONFIGURAÇÃO:**
- Teste um dispositivo por vez
- Anote IPs e Device IDs
- Mantenha documentação atualizada

🌐 **REDE:**
- TAPO: Mantenha na mesma rede local
- Nova Digital: Precisa de internet
- Verifique firewall e roteador

---

## 🆘 **SUPORTE**

### **Logs do Sistema:**
```bash
docker-compose logs app -f
```

### **Documentação Completa:**
- `docs/API_SETUP_GUIDE.md` (detalhado)
- `QUICKSTART.md` (rápido)
- `README.md` (geral)

### **Testes Automáticos:**
```bash
pytest tests/ -v
```

---

## ✅ **CHECKLIST DE CONFIGURAÇÃO**

- [ ] Criar conta TP-Link
- [ ] Instalar app Tapo
- [ ] Conectar tomadas TAPO
- [ ] Anotar IPs das tomadas
- [ ] Criar conta Nova Digital
- [ ] Gerar API Key Nova Digital
- [ ] Registrar dispositivos Nova Digital
- [ ] Configurar .env com credenciais
- [ ] Iniciar sistema com Docker
- [ ] Testar conexões individuais
- [ ] Adicionar dispositivos via API
- [ ] Verificar dados no dashboard

---

**🎉 PRONTO! Seu sistema Casa Inteligente está configurado e funcionando!**

Agora você pode monitorar seu consumo de energia em tempo real, receber alertas inteligentes e controlar tudo via dashboard!
