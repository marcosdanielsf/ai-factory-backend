# 🔧 Railway Deploy - Troubleshooting Guide

## 📋 Índice de Problemas Comuns

1. [Problemas de Build](#1-problemas-de-build)
2. [Problemas de Deploy](#2-problemas-de-deploy)
3. [Problemas de Conexão](#3-problemas-de-conexão)
4. [Problemas de Performance](#4-problemas-de-performance)
5. [Problemas de Autenticação](#5-problemas-de-autenticação)
6. [Problemas de Custos](#6-problemas-de-custos)

---

## 1. Problemas de Build

### ❌ Erro: "Docker build failed"

**Sintomas:**
```
ERROR: failed to solve: process "/bin/sh -c pip wheel..." did not complete successfully
```

**Causas possíveis:**
- Dependência incompatível no `requirements.txt`
- Timeout durante download de pacotes
- Memória insuficiente durante build

**Soluções:**

```bash
# 1. Testar build localmente primeiro
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework
docker build -t ai-factory-test .

# 2. Se falhar localmente, verificar requirements.txt
cat requirements.txt

# 3. Teste instalar pacotes localmente
pip install -r requirements.txt --dry-run

# 4. Se problema for memória, simplificar build
# Edite Dockerfile - remova build em paralelo
# De: pip wheel --no-cache-dir --no-deps
# Para: pip wheel --no-cache-dir --no-deps --no-binary :all:
```

**Logs relevantes:**
```bash
railway logs --deployment-id <ID> | grep ERROR
```

---

### ❌ Erro: "No module named 'src'"

**Sintomas:**
```
ModuleNotFoundError: No module named 'src'
```

**Causas:**
- `PYTHONPATH` não configurado
- Estrutura de pastas incorreta
- Arquivos não copiados no Dockerfile

**Soluções:**

```bash
# 1. Verificar estrutura de pastas
ls -la /Users/marcosdaniels/Downloads/ai-factory-testing-framework/
# Deve ter: src/, server.py, main.py

# 2. Verificar Dockerfile
cat Dockerfile | grep COPY
# Deve ter: COPY --chown=appuser:appuser src/ src/

# 3. Verificar se main.py existe
ls -la main.py

# 4. Adicionar PYTHONPATH no railway.toml se necessário
# [env]
# PYTHONPATH = "/app"
```

---

## 2. Problemas de Deploy

### ❌ Erro: "Health check timeout"

**Sintomas:**
```
Health check failed: Connection timeout
Service is unhealthy
```

**Causas:**
- App não iniciou em 60 segundos
- App não responde em `/health`
- Porta incorreta

**Soluções:**

```bash
# 1. Verificar logs de startup
railway logs | grep "Uvicorn running"

# 2. Verificar se app está escutando na porta correta
railway logs | grep "0.0.0.0:8000"

# 3. Testar endpoint /health localmente
curl http://localhost:8000/health

# 4. Aumentar timeout no railway.toml
# [deploy]
# healthcheckTimeout = 30  # Era 10

# 5. Verificar variáveis de ambiente
railway variables | grep PORT
railway variables | grep SERVER_PORT
```

**Verificar health check manual:**
```bash
# Quando deploy falhar, pegue URL temporária nos logs
railway logs | grep "Deploying to"

# Teste health check direto
curl -v https://temporary-url.railway.app/health
```

---

### ❌ Erro: "Failed to initialize clients"

**Sintomas:**
```
ERROR - Failed to initialize clients: Missing required environment variables
RuntimeError: Supabase client initialization failed
```

**Causas:**
- Variáveis de ambiente ausentes
- Credenciais incorretas
- Variáveis não sincronizadas após deploy

**Soluções:**

```bash
# 1. Listar todas as variáveis configuradas
railway variables

# Deve ter:
# - SUPABASE_URL
# - SUPABASE_KEY
# - SUPABASE_SERVICE_ROLE_KEY
# - ANTHROPIC_API_KEY

# 2. Adicionar variáveis faltantes
railway variables set SUPABASE_URL="https://seu-projeto.supabase.co"
railway variables set SUPABASE_KEY="eyJhbGci..."
railway variables set SUPABASE_SERVICE_ROLE_KEY="eyJhbGci..."
railway variables set ANTHROPIC_API_KEY="sk-ant-api03-..."

# 3. Verificar valores (primeiros caracteres)
railway variables | grep SUPABASE_URL

# 4. Forçar redeploy
railway up --detach

# 5. Verificar logs após redeploy
railway logs --follow
```

---

### ❌ Erro: "Service crashed immediately after start"

**Sintomas:**
```
Service started but crashed after 5 seconds
Exit code: 1
```

**Causas:**
- Erro Python não capturado
- Import error
- Database connection failure

**Soluções:**

```bash
# 1. Ver logs completos
railway logs --tail 100

# 2. Procurar por traceback
railway logs | grep -A 10 "Traceback"

# 3. Testar localmente com mesmas env vars
cp .env.railway .env
docker build -t ai-factory-test .
docker run -p 8000:8000 --env-file .env ai-factory-test

# 4. Verificar server.py não tem erros de sintaxe
python3 -m py_compile server.py

# 5. Testar imports
python3 -c "from src.supabase_client import SupabaseClient"
```

---

## 3. Problemas de Conexão

### ❌ Erro: "Connection to Supabase refused"

**Sintomas:**
```
httpx.ConnectError: Connection refused
Failed to connect to Supabase
```

**Causas:**
- URL incorreta
- Firewall bloqueando Railway IPs
- Supabase project pausado

**Soluções:**

```bash
# 1. Verificar URL Supabase
railway variables | grep SUPABASE_URL
# Deve ser: https://SEU_PROJETO.supabase.co (sem trailing slash)

# 2. Verificar se Supabase está ativo
curl https://seu-projeto.supabase.co/rest/v1/

# 3. Testar conexão do Railway para Supabase
railway run curl https://seu-projeto.supabase.co/rest/v1/

# 4. Verificar Supabase Dashboard
# Settings → API → Is project paused?

# 5. Whitelist Railway IPs no Supabase (se necessário)
# Settings → Database → Connection Pooling → Allow all IPs
```

---

### ❌ Erro: "Too many connections"

**Sintomas:**
```
remaining connection slots are reserved
FATAL: sorry, too many clients already
```

**Causas:**
- Connection pool esgotado
- Workers demais abrindo conexões
- Connections não sendo fechadas

**Soluções:**

```bash
# 1. Reduzir workers
railway variables set GUNICORN_WORKERS="2"

# 2. Aumentar connection pool no Supabase
# Dashboard → Settings → Database → Connection Pooling
# Increase max connections to 50 (free tier) ou 100 (paid)

# 3. Verificar se app está fazendo connection pooling
# Verificar src/supabase_client.py usa singleton pattern

# 4. Monitorar conexões abertas
# Supabase Dashboard → Database → Connections

# 5. Se problema persistir, usar connection pooler
# Settings → Database → Connection string → Use Pooler
```

---

### ❌ Erro: "CORS policy blocked"

**Sintomas:**
```
Access to fetch at 'https://api.railway.app' from origin 'https://frontend.com'
has been blocked by CORS policy
```

**Causas:**
- CORS não configurado corretamente
- Origin não permitido

**Soluções:**

```python
# 1. Editar server.py - CORS config
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-frontend.com"],  # Em vez de ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Para dev/staging, permitir tudo
allow_origins=["*"]

# 3. Para produção, lista específica
allow_origins=[
    "https://seu-frontend.com",
    "https://seu-frontend.vercel.app",
]

# 4. Commit e redeploy
git add server.py
git commit -m "fix: update CORS policy"
git push
```

---

## 4. Problemas de Performance

### ⚠️ Problema: "API muito lenta (>2s response time)"

**Sintomas:**
- Health check > 500ms
- Requests normais > 2s
- Timeout em alguns requests

**Diagnóstico:**

```bash
# 1. Testar response time
time curl https://seu-app.railway.app/health

# 2. Ver métricas Railway
railway open
# Dashboard → Metrics → Response Time

# 3. Verificar logs para queries lentas
railway logs | grep "slow query"
railway logs | grep "timeout"
```

**Soluções:**

```bash
# Solução 1: Aumentar workers
railway variables set GUNICORN_WORKERS="4"

# Solução 2: Aumentar memória
# Edite railway.toml:
# memory = "1024MB"  # Era 512MB
git add railway.toml
git commit -m "perf: increase memory"
git push

# Solução 3: Aumentar CPU
# railway.toml:
# cpu = "2"  # Era 1

# Solução 4: Otimizar queries Supabase
# Adicionar índices nas tabelas mais consultadas

# Solução 5: Adicionar caching
# Implementar Redis ou in-memory cache
```

---

### ⚠️ Problema: "High memory usage (>90%)"

**Sintomas:**
```
Memory usage: 475MB / 512MB (92%)
Service may be killed due to OOM
```

**Diagnóstico:**

```bash
# Ver métricas
railway open
# Metrics → Memory Usage

# Ver logs de memory
railway logs | grep "memory"
railway logs | grep "OOM"
```

**Soluções:**

```bash
# Solução 1: Reduzir workers
railway variables set GUNICORN_WORKERS="2"

# Solução 2: Aumentar memória alocada
# railway.toml:
# memory = "1024MB"

# Solução 3: Adicionar graceful restarts
# railway.toml ou gunicorn.conf.py:
# max_requests = 500
# max_requests_jitter = 50

# Solução 4: Verificar memory leaks
# Adicionar logging de memória no código

# Solução 5: Reduzir timeout
railway variables set GUNICORN_TIMEOUT="60"
```

---

### ⚠️ Problema: "Requests timeout após 30s"

**Sintomas:**
```
504 Gateway Timeout
Request took longer than 30s
```

**Causas:**
- Operações longas (ex: processar 100 tests)
- Railway timeout default (30s)
- Database queries lentas

**Soluções:**

```bash
# Solução 1: Aumentar timeout Gunicorn
railway variables set GUNICORN_TIMEOUT="120"

# Solução 2: Usar background tasks
# Mover operações longas para FastAPI BackgroundTasks

# Exemplo em server.py:
from fastapi import BackgroundTasks

@app.post("/api/v1/test/batch")
async def batch_test(request: BatchRequest, background_tasks: BackgroundTasks):
    # Processar em background
    background_tasks.add_task(process_batch, request)
    return {"status": "processing", "task_id": "..."}

# Solução 3: Implementar fila (Celery/RQ)
# Para operações realmente longas

# Solução 4: Otimizar queries
# Adicionar índices, usar select específico em vez de *
```

---

## 5. Problemas de Autenticação

### ❌ Erro: "401 Unauthorized"

**Sintomas:**
```
{"detail": "Invalid API key"}
401 Unauthorized
```

**Causas:**
- API_KEY não enviada no header
- API_KEY incorreta
- API_KEY não configurada no servidor

**Soluções:**

```bash
# 1. Verificar se API_KEY está configurada
railway variables | grep API_KEY

# 2. Se não estiver, adicionar
railway variables set API_KEY="sua-chave-segura"

# 3. Gerar chave segura
openssl rand -hex 32

# 4. Testar com curl
curl -H "X-API-Key: sua-chave" https://seu-app.railway.app/api/v1/agents

# 5. Se endpoint não requer auth, verificar código
# server.py deve ter:
@app.get("/health")  # SEM dependency de API key
async def health():
    ...

@app.get("/api/v1/agents", dependencies=[Depends(verify_api_key)])
async def list_agents():
    ...
```

---

### ❌ Erro: "Supabase Auth failed"

**Sintomas:**
```
Invalid JWT
Auth session expired
```

**Causas:**
- SUPABASE_KEY expirada ou incorreta
- SERVICE_ROLE_KEY necessário mas não configurado

**Soluções:**

```bash
# 1. Pegar chaves atualizadas do Supabase
# Dashboard → Settings → API

# 2. Tem dois tipos de chave:
# - anon/public (SUPABASE_KEY) - para frontend
# - service_role (SUPABASE_SERVICE_ROLE_KEY) - para backend

# 3. Backend deve usar service_role
railway variables set SUPABASE_SERVICE_ROLE_KEY="eyJhbGci..."

# 4. Verificar código usa a chave correta
# src/supabase_client.py deve usar SERVICE_ROLE_KEY

# 5. Testar conexão
railway run python3 -c "from src.supabase_client import SupabaseClient; SupabaseClient()"
```

---

## 6. Problemas de Custos

### 💰 Problema: "Custos acima do esperado"

**Sintomas:**
- Fatura Railway > $20/mês
- Usage alerts do Railway

**Diagnóstico:**

```bash
# Ver usage atual
railway open
# Dashboard → Usage → Current billing period

# Ver breakdown
# Settings → Billing → Usage breakdown
```

**Soluções:**

```bash
# Solução 1: Reduzir recursos
# railway.toml:
memory = "256MB"  # Era 512MB
cpu = "1"         # Já é o mínimo

# Solução 2: Reduzir workers
railway variables set GUNICORN_WORKERS="2"

# Solução 3: Auto-sleep em staging
# Railway Dashboard → Settings → Sleep after 1 hour of inactivity

# Solução 4: Usar Free Tier para dev/test
# Criar ambiente separado
railway environment create staging
railway environment create production

# Solução 5: Otimizar bandwidth
# Implementar GZIP compression (já está no código)
# Reduzir logs verbosos em produção
railway variables set LOG_LEVEL="WARNING"

# Solução 6: Monitorar custos
# Settings → Billing → Set spending limit
```

---

### 💰 Problema: "Créditos grátis acabaram rapidamente"

**Causas:**
- Muitos deploys
- Resources alocados demais
- Tráfego alto inesperado

**Soluções:**

```bash
# Otimizar deploys
# 1. Não fazer deploy a cada commit - usar staging

# 2. Deploy apenas quando necessário
git commit -m "feat: new feature"
# NÃO faça push automático para main
# Use branch feature → PR → merge

# 3. Configurar CI/CD controlado
# GitHub Actions só para merge em main

# 4. Usar Railway Environments
railway environment create staging  # Free credits
railway environment create production  # Billing

# 5. Reduzir recursos em staging
# Use memory="256MB", workers=1 em staging
```

---

## 📞 Suporte e Recursos

### Railway Support

- **Discord**: https://discord.gg/railway (mais rápido)
- **Email**: team@railway.app
- **Status**: https://status.railway.app

### Debugging Tools

```bash
# Railway CLI commands úteis
railway logs --follow          # Logs em tempo real
railway logs --tail 100        # Últimas 100 linhas
railway logs | grep ERROR      # Filtrar erros
railway status                 # Status do serviço
railway variables              # Listar env vars
railway restart                # Restart service
railway open                   # Abrir dashboard
```

### Logs Úteis para Compartilhar com Suporte

```bash
# Gerar relatório completo
railway logs --tail 500 > railway-debug.log

# Info do ambiente
railway status > railway-status.txt

# Variáveis (sem valores sensíveis)
railway variables | sed 's/=.*/=***/' > railway-vars.txt

# Enviar para suporte
# Anexe: railway-debug.log, railway-status.txt
```

---

## 🔍 Checklist de Debugging

Use este checklist quando algo der errado:

- [ ] Verificar logs: `railway logs --tail 100`
- [ ] Verificar variáveis: `railway variables`
- [ ] Verificar status: `railway status`
- [ ] Testar localmente: `docker build . && docker run -p 8000:8000 ...`
- [ ] Testar health check: `curl https://seu-app.railway.app/health`
- [ ] Verificar Supabase online: Dashboard → Project status
- [ ] Verificar billing: Railway dashboard → não ultrapassou limite?
- [ ] Procurar erros conhecidos: Este documento
- [ ] Procurar no Discord Railway: Alguém teve problema similar?
- [ ] Criar issue detalhado: Logs + passos para reproduzir

---

**Última atualização:** 31/12/2024
**Versão:** 1.0.0
