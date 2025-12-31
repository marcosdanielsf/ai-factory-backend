# 🔍 Como Verificar e Forçar Deploy no Vercel

**Problema:** Código foi commitado mas não aparece no dashboard em produção

**Causa:** Vercel pode estar:
- Usando cache antigo
- Não detectou o novo commit
- Precisa de redeploy manual

---

## ✅ PASSO A PASSO - VERIFICAR DEPLOY

### 1. Acesse o Dashboard do Vercel

```
https://vercel.com/marcosdanielsfs-projects/dashboard
```

### 2. Verifique a Última Deployment

Na lista de deployments, procure por:
- ✅ Commit `5666c0e` (trigger vercel deploy)
- ✅ Commit `2ae0b15` (feat: Implementa Prompt Studio)

**Status esperado:** "Ready" (verde)

### 3. Se NÃO estiver lá ou estiver "Building":

**Opção A - Aguardar 2-3 minutos**
- Vercel pode estar fazendo build agora
- Refresh a página a cada 30 segundos

**Opção B - Forçar Redeploy Manual:**

#### 3.1 Clique no último deployment (topo da lista)

#### 3.2 Clique nos 3 pontinhos (...) no canto superior direito

#### 3.3 Selecione "Redeploy"

#### 3.4 **IMPORTANTE:** DESMARQUE a opção:
```
☐ Use existing Build Cache
```

#### 3.5 Clique em "Redeploy"

#### 3.6 Aguarde 2-3 minutos até status = "Ready"

---

## 🔍 VERIFICAR SE O CÓDIGO ESTÁ LÁ

### Opção 1: Verificar Logs de Build

1. Clique no deployment mais recente
2. Vá em "Building" → "View Function Logs"
3. Procure por:
```
✓ Collecting page data
✓ Generating static pages
  ├ ○ /
  ├ ○ /agents
  ├ ○ /prompt-studio  ← DEVE APARECER AQUI!
  └ ○ /tests
```

### Opção 2: Verificar Source Files

1. Clique no deployment
2. Vá em "Source"
3. Navegue para: `dashboard/src/app/`
4. Verifique se a pasta `prompt-studio/` existe

---

## 🧪 TESTAR EM PRODUÇÃO

Após deploy concluído (status "Ready"):

### 1. Abra a URL de produção:
```
https://dashboard-ks2jfjj6h-marcosdanielsfs-projects.vercel.app
```

### 2. Limpe o cache do navegador:
- **Chrome/Edge:** Ctrl+Shift+R (Windows) ou Cmd+Shift+R (Mac)
- **Firefox:** Ctrl+F5 (Windows) ou Cmd+Shift+R (Mac)
- **Safari:** Cmd+Option+E, depois Cmd+R

### 3. Verifique o menu superior:
```
Overview | Agents | Prompt Studio | Tests
                    ↑
                DEVE TER ESTE LINK!
```

### 4. Clique em "Prompt Studio"

**URL esperada:**
```
https://dashboard-ks2jfjj6h-marcosdanielsfs-projects.vercel.app/prompt-studio
```

### 5. Se abrir a página:
✅ **SUCESSO!** Deploy funcionou!

### 6. Se der 404:
❌ **Deploy não pegou os arquivos novos**
→ Siga instruções abaixo

---

## 🚨 SE CONTINUAR NÃO FUNCIONANDO

### Problema: Vercel não está pegando os commits

#### Solução 1: Verificar Webhook GitHub → Vercel

1. Vá em: https://github.com/marcosdanielsf/ai-factory-backend/settings/hooks
2. Procure pelo webhook do Vercel
3. Clique em "Edit"
4. Verifique "Recent Deliveries"
5. Se tiver erro (X vermelho), clique em "Redeliver"

#### Solução 2: Reconectar Repositório

1. Vercel Dashboard → Settings → Git
2. Clique em "Disconnect"
3. Clique em "Connect Git Repository"
4. Selecione o repositório novamente

#### Solução 3: Deploy Manual via CLI

```bash
# Instalar Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd dashboard
vercel --prod
```

---

## 📊 CHECKLIST COMPLETO

- [ ] Acessei https://vercel.com/marcosdanielsfs-projects/dashboard
- [ ] Verifiquei se commit `2ae0b15` está na lista
- [ ] Status do deployment = "Ready" (verde)
- [ ] Forcei redeploy (se necessário)
- [ ] Desmarcquei "Use existing Build Cache"
- [ ] Aguardei build terminar (2-3 min)
- [ ] Limpei cache do navegador (Ctrl+Shift+R)
- [ ] Acessei /prompt-studio
- [ ] Página carregou com sucesso
- [ ] Editor apareceu
- [ ] Lista de agentes carregou

---

## 🐛 ERROS COMUNS

### Erro 1: "Module not found: Can't resolve '@/components/prompt-studio/...'"

**Causa:** Arquivos não foram incluídos no build

**Solução:**
1. Verifique se arquivos existem no Source do deployment
2. Force redeploy sem cache

### Erro 2: "404 - This page could not be found"

**Causa:** Rota não foi gerada

**Solução:**
1. Verifique logs de build
2. Procure por erros de TypeScript
3. Force redeploy sem cache

### Erro 3: Página carrega mas fica em branco

**Causa:** Erro de JavaScript no cliente

**Solução:**
1. Abra DevTools (F12)
2. Vá em "Console"
3. Procure por erros em vermelho
4. Me envie o erro para debug

---

## 📞 SE PRECISAR DE AJUDA

Me envie:
1. Screenshot do Vercel Dashboard (lista de deployments)
2. Screenshot do último deployment (detalhes)
3. Screenshot do erro (se houver)
4. Logs de build (se houver erro)

---

## ✅ CONFIRMAÇÃO DE SUCESSO

Quando funcionar, você verá:

```
┌─────────────────────────────────────────────┐
│ Prompt Studio                               │
│ ─────────────────────────────────────────── │
│                                             │
│ ┌───────┐  ┌──────────────┐  ┌──────────┐ │
│ │Versões│  │ Editor       │  │Config    │ │
│ │       │  │              │  │          │ │
│ │ v2.1  │  │ Você é a Nina│  │Tom: Amig.│ │
│ │ v2.2  │  │ ...          │  │Proibidas │ │
│ │       │  │              │  │          │ │
│ └───────┘  └──────────────┘  └──────────┘ │
│                                             │
│          [Sandbox] [Salvar]                 │
└─────────────────────────────────────────────┘
```

**Pronto para editar prompts!** 🎉
