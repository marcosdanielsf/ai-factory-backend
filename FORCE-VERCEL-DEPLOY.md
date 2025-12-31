# 🚨 FORÇAR DEPLOY DO VERCEL - Dashboard

**Problema:** Vercel não está pegando os commits mais recentes do GitHub

**Commits no GitHub:** ✅ 530e056 e 7feac9f (ambos pushed)
**Deploy atual:** ❌ Versão antiga (sem as correções)

---

## 🔧 SOLUÇÃO 1: Redeploy Manual (RÁPIDO)

### Via Vercel Dashboard:

1. Acesse: https://vercel.com/dashboard
2. Selecione o projeto do dashboard
3. Vá em **Deployments**
4. Encontre o deployment mais recente
5. Clique nos **3 pontinhos** (⋮) → **Redeploy**
6. Selecione **"Use existing build cache"** → **DESMARCAR** ❌
7. Clique em **"Redeploy"**

**OU**

### Via Vercel CLI (se tiver instalado):

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard
vercel --prod --force
```

---

## 🔧 SOLUÇÃO 2: Commit Vazio para Trigger (ALTERNATIVA)

Se o Vercel não está detectando os pushes:

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework

# Criar commit vazio para forçar webhook
git commit --allow-empty -m "chore: force vercel deploy

Trigger deploy to pick up latest changes:
- 530e056: fix 404 em /agents/[id]
- 7feac9f: fix /tests mockData"

git push origin main
```

**Aguarde 2-3 minutos** e verifique novamente.

---

## 🔧 SOLUÇÃO 3: Verificar Configuração do Vercel

### Possíveis problemas:

#### 1. Branch incorreto configurado:
- Ir em: **Settings** → **Git** → **Production Branch**
- Verificar se está em: `main` (não `master`)

#### 2. Auto Deploy desabilitado:
- Ir em: **Settings** → **Git**
- Verificar se **"Auto Deploy"** está ENABLED ✅

#### 3. Build Command incorreto:
- Ir em: **Settings** → **Build & Development Settings**
- Verificar:
  - Framework Preset: **Next.js**
  - Build Command: `cd dashboard && npm run build` ou `next build`
  - Output Directory: `dashboard/.next` ou `.next`
  - Install Command: `npm install`

#### 4. Root Directory incorreto:
- Ir em: **Settings** → **General**
- Root Directory: `dashboard` (se o Next.js está em subpasta)

---

## 🔍 DIAGNÓSTICO: Qual commit está deployado?

### Para verificar qual versão está no ar:

1. Vá em **Deployments** no Vercel
2. Veja o commit SHA do deployment "Ready"
3. Compare com: `530e056` (deveria ser este ou mais recente)

**Se for diferente:** Vercel não está pegando os commits novos

---

## ⚡ AÇÃO URGENTE AGORA:

### Opção A: Se você tem acesso ao Vercel Dashboard
1. Vá em Deployments
2. Veja qual commit está deployado
3. Se não for `530e056`, clique em **Redeploy**
4. **DESMARQUE** "Use existing cache"
5. Aguarde 2-3 minutos

### Opção B: Se não tem acesso
```bash
# Executar este comando:
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework
git commit --allow-empty -m "chore: force vercel redeploy"
git push origin main

# Aguardar 3-5 minutos e testar novamente
```

---

## 📊 VERIFICAÇÃO APÓS DEPLOY:

### Teste 1: Verificar commit deployado
```bash
# No Vercel Deployments, deve mostrar:
# Commit: 530e056 fix(dashboard): corrigir 404...
# Status: Ready
```

### Teste 2: Testar URL
```bash
# Abrir e clicar em um agente:
open https://dashboard-ks2jfjj6h-marcosdanielsfs-projects.vercel.app

# DEVE funcionar (não 404)
```

### Teste 3: Verificar Console
```bash
# Abrir DevTools (F12) → Console
# NÃO deve ter erros de fetch/404
```

---

## 🚨 SE NADA FUNCIONAR:

### Criar novo projeto no Vercel (última opção):

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard

# Instalar Vercel CLI se não tiver
npm i -g vercel

# Deploy novo
vercel --prod

# Seguir o wizard:
# 1. Login na conta
# 2. Criar novo projeto
# 3. Configurar environment variables
# 4. Deploy
```

---

**Causa raiz provável:**
- Vercel está configurado para deployar de um branch diferente
- Ou Auto Deploy está desabilitado
- Ou há um problema no webhook GitHub → Vercel

**Solução mais rápida:** Redeploy manual no Dashboard do Vercel

---

**Data:** 31/12/2025 14:55 BRT
**Status:** Aguardando ação manual no Vercel
