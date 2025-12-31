# 🏭 AI Factory V4 - Testing Framework

Sistema completo de testes, validação e auto-melhoria para agentes IA.

---

## 🎯 O Que É

Framework Python que:
- ✅ **Testa agentes** automaticamente com 20+ cenários
- ✅ **Avalia com LLM-as-Judge** (Claude Opus)
- ✅ **Gera relatórios HTML** profissionais
- ✅ **Auto-melhora** agentes com score < 8.0
- ✅ **Integra com Supabase** (source of truth)
- ✅ **API REST** para integração com n8n

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────┐
│   N8N Workflows (AI Factory V3)    │
│   - Cria agent_versions             │
└────────────┬────────────────────────┘
             │
             ▼ webhook
┌─────────────────────────────────────┐
│   Testing Framework (Este Repo)    │
│   - Roda testes                     │
│   - Avalia com Claude Opus          │
│   - Gera relatórios                 │
│   - Auto-melhora se necessário      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│   Supabase (Database)               │
│   - agent_versions                  │
│   - agenttest_test_results          │
│   - agenttest_skills                │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│   Dashboard (Next.js)               │
│   - Visualiza scores                │
│   - Histórico de testes             │
│   - Skills management               │
└─────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Setup

```bash
# Clone
git clone https://github.com/mottivme/ai-factory-testing-framework
cd ai-factory-testing-framework

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install
pip install -r requirements.txt

# Environment
cp .env.example .env
# Edit .env with your keys
```

### 2. Run Migrations

```bash
# Set database URL
export DATABASE_URL='postgresql://user:pass@host:5432/db'

# Run migrations
psql $DATABASE_URL -f migrations/001_add_testing_columns_to_agent_versions.sql
psql $DATABASE_URL -f migrations/002_create_agenttest_test_results.sql
psql $DATABASE_URL -f migrations/003_create_agenttest_skills.sql
psql $DATABASE_URL -f migrations/004_create_dashboard_views.sql
```

### 3. Test

```bash
# Test single agent (with Supabase)
python test_e2e.py --agent-id <AGENT_VERSION_ID>

# Test offline (no Supabase needed)
python test_offline.py

# Auto-discover and test all pending
python test_e2e.py
```

### 4. Start API Server

```bash
# Development
uvicorn server:app --reload --port 8000

# Production
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📁 Project Structure

```
ai-factory-testing-framework/
├── migrations/              # SQL migrations
│   ├── 001_*.sql
│   ├── 002_*.sql
│   └── ...
│
├── src/                     # Python source
│   ├── __init__.py          # ✅ DONE - Package exports
│   ├── supabase_client.py   # ✅ DONE - Database client
│   ├── test_runner.py       # ✅ DONE - Test orchestration
│   ├── evaluator.py         # ✅ DONE - LLM-as-Judge (Claude Opus)
│   ├── report_generator.py  # ✅ DONE - HTML reports
│   ├── reflection_loop.py   # ⏳ TODO - Auto-improvement
│   └── skill_loader.py      # ⏳ TODO - Skills from files
│
├── scripts/                 # Utility scripts
│   ├── sync_skills_to_supabase.py
│   ├── generate_knowledge_base.py
│   └── ...
│
├── skills/                  # Skills (Markdown)
│   ├── isabella-sdr/
│   ├── assembly-line/
│   └── _templates/
│
├── templates/               # Jinja2 templates
│   └── report.html
│
├── tests/                   # Unit tests
│
├── server.py                # FastAPI server
├── config.yaml              # Configuration
├── requirements.txt         # Python deps
├── HANDOFF.md              # ⭐ START HERE
└── README.md               # This file
```

---

## 📊 Database Schema

### New Tables

1. **agenttest_test_results**
   - Stores test results
   - Links to agent_versions
   - Includes scores, details, report URL

2. **agenttest_skills**
   - Stores skills (instructions, examples, rubric)
   - Synced from Obsidian/local files
   - Versioned per agent

### Modified Tables

1. **agent_versions**
   - Added: `last_test_score`, `last_test_at`
   - Added: `framework_approved`, `test_report_url`
   - Added: `reflection_count`

### New Views

1. **vw_agent_performance_summary**
2. **vw_latest_test_results**
3. **vw_agent_conversations_summary**
4. **vw_test_results_history**
5. **vw_agents_needing_testing**

---

## 🎨 Skills System

Skills são arquivos Markdown que definem:
- **INSTRUCTIONS.md**: Custom Instructions (para Claude Project)
- **EXAMPLES.md**: Few-shot examples
- **RUBRIC.md**: Evaluation criteria
- **test-cases.json**: 20+ test scenarios

**Sincronização:**
- Local (Obsidian) ↔ Supabase (bidirecional)
- Auto-geração de KNOWLEDGE.md com dados reais

---

## 🧪 Testing

### Test Suite Example

```json
{
  "test_cases": [
    {
      "name": "Lead frio - primeira mensagem",
      "input": "Oi",
      "expected_behavior": "Pergunta aberta sobre interesse",
      "rubric_focus": ["tone", "engagement"]
    },
    {
      "name": "Lead pergunta preço",
      "input": "Quanto custa?",
      "expected_behavior": "Âncora valor + qualificação BANT",
      "rubric_focus": ["compliance", "completeness"]
    }
  ]
}
```

### Rubric (5 Dimensions)

1. **Completeness (25%)**: BANT completo?
2. **Tone (20%)**: Tom consultivo, empático?
3. **Engagement (20%)**: Lead respondeu múltiplas vezes?
4. **Compliance (20%)**: Seguiu guardrails?
5. **Conversion (15%)**: Agendou/converteu?

**Threshold:** 8.0/10 para aprovação

---

## 🔄 Reflection Loop (Auto-Improvement)

Workflow:
1. Agent testa e recebe score < 8.0
2. Framework analisa `weaknesses` e `failures`
3. Gera prompt melhorado (v2)
4. Cria nova `agent_version` com v2
5. Testa v2 automaticamente
6. Se v2 > v1: aprova e ativa
7. Se v2 ≤ v1: rollback, mantém v1

---

## 🌐 API Endpoints

```
POST   /api/test-agent           # Queue test
GET    /api/agents                # List all agents
GET    /api/agent/{id}            # Agent details
GET    /api/agent/{id}/tests      # Test history
GET    /api/agent/{id}/skill      # Current skill
POST   /api/agent/{id}/skill      # Update skill
GET    /api/test-results/{id}     # Test result details
```

---

## 📈 Metrics & Monitoring

Dashboard mostra:
- Score médio por agente
- Conversas últimos 7/30 dias
- Taxa de aprovação
- Histórico de melhorias (reflection count)
- Tokens consumidos / custo

---

## 🔐 Environment Variables

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhb...
SUPABASE_SERVICE_ROLE_KEY=eyJhb...  # Admin operations

# Anthropic
ANTHROPIC_API_KEY=sk-ant-api...

# Optional
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

---

## 🐛 Troubleshooting

### Common Issues

1. **Migrations fail**
   - Check `DATABASE_URL` is correct
   - Ensure user has CREATE TABLE permissions
   - Check if tables already exist

2. **Claude Opus rate limit**
   - Implement exponential backoff
   - Reduce concurrent tests
   - Use batching

3. **Reports not generating**
   - Check `/mnt/user-data/outputs/` permissions
   - Verify Jinja2 template exists
   - Check logs in `logs/framework.log`

---

## 📚 Documentation

- **[HANDOFF.md](HANDOFF.md)** - ⭐ Start here for implementation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design
- **[API.md](API.md)** - API documentation
- **[SKILLS.md](SKILLS.md)** - Skills system guide

---

## 🤝 Contributing

1. Read `HANDOFF.md`
2. Pick a task from TODO list
3. Create feature branch
4. Submit PR with tests

---

## 📄 License

MIT License - Copyright (c) 2024 MOTTIVME

---

## 🙏 Credits

- **Marcos Daniels** - Product & Architecture
- **Claude (Anthropic)** - Code generation
- **AI Factory Team** - Testing & feedback

---

## 📞 Support

- Slack: #ai-factory-testing
- Email: dev@mottivme.com
- Docs: https://docs.mottivme.com/testing-framework

---

**Built with ❤️ by MOTTIVME**
