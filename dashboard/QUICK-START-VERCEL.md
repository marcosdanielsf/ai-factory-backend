# ⚡ Quick Start - Deploy Dashboard para Vercel

## 5 Minutos do Local ao Production

---

## 🎯 Passo 1: Preparar Ambiente Local (1 min)

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard

# Copiar template de env
cp .env.railway.template .env.local

# Editar .env.local
nano .env.local
```

**Preencher**:
```bash
NEXT_PUBLIC_API_URL=https://SEU-PROJETO.railway.app
API_KEY=SUA-API-KEY-AQUI
```

Salvar: `Ctrl+X` → `Y` → `Enter`

---

## 🎯 Passo 2: Testar Localmente (1 min)

```bash
# Instalar dependências (se ainda não instalou)
npm install

# Rodar dashboard
npm run dev
```

**Abrir**: http://localhost:3000

**Verificar**:
- ✅ Dashboard carrega
- ✅ Stats aparecem
- ✅ Agentes listados
- ✅ Botão "Run Test" funciona

Se tudo OK → **Ctrl+C** para parar

---

## 🎯 Passo 3: Deploy no Vercel (2 min)

### Opção A: Via Dashboard (Mais fácil)

1. Acesse: https://vercel.com/new
2. Conecte GitHub/GitLab
3. Selecione repositório do dashboard
4. **IMPORTANTE**: Antes de clicar "Deploy", adicione env vars:

```
NEXT_PUBLIC_SUPABASE_URL = https://bfumywvwubvernvhjehk.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_URL = https://SEU-PROJETO.railway.app
API_KEY = SUA-API-KEY
```

5. Clicar **"Deploy"**
6. Aguardar ~2 min
7. Vercel fornece URL: `https://seu-dashboard.vercel.app`

### Opção B: Via CLI (Mais rápido se já tem Vercel CLI)

```bash
# Instalar CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard
vercel --prod
```

Quando perguntar sobre env vars → Responder manualmente ou usar:
```bash
vercel env add NEXT_PUBLIC_API_URL production
# Cole: https://seu-projeto.railway.app

vercel env add API_KEY production
# Cole: sua-api-key

vercel env add NEXT_PUBLIC_SUPABASE_URL production
# Cole: https://bfumywvwubvernvhjehk.supabase.co

vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# Cole: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🎯 Passo 4: Configurar CORS no Railway (1 min)

**CRÍTICO**: Sem CORS, dashboard não funciona!

### Se Railway usa FastAPI (Python):

```bash
# Conectar via Railway CLI
railway link

# Editar main.py
railway run nano main.py
```

Adicionar **ANTES** das rotas:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://seu-dashboard.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

```bash
# Commit e push
git add main.py
git commit -m "Add CORS for Vercel"
git push

# Railway faz redeploy automático
```

### Se Railway usa Express (Node):

```javascript
const cors = require('cors');

app.use(cors({
  origin: [
    'http://localhost:3000',
    'https://seu-dashboard.vercel.app',
    /\.vercel\.app$/
  ]
}));
```

---

## 🎯 Passo 5: Testar Production (30 seg)

```bash
# Abrir dashboard
open https://seu-dashboard.vercel.app

# F12 → Console
# Clicar em "Run Test" em qualquer agente
# Verificar console:
```

**Esperado**:
```
POST https://seu-projeto.railway.app/api/test-agent 200 OK
Alert: "Test started successfully!"
```

**Se der erro CORS**:
```
Access-Control-Allow-Origin error
→ Voltar ao Passo 4 e verificar CORS
```

---

## ✅ Checklist Rápido

- [ ] `.env.local` criado com Railway URL
- [ ] `npm run dev` funciona localmente
- [ ] Deploy no Vercel feito
- [ ] Env vars adicionadas no Vercel
- [ ] CORS configurado no Railway
- [ ] Dashboard abre em produção
- [ ] Botão "Run Test" funciona
- [ ] Dados carregam do Supabase

---

## 🐛 Troubleshooting Rápido

### Dashboard não carrega
```bash
# Ver logs
vercel logs --follow

# Verificar env vars
vercel env ls
```

### Erro "Failed to fetch"
```bash
# Testar Railway API
curl https://seu-projeto.railway.app/health

# Deve retornar 200 OK
```

### Erro CORS
```
Access to fetch blocked by CORS
→ Adicionar CORS no Railway (Passo 4)
```

### Dados não aparecem
```bash
# Verificar Supabase
# Dashboard → Table Editor
# vw_agent_performance_summary deve ter dados
```

---

## 🚀 Próximos Passos (Opcional)

1. **Custom Domain**:
   ```
   Vercel → Settings → Domains
   → Add seu-dashboard.com
   → Seguir instruções DNS
   ```

2. **Analytics**:
   ```
   Vercel → Analytics → Enable
   ```

3. **Monitoring**:
   ```bash
   vercel logs --follow
   ```

---

## 📞 Comandos Úteis

```bash
# Redeploy
vercel --prod

# Ver logs
vercel logs

# Rollback
# Dashboard → Deployments → Promote anterior

# Remover projeto
vercel remove
```

---

**Tempo total**: ~5 minutos
**Status**: Pronto para produção! 🎉
