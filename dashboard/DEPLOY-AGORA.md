# 🚀 DEPLOY AGORA - Guia Passo-a-Passo

**Vamos subir o projeto em produção AGORA!**

---

## 📋 PRÉ-REQUISITOS

Antes de começar, certifique-se de ter:

- [ ] Conta no Railway (https://railway.app)
- [ ] Conta no Vercel (https://vercel.com)
- [ ] Conta no GitHub (para deploy via Git)

---

## 🎯 OPÇÃO 1: DEPLOY VIA RAILWAY WEB (RECOMENDADO)

**Tempo:** ~20 minutos
**Vantagem:** Não precisa instalar nada

### PASSO 1: Deploy Backend no Railway

1. **Acesse:** https://railway.app/new

2. **Clique em:** "Deploy from GitHub repo"

3. **Se não tem repo no GitHub ainda:**

   Execute no terminal:
   ```bash
   cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework

   # Inicializar git (se ainda não tiver)
   git init
   git add .
   git commit -m "Initial commit - AI Factory V4"

   # Criar repo no GitHub e fazer push
   # (Você pode criar via GitHub web ou gh CLI)
   ```

4. **Ou use "Deploy from local directory":**
   - Clique em "Empty Project"
   - Conecte via GitHub ou upload zip

5. **Configurar variáveis de ambiente:**

   No Railway Dashboard → Settings → Variables, adicione:

   ```
   SUPABASE_URL=https://bfumywvwubvernvhjehk.supabase.co

   SUPABASE_SERVICE_ROLE_KEY=<SUA_SERVICE_ROLE_KEY_AQUI>

   ANTHROPIC_API_KEY=<SUA_ANTHROPIC_API_KEY_AQUI>

   API_KEY=sk-test-key-ai-factory-2025

   CORS_ORIGINS=http://localhost:3000
   ```

6. **Railway vai detectar automaticamente** que é um projeto Python com `requirements.txt`

7. **Aguarde o deploy** (~3-5 min)

8. **Anote a URL gerada:**
   ```
   https://SEU-PROJETO.railway.app
   ```

9. **Testar:**
   ```bash
   curl https://SEU-PROJETO.railway.app/health

   # Deve retornar:
   # {"status":"healthy","timestamp":"..."}
   ```

---

### PASSO 2: Deploy Dashboard no Vercel

1. **Acesse:** https://vercel.com/new

2. **Clique em:** "Import Git Repository"

3. **Ou faça upload do projeto:**
   - Faça zip da pasta `dashboard/`
   - Upload no Vercel

4. **Configurar projeto:**
   - Root Directory: `dashboard`
   - Framework Preset: Next.js
   - Build Command: `npm run build` (detectado automaticamente)

5. **Configurar variáveis de ambiente:**

   Em Settings → Environment Variables, adicione:

   ```
   NEXT_PUBLIC_SUPABASE_URL=https://bfumywvwubvernvhjehk.supabase.co

   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmdW15d3Z3dWJ2ZXJudmhqZWhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0MDM3OTksImV4cCI6MjA2Njk3OTc5OX0.60VyeZ8XaD6kz7Eh5Ov_nEeDtu5woMwMJYgUM-Sruao

   NEXT_PUBLIC_API_URL=https://SEU-PROJETO.railway.app

   API_KEY=sk-test-key-ai-factory-2025
   ```

   ⚠️ **IMPORTANTE:** Substitua `https://SEU-PROJETO.railway.app` pela URL real do Railway!

6. **Deploy** (~2-3 min)

7. **Anote a URL gerada:**
   ```
   https://SEU-PROJETO.vercel.app
   ```

---

### PASSO 3: Configurar CORS

1. **Volte no Railway Dashboard**

2. **Settings → Variables**

3. **Edite `CORS_ORIGINS`:**
   ```
   CORS_ORIGINS=https://SEU-PROJETO.vercel.app,http://localhost:3000
   ```

   ⚠️ **IMPORTANTE:** Use a URL REAL do Vercel!

4. **Salvar** (Railway vai fazer redeploy automaticamente)

---

### PASSO 4: Testar Tudo

1. **Acesse o Dashboard em produção:**
   ```
   https://SEU-PROJETO.vercel.app
   ```

2. **Verifique:**
   - [ ] Dashboard carrega sem erros
   - [ ] Dados REAIS aparecem (Dr. Alberto Correia, Isabela)
   - [ ] Score Trends mostra gráfico

3. **Teste o botão "Run Test":**
   - Vá em: `/agents`
   - Clique em "Run Test" em qualquer agente
   - Deve aparecer alert: "Test started successfully!"

4. **Verifique logs do Railway:**
   - Railway Dashboard → Deployments → Logs
   - Deve mostrar: `POST /api/test-agent`

5. **Verifique Supabase:**
   - https://supabase.com/dashboard
   - Table Editor → `test_results`
   - Deve ter novo registro

---

## 🎯 OPÇÃO 2: DEPLOY VIA CLI (SE CONSEGUIR INSTALAR)

### Instalar CLIs:

```bash
# Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Vercel CLI
npm install -g vercel
```

### Deploy Railway:

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework

railway login
railway init
railway variables set SUPABASE_URL=https://bfumywvwubvernvhjehk.supabase.co
railway variables set SUPABASE_SERVICE_ROLE_KEY=eyJh...
railway variables set ANTHROPIC_API_KEY=sk-ant-api03-jMK...
railway variables set API_KEY=sk-test-key-ai-factory-2025
railway up
```

### Deploy Vercel:

```bash
cd dashboard

vercel login
vercel --prod
```

---

## ✅ CHECKLIST FINAL

Após completar TODOS os passos:

```
[ ] Backend Railway está online
[ ] Dashboard Vercel está online
[ ] URL Railway anotada: https://_____.railway.app
[ ] URL Vercel anotada: https://_____.vercel.app
[ ] CORS configurado com URL do Vercel
[ ] Dashboard exibe dados REAIS
[ ] Botão "Run Test" funciona
[ ] Logs do Railway mostram requisições
[ ] Novos testes aparecem no Supabase
```

---

## 🆘 TROUBLESHOOTING

### Problema: Railway não faz build

**Solução:** Criar `Procfile` na raiz:
```
web: uvicorn server:app --host 0.0.0.0 --port $PORT
```

### Problema: Vercel dá erro de build

**Solução:** Verificar se `package.json` tem scripts corretos:
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

### Problema: CORS erro no navegador

**Solução:**
1. Verificar `CORS_ORIGINS` no Railway tem URL correta do Vercel
2. Fazer redeploy do Railway após alterar
3. Limpar cache do navegador (Cmd+Shift+R)

### Problema: Dashboard não exibe dados

**Solução:**
1. Abrir DevTools (F12) → Console
2. Verificar erros de rede
3. Confirmar `NEXT_PUBLIC_API_URL` está correto
4. Testar endpoint: `curl https://SEU-PROJETO.railway.app/health`

---

## 📊 URLS FINAIS

Após deploy completo, salve suas URLs:

```markdown
# 🌐 AI FACTORY V4 - PRODUÇÃO

## Frontend
- **Dashboard:** https://_____.vercel.app
- **Agents:** https://_____.vercel.app/agents
- **Tests:** https://_____.vercel.app/tests

## Backend
- **API:** https://_____.railway.app
- **Health:** https://_____.railway.app/health
- **Docs:** https://_____.railway.app/docs

## Database
- **Supabase:** https://supabase.com/dashboard/project/bfumywvwubvernvhjehk
```

---

## 🎉 PRONTO!

Depois de completar todos os passos, você terá:

✅ Backend em produção no Railway
✅ Dashboard em produção no Vercel
✅ Banco de dados no Supabase
✅ Sistema 100% funcional

**Tempo total:** ~30 minutos

---

**Última atualização:** 31/12/2025 08:40 BRT
