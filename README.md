# AI Factory V4 - Testing Framework

Sistema completo de testes, validação e auto-melhoria para agentes IA.
Usa LLM-as-Judge (Claude Opus) para avaliar agentes em 5 dimensões.

---

## Visão Geral

O AI Factory Testing Framework automatiza o processo de:
- **Testar agentes** com cenários realistas (20+ casos padrão)
- **Avaliar com LLM-as-Judge** usando Claude Opus
- **Gerar relatórios HTML** profissionais
- **Auto-melhorar** agentes com score < 8.0 (Reflection Loop)
- **Integrar com Supabase** como source of truth
- **API REST** para integração com n8n e outros sistemas

---

## Arquitetura

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

## Quick Start

### 1. Instalação

```bash
# Clone o repositório
git clone https://github.com/mottivme/ai-factory-testing-framework
cd ai-factory-testing-framework

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas chaves
```

### 2. Configurar Variáveis de Ambiente

```bash
# .env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbG...
ANTHROPIC_API_KEY=sk-ant-api...
REPORTS_OUTPUT_DIR=./reports
```

### 3. Rodar Migrations

```bash
# Definir DATABASE_URL
export DATABASE_URL='postgresql://user:pass@host:5432/db'

# Executar migrations
psql $DATABASE_URL -f migrations/001_add_testing_columns_to_agent_versions.sql
psql $DATABASE_URL -f migrations/002_create_agenttest_test_results.sql
psql $DATABASE_URL -f migrations/003_create_agenttest_skills.sql
psql $DATABASE_URL -f migrations/004_create_dashboard_views.sql
```

### 4. Iniciar Servidor

```bash
# Desenvolvimento
uvicorn main:app --reload --port 8000

# Produção
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Exemplos de Uso (curl)

### Health Check

```bash
# Verificar status do servidor
curl -X GET http://localhost:8000/health

# Resposta esperada:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T10:30:00",
#   "version": "1.0.0",
#   "database": "connected"
# }
```

### Ping (para load balancers)

```bash
curl -X GET http://localhost:8000/ping

# Resposta:
# {"message": "pong", "timestamp": "2024-01-15T10:30:00.123Z"}
```

### Rodar Teste Individual

```bash
curl -X POST http://localhost:8000/api/v1/test/run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "uuid-do-agente",
    "test_name": "Lead frio - primeira mensagem",
    "input_text": "Oi",
    "expected_behavior": "Cumprimento amigável + pergunta aberta",
    "rubric_focus": ["tone", "engagement"]
  }'

# Resposta:
# {
#   "test_id": "test_123",
#   "agent_id": "uuid-do-agente",
#   "test_name": "Lead frio - primeira mensagem",
#   "status": "completed",
#   "score": 8.5,
#   "feedback": "Boa abertura com tom amigável...",
#   "execution_time": 2.3,
#   "timestamp": "2024-01-15T10:30:00"
# }
```

### Rodar Batch de Testes

```bash
curl -X POST http://localhost:8000/api/v1/test/batch \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "uuid-do-agente",
    "run_name": "Teste Completo SDR",
    "test_cases": [
      {
        "agent_id": "uuid-do-agente",
        "test_name": "Lead frio",
        "input_text": "Oi",
        "expected_behavior": "Cumprimento + pergunta",
        "rubric_focus": ["tone", "engagement"]
      },
      {
        "agent_id": "uuid-do-agente",
        "test_name": "Pergunta de preço",
        "input_text": "Quanto custa?",
        "expected_behavior": "Âncora valor + qualificação",
        "rubric_focus": ["compliance", "completeness"]
      }
    ]
  }'

# Resposta:
# {
#   "run_id": "batch_1705312200123",
#   "agent_id": "uuid-do-agente",
#   "test_count": 2,
#   "status": "queued",
#   "status_endpoint": "/api/v1/test/status/batch_1705312200123",
#   "timestamp": "2024-01-15T10:30:00.123Z"
# }
```

### Verificar Status de Batch

```bash
curl -X GET http://localhost:8000/api/v1/test/status/batch_1705312200123

# Resposta (em progresso):
# {
#   "run_id": "batch_1705312200123",
#   "status": "processing",
#   "completed": 1,
#   "total": 2
# }

# Resposta (completo):
# {
#   "run_id": "batch_1705312200123",
#   "status": "completed",
#   "overall_score": 8.2,
#   "results": [...]
# }
```

### Buscar Resultados de um Agente

```bash
curl -X GET "http://localhost:8000/api/v1/agents/uuid-do-agente/results?limit=5&offset=0"

# Resposta:
# {
#   "agent_id": "uuid-do-agente",
#   "count": 5,
#   "results": [
#     {
#       "id": "test-result-uuid",
#       "overall_score": 8.5,
#       "test_details": {...},
#       "created_at": "2024-01-15T10:30:00"
#     },
#     ...
#   ]
# }
```

### Buscar Métricas do Sistema

```bash
curl -X GET http://localhost:8000/api/v1/metrics

# Resposta:
# {
#   "timestamp": "2024-01-15T10:30:00.123Z",
#   "metrics": {
#     "total_agents": 15,
#     "total_tests": 234,
#     "avg_score": 7.8
#   }
# }
```

---

## Uso Programático (Python)

### Teste Rápido

```python
import asyncio
from src import run_quick_test

async def main():
    result = await run_quick_test(
        agent_version_id="uuid-do-agente",
        test_cases=[
            {
                "name": "Lead frio",
                "input": "Oi",
                "expected_behavior": "Cumprimento + pergunta"
            }
        ]
    )
    print(f"Score: {result['overall_score']}")
    print(f"Report: {result['report_url']}")

asyncio.run(main())
```

### Uso Completo

```python
from src import TestRunner, Evaluator, ReportGenerator, SupabaseClient

# Inicializar componentes
supabase = SupabaseClient()
evaluator = Evaluator()
reporter = ReportGenerator(output_dir="./reports")

# Criar runner
runner = TestRunner(
    supabase_client=supabase,
    evaluator=evaluator,
    report_generator=reporter
)

# Executar testes
result = await runner.run_tests("uuid-do-agente")

print(f"Score: {result['overall_score']}")
print(f"Strengths: {result['test_details']['strengths']}")
print(f"Weaknesses: {result['test_details']['weaknesses']}")
```

### Avaliação Direta

```python
from src import Evaluator

evaluator = Evaluator()

result = await evaluator.evaluate(
    agent={"name": "SDR", "system_prompt": "..."},
    skill=None,
    test_results=[
        {"name": "test1", "input": "Oi", "agent_response": "Olá!"}
    ]
)

print(f"Score: {result['overall_score']}")
print(f"Scores: {result['scores']}")
```

---

## Rubrica de Avaliação

Agentes são avaliados em 5 dimensões:

| Dimensão | Peso | Descrição |
|----------|------|-----------|
| **Completeness** | 25% | BANT completo? Coletou Budget, Authority, Need, Timeline? |
| **Tone** | 20% | Tom consultivo e profissional? Empático? |
| **Engagement** | 20% | Lead engajou? Conversa fluiu? |
| **Compliance** | 20% | Seguiu guardrails e instruções? |
| **Conversion** | 15% | Conseguiu converter/agendar? |

**Threshold de aprovação:** Score >= 8.0

---

## Estrutura do Projeto

```
ai-factory-testing-framework/
├── migrations/              # SQL migrations
│   ├── 001_*.sql
│   ├── 002_*.sql
│   └── ...
├── src/                     # Código Python
│   ├── __init__.py          # Package exports
│   ├── supabase_client.py   # Cliente Supabase
│   ├── test_runner.py       # Orquestrador de testes
│   ├── evaluator.py         # LLM-as-Judge (Claude Opus)
│   ├── report_generator.py  # Gerador de relatórios HTML
│   └── reflection_loop.py   # Auto-melhoria (em desenvolvimento)
├── templates/               # Templates Jinja2
│   └── report.html
├── main.py                  # FastAPI application
├── server.py                # Servidor alternativo
├── config.yaml              # Configurações
├── requirements.txt         # Dependências Python
└── README.md                # Este arquivo
```

---

## Deploy no Railway

### Via CLI

```bash
# Login
railway login

# Inicializar projeto
railway init

# Deploy
railway up
```

### Variáveis de Ambiente (Railway)

```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbG...
ANTHROPIC_API_KEY=sk-ant-api...
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

---

## Troubleshooting

### Erro: "SUPABASE_URL and SUPABASE_KEY must be set"

Verifique se as variáveis de ambiente estão definidas:
```bash
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

### Erro: "ANTHROPIC_API_KEY must be set"

Defina a variável:
```bash
export ANTHROPIC_API_KEY=sk-ant-api...
```

### Rate Limit do Claude

Se encontrar rate limits:
- Reduza concorrência de testes
- Implemente exponential backoff
- Use batching

### Relatórios não sendo gerados

Verifique:
1. Permissões do diretório de saída
2. Se o template existe em `templates/report.html`
3. Logs em `logs/framework.log`

---

## Documentação Adicional

- **[API_REFERENCE.md](API_REFERENCE.md)** - Documentação completa da API
- **[HANDOFF.md](HANDOFF.md)** - Guia de implementação
- **[ARCHITECTURE.txt](ARCHITECTURE.txt)** - Design do sistema
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solução de problemas

---

## Contribuindo

1. Leia `HANDOFF.md`
2. Escolha uma task do TODO
3. Crie branch feature
4. Submeta PR com testes

---

## Licença

MIT License - Copyright (c) 2024 MOTTIVME

---

## Suporte

- Slack: #ai-factory-testing
- Email: dev@mottivme.com
- Docs: https://docs.mottivme.com/testing-framework

---

**Built with love by MOTTIVME**
