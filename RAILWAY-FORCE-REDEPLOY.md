# 🔄 Forçar Redeploy no Railway

**Problema:** Railway não está fazendo deploy automático das últimas alterações no GitHub.

**Solução:** Forçar redeploy manual.

---

## ✅ CÓDIGO ESTÁ CORRETO

Testes locais confirmam que o código funciona:

```bash
✅ SupabaseClient initialized successfully
✅ Query successful: 1 records found
```

**Últimos commits:**
```
9df224e Add debug endpoint to check env vars
93b7f3b Fix Supabase env var to use SUPABASE_SERVICE_ROLE_KEY
75e7e60 Fix httpx version conflict with supabase 2.9.1
```

---

## 📋 PASSO A PASSO - FORÇAR REDEPLOY

### Opção 1: Redeploy via Interface (RECOMENDADO)

1. Acesse https://railway.app
2. Entre no projeto **ai-factory-backend**
3. Clique no serviço **web**
4. Vá na aba **Deployments**
5. No deploy mais recente, clique nos **3 pontinhos** (⋮)
6. Clique em **"Redeploy"**
7. Aguarde 2-3 minutos

### Opção 2: Trigger via Commit Vazio

Se a Opção 1 não funcionar:

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework
git commit --allow-empty -m "Force Railway redeploy"
git push origin main
```

---

## 🧪 APÓS REDEPLOY - TESTAR

Execute este comando para verificar se funcionou:

```bash
# 1. Health check
curl -s https://ai-factory-backend-production.up.railway.app/health | jq '.'

# Esperado: "supabase_connected": true

# 2. Debug endpoint (temporário)
curl -s https://ai-factory-backend-production.up.railway.app/debug/env | jq '.'

# Esperado:
# {
#   "SUPABASE_URL": "https://bfumywvwubvernvhjehk.s...",
#   "SUPABASE_SERVICE_ROLE_KEY": "SET",
#   "SUPABASE_KEY": "SET",
#   "supabase_client_initialized": true
# }
```

---

## 🔍 O QUE FOI CORRIGIDO

1. ✅ **httpx version conflict** - Atualizado `requirements.txt` linha 28:
   ```python
   httpx>=0.26,<0.28  # Compatible with supabase 2.9.1
   ```

2. ✅ **Supabase env var** - Atualizado `src/supabase_client.py` linha 22:
   ```python
   self.key = key or os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
   ```

3. ✅ **Debug endpoint** - Adicionado `/debug/env` no `server.py` para diagnóstico

---

## ⚠️ SE CONTINUAR FALHANDO

Se após redeploy o Supabase ainda aparecer como `disconnected`:

1. Verifique as **variáveis de ambiente** no Railway:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY` (ou `SUPABASE_KEY`)

2. Teste o endpoint de debug:
   ```bash
   curl https://ai-factory-backend-production.up.railway.app/debug/env
   ```

3. Verifique os **logs do Railway**:
   - Procure por "Supabase client initialized"
   - Procure por erros de importação ou dependências

---

**Última atualização:** 31/12/2025 11:50 BRT
