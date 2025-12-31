# 🗄️ ONDE ESTÃO AS TABELAS? - Guia Completo

**Data:** 31 de Dezembro de 2025
**Pergunta:** "Onde vejo as tabelas no Railway?"
**Resposta:** As tabelas **NÃO estão no Railway!** Estão no **Supabase**.

---

## 🎯 ARQUITETURA ATUAL

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARQUITETURA COMPLETA                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐         ┌─────────┐ │
│  │   VERCEL     │         │   RAILWAY    │         │SUPABASE │ │
│  │  (Frontend)  │────────▶│  (Backend)   │────────▶│  (DB)   │ │
│  │              │  HTTP   │              │  API    │         │ │
│  │  Dashboard   │         │  FastAPI     │         │ Tables  │ │
│  │  Next.js     │         │  Python      │         │ Views   │ │
│  └──────────────┘         └──────────────┘         └─────────┘ │
│                                                                  │
│  localhost:3000           localhost:8000        Supabase Cloud  │
│  (ou Vercel)              (ou Railway)          (PostgreSQL)    │
└─────────────────────────────────────────────────────────────────┘
```

**IMPORTANTE:**
- ❌ Railway **NÃO TEM** banco de dados próprio
- ✅ Railway **USA** Supabase como banco externo
- ✅ Tabelas estão **NO SUPABASE**, não no Railway

---

## 📍 ONDE VER AS TABELAS

### ✅ OPÇÃO 1: Supabase Dashboard (RECOMENDADO)

1. **Acesse:** https://supabase.com/dashboard
2. **Faça login**
3. **Selecione o projeto:** `bfumywvwubvernvhjehk` (AI Factory)
4. **Clique em:** `Table Editor` (menu lateral esquerdo)
5. **Você verá:**

```
┌─────────────────────────────────────────────────────────┐
│ Table Editor - Supabase Dashboard                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 📊 Tables (Schema: public)                              │
│                                                          │
│ ✅ agent_versions                    (1 row)            │
│ ✅ agent_metrics                     (0 rows)           │
│ ✅ agent_conversations               (1 row)            │
│ ✅ agent_conversation_messages       (1 row)            │
│ ✅ vw_agent_performance_summary      (VIEW - 4 rows)    │
│ ✅ vw_test_results_history           (VIEW)             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Caminho visual:**
```
Supabase Dashboard
  └─ Projects
       └─ bfumywvwubvernvhjehk (AI Factory)
            └─ Table Editor ← AQUI!
                 ├─ agent_versions
                 ├─ agent_metrics
                 ├─ agent_conversations
                 └─ agent_conversation_messages
```

---

### ✅ OPÇÃO 2: SQL Editor (Supabase)

1. **Acesse:** Supabase Dashboard
2. **Clique em:** `SQL Editor` (menu lateral)
3. **Execute:**

```sql
-- Ver todas as tabelas
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE';

-- Ver estrutura de uma tabela específica
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'agent_versions';

-- Ver dados de uma tabela
SELECT * FROM agent_versions LIMIT 10;
```

---

### ✅ OPÇÃO 3: Via Terminal (Script Python)

Já criamos o script! Execute:

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework
python3 check_tables.py
```

**Saída:**
```
✅ agent_versions                      | Existe | 1 registro(s)
✅ agent_metrics                       | Existe | 0 registro(s)
✅ agent_conversations                 | Existe | 1 registro(s)
✅ agent_conversation_messages         | Existe | 1 registro(s)
```

---

### ❌ OPÇÃO 4: Railway Dashboard

**NÃO é possível!** Railway não mostra as tabelas porque:

1. Railway só hospeda o **backend FastAPI** (código Python)
2. Banco de dados é **externo** (Supabase)
3. Railway não tem acesso direto ao Supabase

**O que você VÊ no Railway:**
```
Railway Dashboard
  └─ Seu Projeto (Backend)
       ├─ 📦 Deployments
       ├─ ⚙️  Variables (SUPABASE_URL, SUPABASE_KEY)
       ├─ 📊 Metrics (CPU, RAM)
       └─ 📝 Logs
```

**O que você NÃO VÊ no Railway:**
- ❌ Tabelas do banco
- ❌ Dados do Supabase
- ❌ SQL Editor

---

## 🔐 CREDENCIAIS SUPABASE

**URL do projeto:**
```
https://bfumywvwubvernvhjehk.supabase.co
```

**Anon Key (pública):**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmdW15d3Z3dWJ2ZXJudmhqZWhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0MDM3OTksImV4cCI6MjA2Njk3OTc5OX0.60VyeZ8XaD6kz7Eh5Ov_nEeDtu5woMwMJYgUM-Sruao
```

**Service Role Key (privada):**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmdW15d3Z3dWJ2ZXJudmhqZWhrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTQwMzc5OSwiZXhwIjoyMDY2OTc5Nzk5fQ.fdTsdGlSqemXzrXEU4ov1SUpeDn_3bSjOingqkSAWQE
```

---

## 📊 TABELAS ENCONTRADAS

### 1. `agent_versions` (1 registro)

**Estrutura:**
```sql
CREATE TABLE agent_versions (
  id UUID PRIMARY KEY,
  agent_name TEXT,
  version TEXT,
  created_at TIMESTAMP,
  status TEXT
);
```

### 2. `agent_metrics` (0 registros - vazio)

**Estrutura:**
```sql
CREATE TABLE agent_metrics (
  id UUID PRIMARY KEY,
  agent_version_id UUID REFERENCES agent_versions(id),
  metric_name TEXT,
  metric_value NUMERIC,
  created_at TIMESTAMP
);
```

### 3. `agent_conversations` (1 registro)

**Estrutura:**
```sql
CREATE TABLE agent_conversations (
  id UUID PRIMARY KEY,
  agent_version_id UUID,
  started_at TIMESTAMP,
  ended_at TIMESTAMP,
  status TEXT
);
```

### 4. `agent_conversation_messages` (1 registro)

**Estrutura:**
```sql
CREATE TABLE agent_conversation_messages (
  id UUID PRIMARY KEY,
  conversation_id UUID REFERENCES agent_conversations(id),
  role TEXT,
  content TEXT,
  created_at TIMESTAMP
);
```

---

## 🚀 COMO O RAILWAY ACESSA AS TABELAS

O **Railway backend** acessa as tabelas via **Supabase Python SDK**:

**Código (src/supabase_client.py):**
```python
from supabase import create_client

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.client = create_client(self.url, self.key)

    def get_agent_versions(self):
        return self.client.from_('agent_versions').select('*').execute()
```

**Fluxo:**
```
Railway Backend (Python)
  └─ supabase_client.py
       └─ create_client(SUPABASE_URL, SUPABASE_KEY)
            └─ HTTP Request para Supabase
                 └─ PostgreSQL Database
                      └─ Tables (agent_versions, etc.)
```

---

## ✅ COMO VERIFICAR SE ESTÁ FUNCIONANDO

### Teste 1: Via Python Script

```bash
python3 check_tables.py
```

**Esperado:**
```
✅ agent_versions                      | Existe | 1 registro(s)
✅ agent_metrics                       | Existe | 0 registro(s)
✅ agent_conversations                 | Existe | 1 registro(s)
✅ agent_conversation_messages         | Existe | 1 registro(s)

🎉 Todas as tabelas necessárias existem!
```

---

### Teste 2: Via Supabase Dashboard

1. Acesse: https://supabase.com/dashboard
2. Projeto: `bfumywvwubvernvhjehk`
3. Table Editor
4. Clique em `agent_versions`
5. Você deve ver **1 registro**

---

### Teste 3: Via cURL (API REST)

```bash
curl 'https://bfumywvwubvernvhjehk.supabase.co/rest/v1/agent_versions?select=*' \
  -H 'apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmdW15d3Z3dWJ2ZXJudmhqZWhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0MDM3OTksImV4cCI6MjA2Njk3OTc5OX0.60VyeZ8XaD6kz7Eh5Ov_nEeDtu5woMwMJYgUM-Sruao'
```

**Esperado:**
```json
[
  {
    "id": "uuid-aqui",
    "agent_name": "Dr. Alberto Correia",
    "version": "v3.0-hyperpersonalized",
    "created_at": "2025-01-15T10:30:00Z",
    "status": "active"
  }
]
```

---

## 🎯 RESUMO PARA O USUÁRIO

### ❓ "Onde vejo as tabelas no Railway?"

**Resposta:** Você **NÃO VÊ** as tabelas no Railway porque:

1. ❌ Railway **não tem banco próprio**
2. ✅ Railway **usa Supabase externo**
3. ✅ Tabelas estão **no Supabase Dashboard**

---

### ✅ Onde VER as tabelas:

1. **Supabase Dashboard** → Table Editor (RECOMENDADO)
2. **Supabase SQL Editor** → Execute queries
3. **Python Script** → `python3 check_tables.py`
4. **cURL** → API REST do Supabase

---

### ❌ Onde NÃO VER as tabelas:

- ❌ Railway Dashboard (não tem banco)
- ❌ Railway Logs (só mostra logs do backend)
- ❌ Railway Deployments (só mostra deploys)

---

## 📞 LINKS ÚTEIS

- **Supabase Project:** https://supabase.com/dashboard/project/bfumywvwubvernvhjehk
- **Table Editor:** https://supabase.com/dashboard/project/bfumywvwubvernvhjehk/editor
- **SQL Editor:** https://supabase.com/dashboard/project/bfumywvwubvernvhjehk/sql
- **API Docs:** https://supabase.com/dashboard/project/bfumywvwubvernvhjehk/api

---

**Última atualização:** 31/12/2025 08:30 BRT
