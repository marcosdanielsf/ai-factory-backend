# ✅ CHECKLIST COMPLETO - DEPLOY 100% FUNCIONAL

**Data:** 31 de Dezembro de 2025
**Objetivo:** Subir AI Factory V4 100% funcional em produção
**Status Atual:** 75% completo

---

## 📊 RESUMO EXECUTIVO

### ✅ O QUE JÁ ESTÁ PRONTO (75%)

| Componente | Status | Ambiente |
|------------|--------|----------|
| Backend FastAPI | ✅ Funcional | Local (localhost:8000) |
| Dashboard Next.js | ✅ Funcional | Local (localhost:3000) |
| Supabase Database | ✅ Funcional | Cloud (online) |
| Dados Reais | ✅ Configurado | Dashboard usando Supabase |
| API Endpoints | ✅ 8 endpoints | /api/test-agent, /health, etc. |
| Documentação | ✅ Completa | 12+ arquivos markdown |

### ❌ O QUE FALTA (25%)

| Tarefa | Criticidade | Tempo Estimado |
|--------|-------------|----------------|
| Deploy Railway Backend | 🔴 CRÍTICO | 15 min |
| Deploy Vercel Dashboard | 🔴 CRÍTICO | 10 min |
| Configurar CORS produção | 🟡 IMPORTANTE | 5 min |
| Testar integração completa | 🟡 IMPORTANTE | 10 min |
| Criar arquivos de deploy | 🟢 OPCIONAL | 5 min |

---

## 🎯 TAREFAS PENDENTES (ORDEM DE PRIORIDADE)

---

### 🔴 PRIORIDADE CRÍTICA (BLOQUEADOR)

Sem essas tarefas, o projeto NÃO funciona em produção.

---

#### ✅ TAREFA 1: Deploy do Backend no Railway

**Status:** ⚠️ PENDENTE
**Tempo:** 15 minutos
**Bloqueador:** Sim - Dashboard não funciona sem backend em produção

**O que fazer:**

1. **Instalar Railway CLI** (se não tiver):
   ```bash
   npm install -g railway
   ```

2. **Fazer login**:
   ```bash
   railway login
   ```

3. **Deploy via CLI**:
   ```bash
   cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework

   # Criar projeto Railway
   railway init

   # Configurar variáveis de ambiente
   railway variables set SUPABASE_URL=https://bfumywvwubvernvhjehk.supabase.co
   railway variables set SUPABASE_SERVICE_ROLE_KEY=<SUA_SERVICE_ROLE_KEY_AQUI>
   railway variables set ANTHROPIC_API_KEY=<SUA_ANTHROPIC_API_KEY_AQUI>
   railway variables set API_KEY=sk-test-key-ai-factory-2025

   # Deploy
   railway up
   ```

4. **Anotar URL gerada**:
   ```
   https://SEU-PROJETO.railway.app
   ```

**Como validar:**
```bash
# Testar health endpoint
curl https://SEU-PROJETO.railway.app/health

# Esperado:
# {"status":"healthy","timestamp":"..."}
```

**Documentação:** `RAILWAY_DEPLOY_MANUAL_GUIDE.md`

---

#### ✅ TAREFA 2: Deploy do Dashboard no Vercel

**Status:** ⚠️ PENDENTE
**Tempo:** 10 minutos
**Bloqueador:** Sim - Usuários não acessam o sistema sem frontend em produção

**O que fazer:**

1. **Configurar variáveis de ambiente**:
   ```bash
   cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard

   # Criar .env.production
   cat > .env.production << EOF
   NEXT_PUBLIC_SUPABASE_URL=https://bfumywvwubvernvhjehk.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmdW15d3Z3dWJ2ZXJudmhqZWhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0MDM3OTksImV4cCI6MjA2Njk3OTc5OX0.60VyeZ8XaD6kz7Eh5Ov_nEeDtu5woMwMJYgUM-Sruao
   NEXT_PUBLIC_API_URL=https://SEU-PROJETO.railway.app
   API_KEY=sk-test-key-ai-factory-2025
   EOF
   ```

2. **Deploy no Vercel**:
   ```bash
   # Instalar Vercel CLI (se não tiver)
   npm install -g vercel

   # Login
   vercel login

   # Deploy
   vercel --prod
   ```

3. **Configurar variáveis no Vercel Dashboard**:
   - Acesse: https://vercel.com/dashboard
   - Selecione o projeto
   - Settings → Environment Variables
   - Adicione:
     - `NEXT_PUBLIC_API_URL` = URL do Railway
     - `API_KEY` = `sk-test-key-ai-factory-2025`

**Como validar:**
```bash
# Acessar no navegador
https://SEU-PROJETO.vercel.app

# Deve exibir dashboard com dados reais do Supabase
```

**Documentação:** `QUICK-START-VERCEL.md`

---

### 🟡 PRIORIDADE IMPORTANTE (NÃO BLOQUEADOR)

Essas tarefas melhoram a experiência mas o sistema funciona sem elas.

---

#### ✅ TAREFA 3: Configurar CORS para Produção

**Status:** ⚠️ PENDENTE
**Tempo:** 5 minutos
**Impacto:** Frontend não consegue chamar backend sem CORS correto

**O que fazer:**

1. **Atualizar CORS no Railway**:
   ```bash
   railway variables set CORS_ORIGINS=https://SEU-PROJETO.vercel.app
   ```

2. **Verificar código do backend** (`server.py`):
   ```python
   # Deve ter:
   app.add_middleware(
       CORSMiddleware,
       allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Fazer redeploy**:
   ```bash
   railway up
   ```

**Como validar:**
```bash
# No navegador (Console DevTools):
fetch('https://SEU-PROJETO.railway.app/health')
  .then(r => r.json())
  .then(console.log)

# Não deve dar erro de CORS
```

---

#### ✅ TAREFA 4: Testar Integração Completa

**Status:** ⚠️ PENDENTE
**Tempo:** 10 minutos
**Impacto:** Garantir que tudo funciona end-to-end

**Fluxo de teste:**

1. **Acessar Dashboard em produção**:
   ```
   https://SEU-PROJETO.vercel.app
   ```

2. **Verificar dados reais**:
   - Dashboard deve exibir agentes reais:
     - Dr. Alberto Correia
     - Isabela - Instituto Amar

3. **Testar botão "Run Test"**:
   - Ir em: `/agents`
   - Clicar em "Run Test" em algum agente
   - Deve aparecer alert: "Test started successfully!"

4. **Verificar logs do Railway**:
   ```bash
   railway logs
   ```
   - Deve mostrar requisição POST para `/api/test-agent`

5. **Verificar dados no Supabase**:
   - Acessar: https://supabase.com/dashboard
   - Table Editor → `test_results`
   - Deve ter novo registro do teste

**Checklist de validação:**
```
[ ] Dashboard carrega sem erros
[ ] Dados reais aparecem (não mockados)
[ ] Botão "Run Test" funciona
[ ] Logs do Railway mostram requisição
[ ] Novo teste aparece no Supabase
```

---

### 🟢 PRIORIDADE OPCIONAL (MELHORIAS)

Essas tarefas são nice-to-have mas não afetam funcionalidade principal.

---

#### ✅ TAREFA 5: Criar Arquivos de Deploy

**Status:** ⚠️ PENDENTE
**Tempo:** 5 minutos
**Impacto:** Facilita deploys futuros

**Arquivos a criar:**

1. **`vercel.json`** (Dashboard):
   ```json
   {
     "buildCommand": "npm run build",
     "framework": "nextjs",
     "env": {
       "NEXT_PUBLIC_API_URL": "@next-public-api-url",
       "NEXT_PUBLIC_SUPABASE_URL": "@next-public-supabase-url",
       "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@next-public-supabase-anon-key"
     }
   }
   ```

2. **`Procfile`** (Railway - root):
   ```
   web: uvicorn server:app --host 0.0.0.0 --port $PORT
   ```

3. **`railway.json`** (Railway - root):
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

---

#### ✅ TAREFA 6: Configurar Monitoramento

**Status:** ⚠️ PENDENTE
**Tempo:** 10 minutos
**Impacto:** Visibilidade de erros em produção

**Opções:**

1. **Sentry** (Recomendado):
   ```bash
   npm install @sentry/nextjs
   npx @sentry/wizard@latest -i nextjs
   ```

2. **Railway Logs**:
   - Já está ativo por padrão
   - Acesse: `railway logs --tail`

3. **Vercel Analytics**:
   - Já está ativo por padrão
   - Acesse: Vercel Dashboard → Analytics

---

#### ✅ TAREFA 7: Documentar URLs de Produção

**Status:** ⚠️ PENDENTE
**Tempo:** 2 minutos
**Impacto:** Facilita acesso e compartilhamento

**Criar arquivo `PRODUCTION-URLS.md`**:

```markdown
# 🌐 URLs DE PRODUÇÃO - AI Factory V4

## Frontend (Dashboard)
- **URL:** https://SEU-PROJETO.vercel.app
- **Health:** https://SEU-PROJETO.vercel.app
- **Agents:** https://SEU-PROJETO.vercel.app/agents

## Backend (API)
- **URL:** https://SEU-PROJETO.railway.app
- **Health:** https://SEU-PROJETO.railway.app/health
- **API Docs:** https://SEU-PROJETO.railway.app/docs

## Database
- **Supabase:** https://supabase.com/dashboard/project/bfumywvwubvernvhjehk
- **Table Editor:** https://supabase.com/dashboard/project/bfumywvwubvernvhjehk/editor
```

---

## 📋 ORDEM DE EXECUÇÃO RECOMENDADA

Execute nesta ordem para deploy mais eficiente:

```
1. ✅ Deploy Backend Railway        (15 min) - CRÍTICO
   ↓
2. ✅ Anotar URL do Railway         (1 min)
   ↓
3. ✅ Deploy Dashboard Vercel       (10 min) - CRÍTICO
   ↓
4. ✅ Configurar CORS produção      (5 min)  - IMPORTANTE
   ↓
5. ✅ Testar integração completa    (10 min) - IMPORTANTE
   ↓
6. ✅ Criar arquivos de deploy      (5 min)  - OPCIONAL
   ↓
7. ✅ Configurar monitoramento      (10 min) - OPCIONAL
   ↓
8. ✅ Documentar URLs produção      (2 min)  - OPCIONAL

TEMPO TOTAL (CRÍTICO): ~30 minutos
TEMPO TOTAL (COMPLETO): ~60 minutos
```

---

## 🚀 SCRIPT DE DEPLOY RÁPIDO (30 MIN)

Execute este script para fazer deploy completo:

```bash
#!/bin/bash

echo "🚀 AI FACTORY V4 - DEPLOY COMPLETO"
echo ""

# 1. Deploy Railway Backend (15 min)
echo "1️⃣ Deploying Backend to Railway..."
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework
railway login
railway init
railway variables set SUPABASE_URL=https://bfumywvwubvernvhjehk.supabase.co
railway variables set SUPABASE_SERVICE_ROLE_KEY=<SUA_SERVICE_ROLE_KEY_AQUI>
railway variables set ANTHROPIC_API_KEY=<SUA_ANTHROPIC_API_KEY_AQUI>
railway variables set API_KEY=sk-test-key-ai-factory-2025
railway up

echo ""
echo "⚠️ ATENÇÃO: Anote a URL do Railway exibida acima!"
read -p "Cole a URL do Railway aqui: " RAILWAY_URL
echo ""

# 2. Deploy Vercel Dashboard (10 min)
echo "2️⃣ Deploying Dashboard to Vercel..."
cd dashboard

# Criar .env.production
cat > .env.production << EOF
NEXT_PUBLIC_SUPABASE_URL=https://bfumywvwubvernvhjehk.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmdW15d3Z3dWJ2ZXJudmhqZWhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0MDM3OTksImV4cCI6MjA2Njk3OTc5OX0.60VyeZ8XaD6kz7Eh5Ov_nEeDtu5woMwMJYgUM-Sruao
NEXT_PUBLIC_API_URL=$RAILWAY_URL
API_KEY=sk-test-key-ai-factory-2025
EOF

vercel login
vercel --prod

echo ""
echo "⚠️ ATENÇÃO: Anote a URL do Vercel exibida acima!"
read -p "Cole a URL do Vercel aqui: " VERCEL_URL
echo ""

# 3. Configurar CORS (5 min)
echo "3️⃣ Configuring CORS..."
cd ..
railway variables set CORS_ORIGINS=$VERCEL_URL
railway up

echo ""
echo "✅ DEPLOY COMPLETO!"
echo ""
echo "🌐 URLs DE PRODUÇÃO:"
echo "   Dashboard: $VERCEL_URL"
echo "   API:       $RAILWAY_URL"
echo ""
echo "📊 PRÓXIMOS PASSOS:"
echo "   1. Acesse: $VERCEL_URL"
echo "   2. Verifique se dados reais aparecem"
echo "   3. Teste botão 'Run Test' em /agents"
echo ""
```

**Salvar como:** `deploy-production.sh`

**Executar:**
```bash
chmod +x deploy-production.sh
./deploy-production.sh
```

---

## ✅ VALIDAÇÃO FINAL

Após completar todas as tarefas críticas, execute este checklist:

```
[ ] Backend Railway está online
[ ] Dashboard Vercel está online
[ ] Dashboard exibe dados REAIS (não mockados)
[ ] Botão "Run Test" funciona
[ ] Logs do Railway mostram requisições
[ ] Novos testes aparecem no Supabase
[ ] CORS está configurado corretamente
[ ] Sem erros no console do navegador
```

---

## 🎯 RESUMO FINAL

### Para ter 100% funcional em produção, você precisa:

1. ✅ **Deploy Railway Backend** (15 min) - CRÍTICO
2. ✅ **Deploy Vercel Dashboard** (10 min) - CRÍTICO
3. ✅ **Configurar CORS** (5 min) - IMPORTANTE
4. ✅ **Testar integração** (10 min) - IMPORTANTE

**TEMPO TOTAL: ~40 minutos**

### O que já está pronto:

- ✅ Backend funcional localmente
- ✅ Dashboard funcional localmente
- ✅ Supabase configurado com dados reais
- ✅ Documentação completa
- ✅ Scripts de teste

**STATUS ATUAL: 75% completo**
**FALTA: 25% (apenas deploys)**

---

**Última atualização:** 31/12/2025 08:35 BRT
