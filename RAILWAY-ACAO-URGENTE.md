# 🚨 AÇÃO URGENTE - Railway Com Problema Crítico

## ⚠️ SITUAÇÃO

**Railway NÃO está fazendo deploy há mais de 1 hora, apesar de 10+ commits.**

O código está 100% funcional localmente, mas o Railway está "congelado" em uma versão antiga.

---

## ✅ VOCÊ DEVE FAZER AGORA (3 PASSOS)

### PASSO 1: Verificar Se Há Deploy FAILED no Railway

1. Acesse https://railway.app
2. Projeto: `ai-factory-backend`
3. Vá na aba **Deployments**
4. Procure por deploys com status **FAILED** (vermelho)

**Se houver FAILED:**
- Clique no deploy
- Leia os logs de erro
- Copie e me envie os logs

**Se NÃO houver FAILED:**
- Significa que Railway não está detectando os commits do GitHub
- Vá para PASSO 2

---

### PASSO 2: Verificar Conexão GitHub → Railway

1. Railway → Projeto `ai-factory-backend` → **Settings**
2. Seção **Source**
3. Verifique:
   - ✅ **Repository:** `marcosdanielsf/ai-factory-backend`
   - ✅ **Branch:** `main`
   - ✅ **Auto Deploy:** deve estar **ATIVO** (toggle verde)

**Se Auto Deploy estiver desativado:**
- Clique para ATIVAR
- Aguarde 2 minutos
- Railway deve iniciar deploy automaticamente

**Se estiver ativo mas não deployando:**
- Vá para PASSO 3

---

### PASSO 3: DELETAR E RECRIAR SERVIÇO (SOLUÇÃO DEFINITIVA)

**Esta é a única solução 100% garantida quando Railway está com cache travado.**

#### 3.1 - Deletar Serviço Atual

1. Railway → Projeto `ai-factory-backend`
2. Clique no serviço **web**
3. **Settings** → Role até o final → **Danger Zone**
4. **"Delete Service"**
5. Confirmar

#### 3.2 - Criar Novo Serviço

1. No projeto, clique **"+ New Service"**
2. Selecione **"GitHub Repo"**
3. Escolha: **`marcosdanielsf/ai-factory-backend`**
4. Railway detectará automaticamente:
   - ✅ Python
   - ✅ Procfile
   - ✅ Nixpacks

#### 3.3 - Configurar Variáveis de Ambiente

Vá em **Variables** e adicione exatamente estas:

```bash
SUPABASE_URL=https://bfumywvwubvernvhjehk.supabase.co

SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmdW15d3Z3dWJ2ZXJudmhqZWhrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTQwMzc5OSwiZXhwIjoyMDY2OTc5Nzk5fQ.yJnP-PwZFg0pUDEYSuT3lNbjXE8cOZSIZu-hSkGFGYs

ANTHROPIC_API_KEY=<SUA_CHAVE_ANTHROPIC>

API_KEY=sk-test-key-ai-factory-2025

CORS_ORIGINS=http://localhost:3000,http://localhost:3001,https://dashboard-marcosdaniels-projects.vercel.app
```

**⚠️ IMPORTANTE:**
- NÃO adicione `PORT` (Railway injeta automaticamente)
- Substitua `<SUA_CHAVE_ANTHROPIC>` pela sua chave real

#### 3.4 - Aguardar Deploy

1. Railway iniciará build automaticamente
2. Aguarde 3-5 minutos
3. Acompanhe os logs em **Deployments**

#### 3.5 - Gerar Domínio Público

1. **Settings** → **Networking** → **Public Networking**
2. **"Generate Domain"**
3. Copie a URL gerada (ex: `https://web-production-xyz.up.railway.app`)

---

## 🧪 TESTAR APÓS NOVO DEPLOY

Execute os testes:

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework

# Teste 1: Debug endpoint DEVE funcionar
curl https://[SUA_URL_RAILWAY]/debug/env

# Esperado:
# {
#   "SUPABASE_URL": "https://bfumywvwubvernvhjehk.s...",
#   "SUPABASE_SERVICE_ROLE_KEY": "SET",
#   "supabase_client_initialized": true
# }

# Teste 2: Health check DEVE mostrar Supabase conectado
curl https://[SUA_URL_RAILWAY]/health

# Esperado:
# {
#   "status": "healthy",
#   "supabase_connected": true
# }

# Teste 3: Script completo
./test-railway-production.sh
```

---

## 📊 POR QUE DELETAR E RECRIAR FUNCIONA?

1. ✅ **Cache limpo** - Sem dependências antigas
2. ✅ **Build do zero** - Railway detecta código mais recente
3. ✅ **Configuração limpa** - Sem conflitos de settings
4. ✅ **Nixpacks atualizado** - Usa buildpack mais recente

---

## 🎯 PRÓXIMOS PASSOS (APÓS BACKEND OK)

1. ✅ **Backend Railway** ← VOCÊ RESOLVE AGORA
2. 📦 **Deploy Dashboard Vercel** ← EU FAÇO ASSIM QUE BACKEND OK
3. 🔗 **Configurar CORS** ← Atualizar com URL do Vercel
4. 🧪 **Teste E2E** ← Dashboard → API → Supabase

---

## 💡 ALTERNATIVA RÁPIDA (SE TIVER ACESSO AO RAILWAY CLI)

Se você tem o Railway CLI instalado:

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework
railway link
railway up --detach
```

Isso força um novo deploy via CLI.

---

**⏰ TEMPO ESTIMADO:**
- Opção 1 (verificar configs): 2-5 minutos
- Opção 2 (deletar/recriar): 10-15 minutos

**PRIORIDADE:** 🔴 CRÍTICA

**STATUS:** Aguardando sua ação manual no Railway.

---

**Última atualização:** 31/12/2025 12:20 BRT
