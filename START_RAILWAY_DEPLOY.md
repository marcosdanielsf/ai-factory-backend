# 🚀 START HERE - Railway Deploy

## ⚡ Quick Start (5 Minutos)

### Método Automático - Use o Script Guiado

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework
./quick-deploy.sh
```

O script irá:
1. Verificar pré-requisitos
2. Instalar Railway CLI (se necessário)
3. Ajudar você a configurar variáveis
4. Fazer deploy automático
5. Gerar domínio público

---

## 📋 Pré-Requisitos

Você precisa ter:

### 1. Conta Railway
- Cadastre-se: https://railway.app (grátis)
- $5 de créditos grátis/mês

### 2. Credenciais Supabase
- URL: `https://seu-projeto.supabase.co`
- Anon Key: `eyJhbGci...`
- Service Role Key: `eyJhbGci...`

Onde encontrar:
- Dashboard → Projeto → Settings → API

### 3. Credenciais Anthropic
- API Key: `sk-ant-api03-...`

Onde encontrar:
- https://console.anthropic.com/settings/keys

---

## 🎯 Escolha seu Caminho

### 🟢 Iniciante / Primeira vez
→ Use: `./quick-deploy.sh`

### 🟡 Conhece Railway CLI
→ Leia: `RAILWAY_DEPLOY_MANUAL_GUIDE.md`

### 🔴 Prefere GitHub deploy
→ Leia: `RAILWAY_DEPLOY.md`

---

## ✅ Arquivos Já Prontos

Você NÃO precisa criar nada. Tudo está pronto:

- ✅ `Dockerfile` - Build otimizado
- ✅ `railway.toml` - Config de produção
- ✅ `gunicorn.conf.py` - Performance config
- ✅ `requirements.txt` - Dependências
- ✅ `.env.railway.example` - Template de vars
- ✅ `.gitignore` - Proteção de secrets
- ✅ `test-railway-api.sh` - Testes automatizados

---

## 🚀 Deploy em 3 Passos (CLI)

### Passo 1: Instalar Railway CLI

```bash
npm install -g @railway/cli
```

### Passo 2: Configurar Variáveis

```bash
# Copiar template
cp .env.railway.example .env.railway

# Editar com suas credenciais
nano .env.railway

# Upload para Railway
railway login
railway init
railway variables set --env production < .env.railway
```

### Passo 3: Deploy

```bash
railway up
railway domain
```

Pronto! Sua API está no ar.

---

## 🧪 Testar Deploy

```bash
# Edite o script com sua URL Railway
nano test-railway-api.sh
# Altere: API_URL="https://SEU-PROJETO.railway.app"

# Execute os testes
./test-railway-api.sh
```

Esperado:
- ✅ `/health` → HTTP 200
- ✅ `/ping` → HTTP 200
- ✅ `/docs` → HTTP 200

---

## 🐛 Algo Deu Errado?

### Deploy falhou?
```bash
railway logs --tail 100
```

### Health check timeout?
```bash
railway logs | grep "Uvicorn running"
```

### Precisa de ajuda detalhada?
→ Leia: `TROUBLESHOOTING.md` (20+ soluções)

---

## 💰 Custos

Com configuração padrão (512MB RAM, 1 CPU):
- **Dev/Test**: $0-5/mês (coberto por free tier)
- **Produção Light**: $8-15/mês
- **Produção Medium**: $20-30/mês

---

## 📚 Documentação Completa

| Documento | Quando usar |
|-----------|-------------|
| `START_RAILWAY_DEPLOY.md` | ⭐ Você está aqui - comece por aqui |
| `quick-deploy.sh` | Deploy automático guiado |
| `RAILWAY_DEPLOY_MANUAL_GUIDE.md` | Guia completo passo-a-passo |
| `DEPLOY_SUMMARY.md` | Resumo executivo do deploy |
| `TROUBLESHOOTING.md` | Quando algo der errado |
| `test-railway-api.sh` | Validar API após deploy |

---

## ⏱️ Timeline Esperado

1. **Setup** (5 min): Instalar CLI + configurar vars
2. **Deploy** (3-5 min): Build + Health checks
3. **Testes** (2 min): Validar endpoints
4. **Total**: ~10-15 minutos

---

## 🎯 Próximo Passo

Execute agora:

```bash
./quick-deploy.sh
```

Ou, se preferir manual:

```bash
# 1. Leia o guia
cat RAILWAY_DEPLOY_MANUAL_GUIDE.md

# 2. Siga o método de sua preferência
```

---

## 📞 Suporte

- **Railway Discord**: https://discord.gg/railway
- **Documentação**: `TROUBLESHOOTING.md`
- **Logs em tempo real**: `railway logs --follow`

---

**Status**: ✅ TUDO PRONTO PARA DEPLOY

Última atualização: 31/12/2024
