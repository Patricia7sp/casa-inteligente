# 🌐 Opções para Deploy do Coletor

## ❌ Por que não funciona no Cloud Run direto?

Seus dispositivos TAPO estão em **192.168.68.x** (rede local).  
Cloud Run está na **internet pública** → **SEM ACESSO** à sua rede doméstica.

---

## ✅ Soluções Possíveis

### 1. **Coletor Local** (Atual - Mais Simples)
**Como funciona:**
- Script Python rodando na sua máquina
- Acessa dispositivos TAPO localmente
- Envia dados para Supabase via HTTPS

**Prós:**
- ✅ Simples de configurar
- ✅ Sem custos adicionais
- ✅ Acesso direto aos dispositivos

**Contras:**
- ❌ Precisa manter computador ligado
- ❌ Depende da sua internet

**Como manter rodando 24/7:**
```bash
# macOS (launchd)
cp scripts/launchd.plist ~/Library/LaunchAgents/com.casainteligente.collector.plist
launchctl load ~/Library/LaunchAgents/com.casainteligente.collector.plist

# Linux (systemd)
sudo cp scripts/systemd.service /etc/systemd/system/casa-inteligente-collector.service
sudo systemctl enable casa-inteligente-collector
sudo systemctl start casa-inteligente-collector
```

---

### 2. **Raspberry Pi / Servidor Local**
**Como funciona:**
- Raspberry Pi na sua rede
- Roda o coletor 24/7
- Baixo consumo de energia

**Prós:**
- ✅ Sempre ligado
- ✅ Baixo custo (~R$300 inicial)
- ✅ Baixo consumo (~5W)

**Contras:**
- ❌ Investimento inicial
- ❌ Manutenção física

---

### 3. **Tailscale VPN** (Recomendado para Cloud)
**Como funciona:**
- Cria rede privada virtual
- Cloud Run conecta via Tailscale
- Acessa dispositivos como se estivesse local

**Prós:**
- ✅ Coletor roda no Cloud Run
- ✅ Sem necessidade de máquina local
- ✅ Seguro (criptografado)

**Contras:**
- ❌ Configuração mais complexa
- ❌ Precisa de gateway na rede local (Raspberry Pi ou roteador)

**Implementação:**
```yaml
# .github/workflows/ci-cd.yml
- name: Deploy com Tailscale
  env:
    TAILSCALE_AUTH_KEY: ${{ secrets.TAILSCALE_AUTH_KEY }}
  run: |
    gcloud run deploy $SERVICE_NAME \
      --set-env-vars TAILSCALE_AUTH_KEY=$TAILSCALE_AUTH_KEY \
      --set-env-vars ENABLE_COLLECTOR=true
```

---

### 4. **Cloudflare Tunnel / ngrok**
**Como funciona:**
- Túnel reverso da sua rede para internet
- Cloud Run acessa via túnel público

**Prós:**
- ✅ Sem VPN complexa
- ✅ Fácil de configurar

**Contras:**
- ❌ Expõe sua rede (risco de segurança)
- ❌ Custo mensal (ngrok Pro ~$8/mês)

---

### 5. **API Gateway Local + Cloud Run**
**Como funciona:**
- Servidor local expõe API REST
- Cloud Run chama API local para coletar dados
- Servidor local acessa TAPO e retorna dados

**Prós:**
- ✅ Separação de responsabilidades
- ✅ Cloud Run não precisa acessar TAPO diretamente

**Contras:**
- ❌ Precisa servidor local sempre ligado
- ❌ Mais complexo

---

## 🎯 Recomendação

### Para Desenvolvimento/Teste:
**Coletor Local** (atual) - Mais simples e rápido

### Para Produção:
1. **Raspberry Pi** - Melhor custo-benefício
2. **Tailscale VPN** - Se quiser tudo na nuvem
3. **Coletor Local + systemd** - Se tiver servidor sempre ligado

---

## 📊 Comparação de Custos

| Solução | Custo Inicial | Custo Mensal | Complexidade |
|---------|---------------|--------------|--------------|
| Local (atual) | R$ 0 | R$ 0 | ⭐ Baixa |
| Raspberry Pi | R$ 300 | ~R$ 2 (energia) | ⭐⭐ Média |
| Tailscale VPN | R$ 0 | R$ 0 (free tier) | ⭐⭐⭐ Alta |
| ngrok | R$ 0 | R$ 40 | ⭐⭐ Média |

---

## 🚀 Próximos Passos (Se quiser migrar)

1. **Escolher solução** (recomendo Raspberry Pi)
2. **Configurar gateway/túnel**
3. **Atualizar Cloud Run** para `ENABLE_COLLECTOR=true`
4. **Testar conectividade**
5. **Migrar coletor**
