# Integração com Dispositivos NovaDigital via Tuya

## Overview

Os dispositivos NovaDigital são baseados na plataforma Tuya. Esta documentação mostra como integrá-los ao seu sistema usando duas abordagens:

1. **API Local Tuya** - Controle direto na rede local
2. **API Cloud Tuya** - Controle via nuvem Tuya

## Método 1: API Local Tuya (Recomendado)

### Instalação

```bash
pip install tinytuya
```

### Configuração

1. **Configure o dispositivo no app Tuya Smart**
2. **Obtenha as credenciais do dispositivo:**
   - Device ID
   - Local Key  
   - IP Address

3. **Adicione ao arquivo .env:**

```env
# Configurações Tuya Local
TUYA_DEVICE_ID=seu_device_id_aqui
TUYA_LOCAL_KEY=sua_local_key_aqui
TUYA_IP_ADDRESS=192.168.x.x
```

### Teste

```bash
# Testar conexão com dispositivo configurado
python scripts/test_tuya.py

# Escanear rede em busca de dispositivos Tuya
python scripts/test_tuya.py scan
```

## Método 2: API Cloud Tuya

### Configuração

1. **Crie conta em https://iot.tuya.com/**
2. **Crie um projeto Cloud**
3. **Obtenha as credenciais:**
   - Access ID
   - Access Secret

4. **Adicione ao arquivo .env:**

```env
# Configurações Tuya Cloud
TUYA_ACCESS_ID=seu_access_id_aqui
TUYA_ACCESS_KEY=seu_access_secret_aqui
TUYA_REGION=br
```

### Teste

```bash
python scripts/test_tuya_cloud.py
```

## Como Obter Credenciais do Dispositivo

### Método 1: Tuya-Convert

```bash
# Clonar e executar Tuya-Convert
git clone https://github.com/ct-Open-Source/tuya-convert
cd tuya-convert
./install_prereq.sh
./start_flash.sh
```

### Método 2: Extração do App

1. Instale o app Tuya Smart
2. Configure seu dispositivo NovaDigital
3. Use ferramentas de depuração para extrair:
   - Device ID
   - Local Key
   - IP Address

## DPS Comuns (Data Points)

| DPS | Descrição | Tipo |
|-----|-----------|------|
| 1   | Status On/Off | Boolean |
| 17  | Consumo de energia hoje | Number |
| 18  | Potência atual (W) | Number |
| 19  | Voltagem (V) | Number |
| 20  | Corrente (A) | Number |
| 23  | Consumo total | Number |

## Exemplos de Uso

### Controle Local

```python
from integrations.tuya_client import TuyaClient

# Criar cliente
client = TuyaClient(
    device_id="seu_device_id",
    local_key="sua_local_key", 
    ip_address="192.168.1.100"
)

# Testar conexão
if await client.test_connection():
    # Ligar dispositivo
    await client.turn_on()
    
    # Obter dados de energia
    energy = await client.get_energy_usage()
    print(f"Potência: {energy['power_watts']}W")
```

### Controle Cloud

```python
from integrations.tuya_cloud_client import TuyaCloudClient

# Criar cliente
async with TuyaCloudClient(
    access_id="seu_access_id",
    access_key="seu_access_key",
    region="br"
) as client:
    
    # Listar dispositivos
    devices = await client.get_device_list()
    
    # Controlar dispositivo
    await client.turn_on(devices[0]['id'])
    
    # Obter dados de energia
    energy = await client.get_energy_usage(devices[0]['id'])
```

## Troubleshooting

### Erro: "tinytuya não instalada"
```bash
pip install tinytuya==1.13.0
```

### Erro: "Dispositivo não encontrado"
- Verifique se o dispositivo está online
- Confirme o IP Address
- Verifique Device ID e Local Key

### Erro: "Conexão falhou"
- Verifique firewall
- Confirme rede local
- Teste conectividade com ping

### Erro: "Token inválido" (Cloud)
- Verifique Access ID e Access Key
- Confirme região correta
- Verifique se projeto está ativo

## Modelos Compatíveis

- **Tomadas Inteligentes**: WK-BR PRO MAX
- **Interruptores**: MS-101, MS-101+RF433
- **Lâmpadas**: Variados modelos
- **Sensores**: Temperatura, umidade, etc.

## Vantagens da Integração Tuya

✅ **Controle Local**: Sem dependência de internet  
✅ **Resposta Rápida**: Comandos diretos na rede  
✅ **Dados em Tempo Real**: Monitoramento instantâneo  
✅ **Multiplataforma**: Funciona com diversos dispositivos  
✅ **Documentação**: Amplamente suportado  

## Comparação com TAPO

| Característica | TAPO | Tuya (NovaDigital) |
|----------------|------|-------------------|
| API Local | ✅ | ✅ |
| API Cloud | ✅ | ✅ |
| Monitoramento | ✅ | ✅ |
| Documentação | Limitada | Ampla |
| Comunidade | Pequena | Grande |
| Dispositivos | TP-Link | Múltiplas marcas |

## Suporte

- **Documentação TinyTuya**: https://pypi.org/project/tinytuya/
- **Tuya Developer**: https://developer.tuya.com/
- **Fórum Home Assistant Brasil**: https://homeassistantbrasil.com.br/
