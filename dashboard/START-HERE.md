# 🚀 START HERE - Dashboard Railway Integration

## Você está no lugar certo!

Este dashboard Next.js precisa ser conectado à Railway API. **Tudo o que você precisa está documentado aqui.**

---

## ⚡ Quick Start (5 minutos)

```bash
# 1. Configurar ambiente
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard
cp .env.railway.template .env.local
nano .env.local  # Preencher com URL Railway

# 2. Testar conexão
./test-railway-connection.sh https://seu-projeto.railway.app sua-api-key

# 3. Testar localmente
npm run dev
open http://localhost:3000

# 4. Deploy
vercel --prod
```

**Guia completo**: [QUICK-START-VERCEL.md](./QUICK-START-VERCEL.md)

---

## 📚 Guias Disponíveis

| Guia | Quando usar |
|------|-------------|
| **[QUICK-START-VERCEL.md](./QUICK-START-VERCEL.md)** | Para deploy rápido (5 min) |
| **[README-RAILWAY-VERCEL.md](./README-RAILWAY-VERCEL.md)** | Índice completo de documentação |
| **[RAILWAY-INTEGRATION.md](./RAILWAY-INTEGRATION.md)** | Detalhes de integração Railway |
| **[VERCEL-DEPLOY-GUIDE.md](./VERCEL-DEPLOY-GUIDE.md)** | Deploy passo a passo |
| **[API-FILES-REFERENCE.md](./API-FILES-REFERENCE.md)** | Referência técnica do código |
| **[ARCHITECTURE-DIAGRAM.md](./ARCHITECTURE-DIAGRAM.md)** | Diagramas visuais |

---

## 🎯 O que preciso fazer?

### Opção A: Já tenho URL do Railway
```bash
# Siga: QUICK-START-VERCEL.md
# Tempo: 5 minutos
```

### Opção B: Preciso entender a arquitetura
```bash
# Leia: ARCHITECTURE-DIAGRAM.md
# Depois: RAILWAY-INTEGRATION.md
# Tempo: 15 minutos
```

### Opção C: Preciso fazer deploy completo
```bash
# Siga: VERCEL-DEPLOY-GUIDE.md
# Tempo: 10-15 minutos
```

---

## 🔑 Environment Variables

```bash
# Copiar template
cp .env.railway.template .env.local

# Preencher com:
NEXT_PUBLIC_API_URL=https://seu-projeto.railway.app
API_KEY=sua-api-key-segura
```

---

## 🧪 Testar Tudo

```bash
# Script de validação automática
./test-railway-connection.sh https://railway-url api-key

# Testa:
# ✓ Railway API online
# ✓ Endpoints funcionando
# ✓ CORS configurado
# ✓ Env vars corretas
```

---

## ✅ Checklist

- [ ] URL do Railway obtida
- [ ] `.env.local` criado e preenchido
- [ ] Script de teste executado com sucesso
- [ ] Dashboard funciona localmente (`npm run dev`)
- [ ] Deploy no Vercel feito
- [ ] Dashboard production funciona

---

## 🐛 Problemas?

| Erro | Ver |
|------|-----|
| CORS error | [RAILWAY-INTEGRATION.md](./RAILWAY-INTEGRATION.md#troubleshooting) |
| Failed to fetch | [VERCEL-DEPLOY-GUIDE.md](./VERCEL-DEPLOY-GUIDE.md#troubleshooting) |
| Build error | [VERCEL-DEPLOY-GUIDE.md](./VERCEL-DEPLOY-GUIDE.md#troubleshooting) |
| Env vars | [API-FILES-REFERENCE.md](./API-FILES-REFERENCE.md#environment-variables) |

---

## 📞 Comandos Úteis

```bash
# Local
npm run dev                           # Rodar dashboard
./test-railway-connection.sh URL KEY  # Testar API

# Vercel
vercel --prod                         # Deploy
vercel logs --follow                  # Ver logs
vercel env add NOME                   # Adicionar env var

# Railway
railway logs --follow                 # Ver logs
```

---

## 🎓 Estrutura da Documentação

```
START-HERE.md                    ← Você está aqui
    ↓
QUICK-START-VERCEL.md           ← Quick start 5 min
    ↓
README-RAILWAY-VERCEL.md        ← Índice completo
    ↓
├── RAILWAY-INTEGRATION.md      ← Integração Railway
├── VERCEL-DEPLOY-GUIDE.md      ← Deploy Vercel
├── API-FILES-REFERENCE.md      ← Referência código
└── ARCHITECTURE-DIAGRAM.md     ← Diagramas
```

---

**Status**: ✅ Pronto para deploy
**Próximo passo**: Abrir [QUICK-START-VERCEL.md](./QUICK-START-VERCEL.md)
