# 🚀 Railway Deploy - Guia Manual Completo

## 📋 Status dos Arquivos de Deploy

✅ **TODOS OS ARQUIVOS DE DEPLOY ESTÃO PRONTOS:**

- ✅ `Dockerfile` - Multi-stage build otimizado
- ✅ `railway.toml` - Configuração de produção
- ✅ `gunicorn.conf.py` - Performance config
- ✅ `requirements.txt` - Dependências Python
- ✅ `server.py` - FastAPI application
- ⚠️ **Railway CLI não instalado** - Será instalado no passo 1

---

## 🔧 PRÉ-REQUISITOS

Antes de começar, prepare:

1. **Conta Railway**: https://railway.app (grátis para começar)
2. **GitHub**: Repositório com o código (recomendado) OU local deploy via CLI
3. **Credenciais necessárias**:
   - Supabase URL e Keys
   - Anthropic API Key
   - Opcional: API Key customizada para autenticação

---

## 📦 MÉTODO 1: Deploy via GitHub (RECOMENDADO)

### Passo 1: Preparar Repositório GitHub

```bash
# Se ainda não tem repositório, crie:
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework

# Inicializar git se necessário
git init

# Adicionar arquivos
git add .

# Commit
git commit -m "feat: AI Factory Testing Framework - Railway deploy ready"

# Criar repositório no GitHub e push
gh repo create ai-factory-testing --public --source=. --push
# OU manualmente via github.com
```

### Passo 2: Conectar ao Railway

1. Acesse: https://railway.app/dashboard
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Autorize Railway a acessar seu GitHub
5. Selecione o repositório `ai-factory-testing`
6. Selecione branch `main` (ou `master`)

### Passo 3: Configurar Variáveis de Ambiente

No Railway Dashboard → Seu Projeto → Variables:

**Obrigatórias:**
```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
ANTHROPIC_API_KEY=sk-ant-api03-...
```

**Opcionais (já têm defaults):**
```env
API_KEY=your-custom-api-key-for-authentication
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
```

### Passo 4: Deploy Automático

Railway detecta o `Dockerfile` automaticamente e faz build + deploy:

- ✅ Build via multi-stage Dockerfile
- ✅ Health checks automáticos em `/health`
- ✅ URL pública gerada automaticamente
- ✅ SSL/HTTPS automático

**Aguarde 3-5 minutos** para o primeiro deploy.

### Passo 5: Obter URL e Testar

1. No Railway Dashboard → Seu Projeto → Settings → Domains
2. Clique em **"Generate Domain"**
3. Copie a URL gerada (ex: `ai-factory-xxx.railway.app`)

Teste os endpoints:

```bash
# Health check
curl https://ai-factory-xxx.railway.app/health

# API Docs
open https://ai-factory-xxx.railway.app/docs
```

---

## 🖥️ MÉTODO 2: Deploy via Railway CLI

### Passo 1: Instalar Railway CLI

```bash
npm install -g @railway/cli
```

Verificar instalação:
```bash
railway --version
```

### Passo 2: Login no Railway

```bash
railway login
```

Isso abrirá o navegador para autenticação. Autorize e volte ao terminal.

### Passo 3: Criar Projeto Railway

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework

# Inicializar projeto
railway init

# Quando perguntado:
# - Project name: ai-factory-testing
# - Environment: production
```

### Passo 4: Adicionar Variáveis de Ambiente

```bash
# Método 1: Via comando interativo
railway variables

# Método 2: Via comandos individuais
railway variables set SUPABASE_URL="https://seu-projeto.supabase.co"
railway variables set SUPABASE_KEY="eyJhbGci..."
railway variables set SUPABASE_SERVICE_ROLE_KEY="eyJhbGci..."
railway variables set ANTHROPIC_API_KEY="sk-ant-api03-..."
railway variables set API_KEY="your-custom-api-key"
```

**Alternativamente**, crie arquivo `.env.railway`:

```bash
cat > .env.railway << 'EOF'
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
ANTHROPIC_API_KEY=sk-ant-api03-...
API_KEY=your-custom-api-key
EOF

# Upload todas as variáveis de uma vez
railway variables set --env production < .env.railway
```

### Passo 5: Deploy

```bash
railway up

# Ou especificar detached mode
railway up --detach
```

### Passo 6: Obter URL do Serviço

```bash
# Gerar domínio público
railway domain

# Ver logs
railway logs

# Abrir dashboard
railway open
```

---

## 🔍 VALIDAÇÃO E TESTES

### Scripts de Teste Prontos

Salve como `test-railway-api.sh`:

```bash
#!/bin/bash

# Configuração
API_URL="https://SEU-PROJETO.railway.app"
API_KEY="your-custom-api-key"  # Se configurou API_KEY

echo "🧪 Testando AI Factory API no Railway..."
echo "URL: $API_URL"
echo ""

# 1. Health Check
echo "1️⃣  Testing /health..."
curl -s "$API_URL/health" | jq .
echo ""

# 2. Ping
echo "2️⃣  Testing /ping..."
curl -s "$API_URL/ping"
echo ""

# 3. API Docs
echo "3️⃣  Testing /docs (OpenAPI)..."
curl -s -o /dev/null -w "Status: %{http_code}\n" "$API_URL/docs"
echo ""

# 4. List Agents (protegido por API key)
echo "4️⃣  Testing /api/v1/agents..."
curl -s -H "X-API-Key: $API_KEY" "$API_URL/api/v1/agents" | jq .
echo ""

echo "✅ Testes concluídos!"
```

Execute:
```bash
chmod +x test-railway-api.sh
./test-railway-api.sh
```

### Teste Manual via Postman/Insomnia

**Exemplo de requisição protegida:**

```bash
curl -X POST "https://SEU-PROJETO.railway.app/api/v1/test/run" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-custom-api-key" \
  -d '{
    "agent_version_id": "uuid-do-agente"
  }'
```

---

## 📊 MONITORAMENTO E LOGS

### Ver Logs em Tempo Real

```bash
# Via CLI
railway logs --follow

# Filtrar por erro
railway logs --filter "ERROR"
```

### Acessar Dashboard Railway

```bash
railway open
```

No dashboard você verá:
- **Deployments**: Histórico de deploys
- **Metrics**: CPU, RAM, Network
- **Logs**: Stream de logs em tempo real
- **Variables**: Gerenciar env vars
- **Settings**: Domínios, scaling, etc

### Métricas Importantes

Monitore:
- ✅ **Response Time** em `/health` (esperado: <50ms)
- ✅ **Memory Usage** (esperado: <300MB com 4 workers)
- ✅ **CPU Usage** (esperado: <50% em idle)
- ⚠️ **Error Rate** (deve ser <1%)
- ⚠️ **5xx Responses** (deve ser próximo a zero)

---

## 🐛 TROUBLESHOOTING

### Problema 1: "Failed to initialize clients"

**Sintoma:** API inicia mas retorna 500 em todos os endpoints

**Causa:** Variáveis de ambiente ausentes ou incorretas

**Solução:**
```bash
# Verificar variáveis configuradas
railway variables

# Adicionar missing variables
railway variables set SUPABASE_URL="..."
railway variables set SUPABASE_KEY="..."
railway variables set ANTHROPIC_API_KEY="..."

# Redeploy
railway up
```

### Problema 2: "Health check timeout"

**Sintoma:** Deploy falha no health check

**Causa:** App não está respondendo em `0.0.0.0:8000`

**Solução:**
```bash
# Verificar logs
railway logs

# Verificar se PORT está correto (Railway injeta automaticamente)
railway variables set SERVER_PORT="8000"

# Verificar se Dockerfile está correto
cat Dockerfile | grep EXPOSE  # Deve ser 8000
```

### Problema 3: "Too Many Connections" (Supabase)

**Sintoma:** Erro de conexão com Supabase após muitas requisições

**Causa:** Connection pool esgotado

**Solução:**
```bash
# Reduzir workers
railway variables set GUNICORN_WORKERS="2"

# Ou aumentar connection pool no Supabase
# (Settings → Database → Connection Pooling)
```

### Problema 4: "Memory limit exceeded"

**Sintoma:** App crashando após algumas horas

**Causa:** Memory leak ou workers demais

**Solução:**
```bash
# Aumentar memória no railway.toml
# Edite railway.toml:
memory = "1024MB"  # Era 512MB

# Ou reduzir workers
railway variables set GUNICORN_WORKERS="2"

# Commit e redeploy
git add railway.toml
git commit -m "chore: increase memory limit"
git push
```

### Problema 5: "Build failed"

**Sintoma:** Erro durante `pip install`

**Causa:** Dependência incompatível ou faltando

**Solução:**
```bash
# Testar build localmente primeiro
docker build -t ai-factory-test .

# Se funcionar local, verificar logs Railway
railway logs --deployment-id <ID>

# Verificar requirements.txt
cat requirements.txt
```

---

## 💰 ESTIMATIVA DE CUSTOS

### Railway Pricing

**Free Tier:**
- ✅ $5 de créditos mensais grátis
- ✅ Suficiente para testes/staging
- ⚠️ Pode dormir após inatividade

**Developer Plan ($5/mês):**
- ✅ $5 de créditos inclusos
- ✅ Mais uso adicional sob demanda
- ✅ Sem sleep

**Uso Estimado com Configuração Atual:**

```
512MB RAM + 1 CPU + 4 workers:
- Idle: ~$3-5/mês
- Uso moderado (100 req/dia): ~$8-12/mês
- Uso intenso (1000 req/dia): ~$15-25/mês
```

### Otimização de Custos

```bash
# Reduzir workers (staging/dev)
railway variables set GUNICORN_WORKERS="2"

# Reduzir memória (se possível)
# railway.toml: memory = "256MB"

# Configurar autoscaling (Enterprise)
# Railway dashboard → Settings → Autoscaling
```

---

## 🔄 CI/CD AUTOMÁTICO

### Setup GitHub Actions (Opcional)

Crie `.github/workflows/railway-deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Railway CLI
        run: npm i -g @railway/cli

      - name: Deploy to Railway
        run: railway up --detach
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

**Setup:**
```bash
# Gerar token Railway
railway login
railway whoami

# Adicionar como GitHub Secret
# Settings → Secrets → New repository secret
# Nome: RAILWAY_TOKEN
# Valor: <seu-token>
```

---

## 📈 SCALING E PERFORMANCE

### Horizontal Scaling

Railway suporta múltiplas instâncias (Enterprise):

```bash
# Via dashboard: Settings → Replicas
# Ou via CLI:
railway scale --replicas 3
```

### Vertical Scaling

Aumentar recursos por instância:

```toml
# railway.toml
[deploy]
memory = "1024MB"  # Era 512MB
cpu = "2"          # Era 1
```

### Load Balancing

Railway faz load balancing automático entre réplicas.

### Caching

Adicione Redis para caching (se necessário):

```bash
# No Railway Dashboard
# Add Service → Redis
# Conecta automaticamente via DATABASE_URL
```

---

## 🔐 SEGURANÇA

### Checklist de Segurança

- ✅ **API Key** configurada via env var (não hardcoded)
- ✅ **HTTPS** automático via Railway
- ✅ **CORS** configurado (atualmente permite `*`, ajuste para produção)
- ✅ **Non-root user** no Dockerfile
- ✅ **Health checks** configurados
- ⚠️ **Rate limiting** - adicionar se necessário

### Configurar Rate Limiting (Opcional)

Adicione ao `server.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/test/run")
@limiter.limit("10/minute")
async def test_agent(...):
    ...
```

Adicione ao `requirements.txt`:
```
slowapi==0.1.9
```

---

## 📚 REFERÊNCIAS

- **Railway Docs**: https://docs.railway.app
- **Railway CLI**: https://docs.railway.app/develop/cli
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Gunicorn + Uvicorn**: https://www.uvicorn.org/#running-with-gunicorn
- **Docker Multi-Stage**: https://docs.docker.com/build/building/multi-stage/

---

## ✅ CHECKLIST FINAL

Antes de considerar deploy concluído:

- [ ] Railway project criado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy bem-sucedido (sem erros nos logs)
- [ ] `/health` retornando 200 OK
- [ ] `/docs` acessível (Swagger UI)
- [ ] Teste de POST em endpoint protegido funcionando
- [ ] Logs não mostram errors críticos
- [ ] Domínio público configurado
- [ ] SSL/HTTPS funcionando
- [ ] Monitoring configurado (Railway dashboard)
- [ ] Custos estimados e aprovados
- [ ] Backup de env vars (`.env.railway` local seguro)

---

## 🆘 SUPORTE

Se encontrar problemas:

1. **Railway Discord**: https://discord.gg/railway
2. **Railway Docs**: https://docs.railway.app
3. **GitHub Issues**: (criar no seu repositório)
4. **Logs Railway**: `railway logs` para debug

---

## 🎯 PRÓXIMOS PASSOS

Após deploy bem-sucedido:

1. **Testes de carga**: k6, Locust, ou Artillery
2. **Monitoring avançado**: Sentry, DataDog, ou New Relic
3. **Alerting**: Configure alertas via Railway ou PagerDuty
4. **Backup**: Automated backups do Supabase
5. **CI/CD**: GitHub Actions para deploys automáticos

---

**Criado em:** 31 de Dezembro de 2024
**Última atualização:** 31/12/2024
**Versão:** 1.0.0
**Status:** ✅ PRONTO PARA DEPLOY
