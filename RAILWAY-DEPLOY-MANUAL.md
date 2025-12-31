# 🚀 Deploy Manual no Railway - Solução Definitiva

**Problema:** Railway está com cache antigo que não limpa.

**Solução:** Criar novo serviço do zero.

---

## 📋 PASSO A PASSO

### 1️⃣ Deletar Serviço Atual (Opcional)

1. No Railway, vá no serviço "web"
2. Clique nos **3 pontinhos** (⋮)
3. **Settings** → **Danger Zone** → **Delete Service**
4. Confirmar

---

### 2️⃣ Criar Novo Serviço

1. No Railway, clique em **"+ New"**
2. Selecione **"GitHub Repo"**
3. Escolha: **`marcosdanielsf/ai-factory-backend`**
4. Railway vai detectar automaticamente:
   - ✅ Linguagem: Python
   - ✅ Build: Nixpacks
   - ✅ Start command: `web: python server.py` (do Procfile)

---

### 3️⃣ Configurar Variáveis de Ambiente

Vá em **Variables** e adicione:

```bash
# Supabase
SUPABASE_URL=https://bfumywvwubvernvhjehk.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<COPIE_DA_INTERFACE_DO_RAILWAY>

# Anthropic
ANTHROPIC_API_KEY=<COPIE_DA_INTERFACE_DO_RAILWAY>

# API
API_KEY=sk-test-key-ai-factory-2025

# CORS (temporário - depois atualizar com URL do Vercel)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

**⚠️ IMPORTANTES:**
- O Railway **injeta automaticamente** a variável `PORT`, então **NÃO adicione** `PORT` manualmente!
- A variável **DEVE** ser `SUPABASE_SERVICE_ROLE_KEY` (não `SUPABASE_KEY`)
- O código suporta ambas, mas `SUPABASE_SERVICE_ROLE_KEY` tem prioridade

---

### 4️⃣ Aguardar Deploy

- Aguarde ~3-5 minutos
- Acompanhe os logs em **Deployments**

**Você DEVE ver:**
```
Starting server at 0.0.0.0:XXXX (ENV PORT: XXXX)
INFO:     Started server process [1]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:XXXX (Press CTRL+C to quit)
==================================================
AI Factory Testing Framework API
==================================================
Supabase: Connected
Config: /app/config.yaml
API Key: ENABLED
==================================================
```

---

### 5️⃣ Anotar URL Gerada

1. Vá em **Settings** do serviço
2. Seção **Networking** → **Public Domain**
3. Copie a URL (exemplo: `https://web-production-abc123.up.railway.app`)

---

### 6️⃣ Testar Backend

Execute o script de teste:

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework
./test-railway-production.sh
```

Quando solicitado, cole a URL do Railway.

**Testes esperados:**
- ✅ Health check (200 OK)
- ✅ API Docs (200 OK)
- ✅ Supabase Connection (200 OK)
- ✅ Test Agent Endpoint (200 OK)

---

## 🎯 POR QUE ESSA SOLUÇÃO FUNCIONA?

1. ✅ **Procfile correto:** `web: python server.py`
2. ✅ **server.py lê PORT:** `port = int(os.environ.get('PORT', 8000))`
3. ✅ **Sem railway.toml:** Não há conflito de configuração
4. ✅ **Sem Dockerfile:** Nixpacks detecta Python automaticamente
5. ✅ **Deploy limpo:** Sem cache antigo

---

## 📊 Próximos Passos

Após backend funcionando:

1. ✅ Anotar URL do Railway
2. 📦 Deploy Dashboard no Vercel
3. 🔗 Configurar CORS com URL do Vercel
4. 🧪 Testar integração completa

---

**Última atualização:** 31/12/2025 10:10 BRT
