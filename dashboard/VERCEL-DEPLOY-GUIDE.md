# 🚀 Guia de Deploy no Vercel - Dashboard Next.js

## Passo a Passo para Conectar com Railway API

---

## 📋 Pré-requisitos

- [x] Railway API funcionando (URL: `https://seu-projeto.railway.app`)
- [x] Conta Vercel criada (https://vercel.com)
- [x] Git repository com código do dashboard
- [x] API_KEY definida

---

## 🎯 Método 1: Deploy via Vercel Dashboard (Recomendado)

### Passo 1: Importar Projeto
1. Acesse https://vercel.com/dashboard
2. Clique em **"Add New..."** → **"Project"**
3. Conecte seu GitHub/GitLab/Bitbucket
4. Selecione o repositório do dashboard
5. Clique em **"Import"**

### Passo 2: Configurar Build Settings
```
Framework Preset: Next.js
Root Directory: dashboard/ (se dashboard está em subdiretório)
Build Command: npm run build (ou deixar padrão)
Output Directory: .next (deixar padrão)
Install Command: npm install (deixar padrão)
```

### Passo 3: Adicionar Environment Variables

**IMPORTANTE**: Configure TODAS estas variáveis antes de fazer deploy!

Clique em **"Environment Variables"** e adicione:

#### Production Environment
| Name | Value | Environment |
|------|-------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | `https://bfumywvwubvernvhjehk.supabase.co` | Production, Preview, Development |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Production, Preview, Development |
| `NEXT_PUBLIC_API_URL` | `https://seu-projeto.railway.app` | **Production only** |
| `API_KEY` | `sua-api-key-segura` | Production, Preview, Development |

#### Preview/Development (Opcional)
| Name | Value | Environment |
|------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | **Development only** |
| `NEXT_PUBLIC_API_URL` | `https://staging-projeto.railway.app` | **Preview only** |

### Passo 4: Deploy!
1. Clique em **"Deploy"**
2. Aguarde build completar (~2-3 minutos)
3. Vercel fornecerá URL de produção: `https://seu-dashboard.vercel.app`

### Passo 5: Verificar Deploy
1. Acesse a URL fornecida
2. Verifique se dashboard carrega
3. Teste botão "Run Test"
4. Verifique console do browser (F12) para erros

---

## 🎯 Método 2: Deploy via Vercel CLI

### Instalação
```bash
npm i -g vercel
```

### Login
```bash
vercel login
```

### Deploy
```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard

# Deploy para preview (staging)
vercel

# Deploy para production
vercel --prod
```

### Adicionar Environment Variables via CLI
```bash
# Production
vercel env add NEXT_PUBLIC_API_URL production
# Cole: https://seu-projeto.railway.app

vercel env add API_KEY production
# Cole: sua-api-key-segura

vercel env add NEXT_PUBLIC_SUPABASE_URL production
# Cole: https://bfumywvwubvernvhjehk.supabase.co

vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# Cole: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Development
vercel env add NEXT_PUBLIC_API_URL development
# Cole: http://localhost:8000

# Fazer redeploy após adicionar env vars
vercel --prod
```

---

## 🔧 Configurar CORS no Railway

**IMPORTANTE**: Sem CORS, o dashboard não conseguirá se comunicar com a API!

### FastAPI (Python)
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Adicionar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",                    # Local dev
        "https://seu-dashboard.vercel.app",         # Production
        "https://*.vercel.app",                     # Preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Express.js (Node.js)
```javascript
// server.js
const express = require('express');
const cors = require('cors');

const app = express();

app.use(cors({
  origin: [
    'http://localhost:3000',
    'https://seu-dashboard.vercel.app',
    /\.vercel\.app$/  // Regex para preview deployments
  ],
  credentials: true
}));
```

**Commit e push** estas mudanças para o Railway fazer redeploy.

---

## 🧪 Testar Integração

### 1. Teste Local (antes de deploy)
```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard

# Configurar .env.local
cp .env.railway.template .env.local

# Editar .env.local com URL Railway
nano .env.local
# NEXT_PUBLIC_API_URL=https://seu-projeto.railway.app
# API_KEY=sua-api-key

# Rodar localmente
npm run dev

# Abrir browser
open http://localhost:3000

# Testar botão "Run Test"
```

### 2. Teste de Conexão com Railway
```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard

# Rodar script de teste
./test-railway-connection.sh https://seu-projeto.railway.app sua-api-key

# Output esperado:
# ✓ Health check endpoint
# ✓ Start test endpoint
# ✓ CORS configured
# ✓ .env.local exists
```

### 3. Teste Production (após deploy)
```bash
# Abrir URL do Vercel
open https://seu-dashboard.vercel.app

# F12 → Console
# Clicar em "Run Test"
# Verificar:
# - POST https://seu-projeto.railway.app/api/test-agent → 200 OK
# - Alert de sucesso
# - Score atualiza após ~30s
```

---

## 🐛 Troubleshooting

### Build Error: "Missing environment variables"
```
Error: NEXT_PUBLIC_SUPABASE_URL is not defined
```

**Solução**:
1. Ir em Vercel Dashboard → Settings → Environment Variables
2. Adicionar todas as variáveis listadas acima
3. Fazer redeploy: Deployments → ... → Redeploy

---

### Runtime Error: "Failed to fetch"
```
TypeError: Failed to fetch
```

**Causas possíveis**:
1. Railway API offline
2. URL incorreta
3. CORS não configurado

**Solução**:
```bash
# 1. Verificar se Railway está no ar
curl https://seu-projeto.railway.app/health

# 2. Verificar variável no Vercel
# Dashboard → Settings → Environment Variables
# NEXT_PUBLIC_API_URL deve ser https://seu-projeto.railway.app

# 3. Adicionar CORS no Railway (ver seção acima)
```

---

### CORS Error
```
Access to fetch at 'https://...' has been blocked by CORS policy
```

**Solução**:
1. Adicionar middleware CORS no Railway (ver seção "Configurar CORS")
2. Incluir domínio Vercel na lista de allowed origins
3. Fazer redeploy do Railway
4. Testar novamente

---

### Dados não aparecem
**Checklist**:
- [ ] Railway API está no ar
- [ ] Supabase tem dados nas tabelas
- [ ] Environment variables corretas no Vercel
- [ ] CORS configurado
- [ ] Build do Vercel passou sem erros

**Debug**:
```bash
# Ver logs do Vercel
vercel logs seu-dashboard.vercel.app

# Ver logs do Railway
railway logs

# Testar Supabase diretamente
# Supabase Dashboard → Table Editor
# Verificar se vw_agent_performance_summary tem registros
```

---

## 🔄 Workflow de Deploy

### Desenvolvimento Local
```bash
# 1. Fazer mudanças no código
git checkout -b feature/nova-funcionalidade

# 2. Testar localmente
npm run dev

# 3. Commit
git add .
git commit -m "feat: nova funcionalidade"

# 4. Push
git push origin feature/nova-funcionalidade
```

### Preview Deploy (Automático)
```
Vercel detecta novo branch/PR
→ Cria preview deployment automaticamente
→ URL: https://dashboard-git-feature-nova-funcionalidade.vercel.app
→ Testar nesta URL antes de merge
```

### Production Deploy (Automático)
```
Merge para main/master
→ Vercel detecta push para main
→ Faz deploy automático para production
→ URL: https://seu-dashboard.vercel.app
→ Rollback disponível se necessário
```

---

## 📊 Monitoramento

### Vercel Analytics (Opcional)
1. Vercel Dashboard → Analytics
2. Habilitar Web Analytics
3. Ver métricas de performance, usuários, etc

### Logs
```bash
# Ver logs em tempo real
vercel logs --follow

# Ver logs de produção
vercel logs --production

# Ver logs de preview
vercel logs --preview

# Ver logs de build específico
vercel logs [deployment-url]
```

---

## 🔐 Segurança

### Variáveis Sensíveis
- ✅ **API_KEY**: Marcar como "Sensitive" no Vercel
- ✅ **SUPABASE_ANON_KEY**: Marcar como "Sensitive"
- ✅ Nunca commitar `.env.local` no Git

### .gitignore
Verificar se `.env.local` está no `.gitignore`:
```bash
cat .gitignore | grep ".env"

# Deve conter:
# .env*.local
# .env.local
```

---

## 🎯 Checklist Final

### Antes do Deploy
- [ ] Código testado localmente
- [ ] `.env.local` configurado
- [ ] Railway API funcionando
- [ ] CORS configurado no Railway
- [ ] Supabase migrations executadas
- [ ] `.gitignore` não inclui `.env.local`

### Durante Deploy
- [ ] Environment variables adicionadas no Vercel
- [ ] Build passou sem erros
- [ ] Preview deployment testado
- [ ] Logs verificados

### Após Deploy
- [ ] Dashboard abre sem erros
- [ ] Stats carregam corretamente
- [ ] Botão "Run Test" funciona
- [ ] Realtime updates funcionam
- [ ] Erros são tratados corretamente
- [ ] Performance aceitável

---

## 📞 Comandos Úteis

```bash
# Deploy para preview
vercel

# Deploy para production
vercel --prod

# Ver env vars
vercel env ls

# Adicionar env var
vercel env add NOME_VARIAVEL

# Remover env var
vercel env rm NOME_VARIAVEL

# Ver logs
vercel logs --follow

# Rollback para deploy anterior
# Vercel Dashboard → Deployments → ... → Promote to Production

# Deletar projeto
vercel remove nome-projeto
```

---

## 🔗 Links Úteis

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Vercel Docs**: https://vercel.com/docs
- **Next.js Docs**: https://nextjs.org/docs
- **Supabase Dashboard**: https://supabase.com/dashboard
- **Railway Dashboard**: https://railway.app/dashboard

---

## 📁 Estrutura de Arquivos

```
dashboard/
├── .env.local                    # ⚠️ NÃO COMMITAR
├── .env.production               # Apenas referência
├── .env.railway.template         # Template para criar .env.local
├── .gitignore                    # Deve incluir .env.local
├── src/
│   ├── lib/
│   │   ├── api.ts               # ✅ Usa NEXT_PUBLIC_API_URL
│   │   ├── supabase.ts          # ✅ Usa NEXT_PUBLIC_SUPABASE_*
│   │   └── supabaseData.ts
│   └── hooks/
│       └── useAgents.ts         # ✅ Chama api.ts
├── RAILWAY-INTEGRATION.md       # 📖 Este guia
├── VERCEL-DEPLOY-GUIDE.md       # 📖 Guia de deploy
└── test-railway-connection.sh   # 🧪 Script de teste
```

---

**Status**: ✅ Pronto para deploy
**Próximo passo**: Executar deploy seguindo Método 1 ou 2 acima
