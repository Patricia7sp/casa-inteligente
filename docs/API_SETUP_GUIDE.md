# 📋 Guia de Configuração de APIs - Casa Inteligente

## 🔌 TP-Link TAPO

### **O que é?**
TP-Link TAPO é uma linha de tomadas inteligentes da TP-Link que permitem monitorar consumo de energia e controlar dispositivos remotamente.

### **Biblioteca Utilizada**
Usamos a biblioteca **`pytapo`** (versão 3.3.12) - uma biblioteca Python não oficial para comunicação com dispositivos TAPO.

### **Como Funciona?**
1. **Descoberta:** A biblioteca se conecta ao IP da tomada na rede local
2. **Autenticação:** Usa suas credenciais TP-Link para autenticar
3. **Comunicação:** Envia comandos diretamente para a tomada via protocolo proprietário
4. **Dados:** Extrai informações de consumo em tempo real

### **Configuração Passo a Passo:**

#### **1. Instalar App TAPO**
- Baixe o app **"Tapo"** na App Store ou Google Play
- Crie uma conta TP-Link (ou use existente)

#### **2. Configurar Tomadas**
- Conecte as tomadas TAPO na sua rede WiFi
- Adicione-as no app Tapo
- Anote o **IP de cada tomada** (geralmente no roteador ou app)

#### **3. Obter Credenciais**
- Email: Seu email de cadastro TP-Link
- Senha: Sua senha TP-Link

#### **4. Configurar no Sistema**
No arquivo `.env`:
```bash
# TAPO Configuration
TAPO_USERNAME=seu_email@exemplo.com
TAPO_PASSWORD=sua_senha_tapo
```

#### **5. Adicionar Dispositivos via API**
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

### **Como Encontrar IPs das Tomadas?**

#### **Opção 1: App Tapo**
1. Abra o app Tapo
2. Vá em Configurações do dispositivo
3. Procure por "Informações de Rede" ou "Rede"
4. Anote o endereço IP

#### **Opção 2: Roteador**
1. Acesse o painel do seu roteador (192.168.1.1 ou 192.168.0.1)
2. Procure por "Dispositivos Conectados" ou "DHCP Clients"
3. Procure por dispositivos com nome "Tapo" ou "Kasa"
4. Anote os IPs

#### **Opção 3: Scanner de Rede**
```bash
# Instalar nmap
brew install nmap

# Escanear sua rede
nmap -sn 192.168.1.0/24
```

---

## 🏠 Nova Digital

### **O que é?**
Nova Digital é uma empresa brasileira de automação residencial que oferece tomadas inteligentes com API para desenvolvedores.

### **Como Funciona?**
1. **API REST:** Comunicação via HTTP/HTTPS
2. **Autenticação:** Token de API
3. **Nuvem:** Dados acessados via nuvem Nova Digital
4. **Webhooks:** Opção de notificações em tempo real

### **Configuração Passo a Passo:**

#### **1. Criar Conta Nova Digital**
- Acesse https://portal.novadigital.com.br
- Crie sua conta de desenvolvedor
- Verifique seu email

#### **2. Solicitar Acesso à API**
- Faça login no portal
- Vá para "Desenvolvedores" → "API Keys"
- Clique em "Gerar Nova API Key"
- Dê um nome para sua key: "Casa Inteligente"
- **Copie a API Key** (ela não aparecerá novamente)

#### **3. Registrar Dispositivos**
- No portal Nova Digital
- Vá para "Meus Dispositivos"
- Adicione suas tomadas Nova Digital
- Anote o **Device ID** de cada tomada

#### **4. Configurar no Sistema**
No arquivo `.env`:
```bash
# Nova Digital Configuration
NOVA_DIGITAL_API_KEY=sua_api_key_aqui
NOVA_DIGITAL_BASE_URL=https://api.novadigital.com.br
```

#### **5. Adicionar Dispositivos via API**
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

## 🔧 **Como o Sistema Identifica Você?**

### **1. Credenciais Únicas**
Cada sistema tem suas próprias credenciais:
- **TAPO:** Email + Senha da sua conta TP-Link
- **Nova Digital:** API Key exclusiva do seu cadastro

### **2. Dispositivos Locais**
- **TAPO:** Funciona na sua rede local (IP local)
- **Nova Digital:** Funciona via nuvem (Device ID)

### **3. Isolamento de Dados**
- Seus dados ficam no seu banco PostgreSQL local
- Ninguém mais acessa suas informações
- Cada instalação é independente

---

## 🧪 **Testar Configuração**

### **Testar TAPO**
```bash
# Verificar se consegue se conectar
curl -X POST http://localhost:8000/devices/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "type": "TAPO",
    "ip_address": "192.168.1.100"
  }'
```

### **Testar Nova Digital**
```bash
# Verificar API Key
curl -X POST http://localhost:8000/devices/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "type": "NOVA_DIGITAL",
    "api_key": "sua_api_key"
  }'
```

---

## 📊 **Como a Extração de Dados Funciona?**

### **Processo Automático**
1. **Coletor** roda a cada 15 minutos (configurável)
2. **Conecta** em cada dispositivo cadastrado
3. **Extrai** dados de consumo:
   - Potência atual (Watts)
   - Tensão (Volts)
   - Corrente (Amperes)
   - Energia acumulada (kWh)
4. **Salva** no banco PostgreSQL
5. **Processa** anomalias e alertas
6. **Envia** notificações se necessário

### **Exemplo de Dados Extraídos**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "device_id": 1,
  "power_watts": 125.5,
  "voltage": 220.0,
  "current": 0.57,
  "energy_today_kwh": 2.34
}
```

---

## 🚨 **Solução de Problemas**

### **TAPO não conecta?**
- Verifique se está na mesma rede
- Confirme email e senha TP-Link
- Teste no app oficial primeiro
- Verifique firewall

### **Nova Digital não funciona?**
- Verifique se API Key está correta
- Confirme se dispositivos estão registrados
- Teste conexão com internet
- Verifique status do portal Nova Digital

### **Dispositivos não aparecem?**
- Reinicie o coletor: `docker-compose restart app`
- Verifique logs: `docker-compose logs app`
- Confirme configurações no `.env`

---

## 📱 **Apps Necessários**

### **Obrigatórios:**
- **Tapo** (para TAPO)
- **Portal Nova Digital** (para Nova Digital)

### **Recomendados:**
- **Fing** (scanner de rede)
- **iNet** (ferramentas de rede)

---

## 🔄 **Próximos Passos**

1. **Configure suas credenciais** no `.env`
2. **Adicione seus dispositivos** via API
3. **Teste as conexões** individualmente
4. **Inicie o coletor** automático
5. **Monitore os dados** no dashboard

---

## 💡 **Dicas Importantes**

- **Segurança:** Nunca compartilhe suas credenciais
- **Backup:** Salve suas API Keys em local seguro
- **Testes:** Teste um dispositivo por vez
- **Documentação:** Anote IPs e Device IDs
- **Rede:** Mantenha dispositivos na mesma rede (TAPO)

---

**🆘 Precisa de ajuda?**
- Verifique os logs: `docker-compose logs app`
- Teste conexões individuais
- Consulte a documentação oficial
- Abra issue no GitHub
