# AI FACTORY V4 - TESTING FRAMEWORK
## HANDOFF DOCUMENT - Continue Building

**Status:** 🏗️ Foundation Created (40% complete)  
**Next Owner:** Claude Code  
**Estimated Completion:** 12-16 hours

---

## ✅ WHAT'S ALREADY DONE

### 1. Database Migrations (100%)
```
✅ migrations/001_add_testing_columns_to_agent_versions.sql
✅ migrations/002_create_agenttest_test_results.sql
✅ migrations/003_create_agenttest_skills.sql
✅ migrations/004_create_dashboard_views.sql
```

**Run these migrations:**
```bash
psql $DATABASE_URL -f migrations/001_add_testing_columns_to_agent_versions.sql
psql $DATABASE_URL -f migrations/002_create_agenttest_test_results.sql
psql $DATABASE_URL -f migrations/003_create_agenttest_skills.sql
psql $DATABASE_URL -f migrations/004_create_dashboard_views.sql
```

### 2. Core Python Files (30%)
```
✅ config.yaml
✅ requirements.txt
✅ src/supabase_client.py (complete)
🟡 src/test_runner.py (skeleton only)
```

---

## 🚧 WHAT NEEDS TO BE BUILT

### Priority 1: Core Framework (8-10h)

#### A. `src/evaluator.py`
**Purpose:** LLM-as-Judge using Claude Opus to evaluate agent responses

```python
"""
Evaluator usando Claude Opus para avaliar agentes.

Método principal:
- evaluate(agent, skill, test_results) -> Dict com scores

Rubrica (5 dimensões):
1. Completeness (25%): BANT completo?
2. Tone (20%): Tom consultivo?
3. Engagement (20%): Lead engajou?
4. Compliance (20%): Seguiu guardrails?
5. Conversion (15%): Converteu/agendou?

Retorna:
{
  'overall_score': 8.5,
  'scores': {
    'completeness': 9.0,
    'tone': 8.5,
    ...
  },
  'strengths': [...],
  'weaknesses': [...],
  'failures': [...],
  'warnings': [...]
}
```

**Key Implementation Points:**
- Use Anthropic SDK (`anthropic` package)
- Load rubric from skill or use default
- Batch evaluate all test_results in single Claude call
- Extract scores from Claude's response (use structured output)

**Example Prompt Structure:**
```
You are evaluating an AI agent's performance.

AGENT INFO:
- Name: {agent_name}
- Purpose: {purpose}

RUBRIC:
{rubric from skill or default}

TEST RESULTS:
{all test cases with input/output}

Evaluate and return JSON:
{
  "overall_score": 8.5,
  "scores": {"completeness": 9.0, ...},
  "strengths": ["..."],
  "weaknesses": ["..."]
}
```

---

#### B. `src/report_generator.py`
**Purpose:** Generate beautiful HTML reports

```python
"""
Gera relatórios HTML dos testes.

Método principal:
- generate_html_report(agent, evaluation, test_results) -> report_url

Usa Jinja2 templates.
Salva em /mnt/user-data/outputs/test-reports/
Retorna URL para o relatório.
"""
```

**Template Structure (`templates/report.html`):**
```html
<!DOCTYPE html>
<html>
<head>
  <title>Test Report - {{agent_name}} v{{version}}</title>
  <style>
    /* Tailwind CSS via CDN or inline */
  </style>
</head>
<body>
  <h1>{{agent_name}} - Test Report</h1>
  
  <section class="summary">
    <h2>Overall Score: {{overall_score}}/10</h2>
    <div class="score-breakdown">
      {% for dimension, score in scores.items() %}
        <div>{{dimension}}: {{score}}/10</div>
      {% endfor %}
    </div>
  </section>
  
  <section class="test-cases">
    {% for test in test_results %}
      <div class="test-case">
        <h3>{{test.name}}</h3>
        <p><strong>Input:</strong> {{test.input}}</p>
        <p><strong>Agent Response:</strong> {{test.agent_response}}</p>
        <p><strong>Score:</strong> {{test.score}}/10</p>
      </div>
    {% endfor %}
  </section>
  
  <section class="feedback">
    <h2>Strengths</h2>
    <ul>
      {% for strength in strengths %}
        <li>{{strength}}</li>
      {% endfor %}
    </ul>
    
    <h2>Weaknesses</h2>
    <ul>
      {% for weakness in weaknesses %}
        <li>{{weakness}}</li>
      {% endfor %}
    </ul>
  </section>
</body>
</html>
```

---

#### C. Complete `src/test_runner.py`
**What's Missing:**
1. `_load_test_cases()` - Load from skill.test_cases or file
2. `_run_single_test()` - Actually simulate conversation with agent
3. Agent simulation logic (call GHL API or simulate locally)

**Agent Simulation Options:**
```python
# Option 1: Call actual agent via GHL webhook
# - Mais realista
# - Mais lento
# - Requer GHL configurado

# Option 2: Simulate locally with Claude
# - Use agent.system_prompt
# - Call Anthropic API directly
# - Mais rápido, mais controlado
```

**Recommendation:** Start with Option 2 (local simulation)

---

#### D. `src/reflection_loop.py`
**Purpose:** Auto-improve agents that score < 8.0

```python
"""
Reflection Loop - Auto-melhoria de agentes.

Workflow:
1. Detecta agent com score < 8.0
2. Analisa weaknesses
3. Gera prompt melhorado (v2)
4. Cria nova agent_version
5. Testa v2
6. Se v2 > v1: aprova
7. Se v2 <= v1: rollback
"""

async def improve_agent(agent_id: str, test_results: Dict):
    """
    Tenta melhorar um agente automaticamente.
    """
    # 1. Carregar agent atual
    agent = supabase.get_agent_version(agent_id)
    
    # 2. Gerar prompt melhorado
    improved_prompt = await generate_improved_prompt(
        current_prompt=agent['system_prompt'],
        weaknesses=test_results['weaknesses'],
        failures=test_results['failures']
    )
    
    # 3. Criar agent_version v2
    new_agent_id = create_agent_version(
        base_agent=agent,
        new_prompt=improved_prompt,
        version=agent['version'] + 1
    )
    
    # 4. Testar v2
    v2_results = await test_runner.run_tests(new_agent_id)
    
    # 5. Comparar
    if v2_results['overall_score'] > test_results['overall_score']:
        # Aprovar v2
        supabase.update_agent_version(new_agent_id, status='active')
        logger.info(f"Agent improved: {test_results['overall_score']} -> {v2_results['overall_score']}")
    else:
        # Rollback
        supabase.update_agent_version(new_agent_id, status='archived')
        logger.info("Improvement failed, rolled back")
```

---

### Priority 2: Skills System (4-6h)

#### E. `src/skill_loader.py`
```python
"""
Carrega skills de arquivos Markdown.

Estrutura esperada:
skills/
├── isabella-sdr/
│   ├── INSTRUCTIONS.md
│   ├── EXAMPLES.md
│   ├── RUBRIC.md
│   └── test-cases.json
"""

def load_skill(agent_name: str) -> Dict:
    """
    Carrega skill de skills/{agent_name}/
    
    Returns:
        {
            'instructions': str,
            'examples': str,
            'rubric': str,
            'test_cases': List[Dict]
        }
    """
    pass
```

#### F. `scripts/sync_skills_to_supabase.py`
```bash
# Upload skills locais para Supabase
python scripts/sync_skills_to_supabase.py --agent isabella-sdr
```

#### G. `scripts/generate_knowledge_base.py`
```python
"""
Gera KNOWLEDGE.md automaticamente.

Inputs:
- agent_version (Supabase)
- test_results (últimos 10)
- conversations (últimas 50, high score)
- metrics (últimos 30 dias)

Output:
- skills/{agent}/KNOWLEDGE.md (completo)
"""
```

---

### Priority 3: API REST (2-3h)

#### H. `server.py` - Complete FastAPI
**Endpoints Needed:**
```python
POST /api/test-agent
  Body: {"agent_version_id": "uuid"}
  Returns: {"status": "queued", "agent_id": "uuid"}

GET /api/agents
  Returns: List of all agents with scores

GET /api/agent/{agent_id}
  Returns: Agent details + latest test

GET /api/agent/{agent_id}/tests
  Returns: Test history

GET /api/agent/{agent_id}/skill
  Returns: Current skill

POST /api/agent/{agent_id}/skill
  Body: {instructions, examples, rubric}
  Returns: Skill ID

GET /api/test-results/{test_id}
  Returns: Full test result + report URL
```

---

### Priority 4: Skills Templates (2h)

#### I. Create Default Skills
```
skills/
├── _templates/
│   ├── INSTRUCTIONS.md.template
│   ├── EXAMPLES.md.template
│   ├── RUBRIC.md.template
│   └── test-cases.json.template
│
├── isabella-sdr/
│   ├── INSTRUCTIONS.md
│   ├── KNOWLEDGE.md (auto-generated)
│   ├── EXAMPLES.md
│   ├── RUBRIC.md
│   └── test-cases.json (20 casos)
│
└── generic-sdr/
    └── ... (fallback quando não tem skill específico)
```

---

## 🎯 IMPLEMENTATION ORDER

### Week 1: Core Testing (Days 1-3)
```
Day 1:
✅ Run migrations
✅ Test Supabase connection
✅ Create src/evaluator.py
✅ Test evaluation with mock data

Day 2:
✅ Create src/report_generator.py
✅ Create Jinja2 template
✅ Complete src/test_runner.py
✅ End-to-end test (mock agent)

Day 3:
✅ Agent simulation (local with Claude)
✅ Integration test with real agent
✅ Fix bugs
```

### Week 2: Auto-Improvement (Days 4-5)
```
Day 4:
✅ Create src/reflection_loop.py
✅ Test prompt improvement
✅ Test versioning

Day 5:
✅ Integration with test_runner
✅ A/B testing v1 vs v2
```

### Week 3: Skills + API (Days 6-8)
```
Day 6:
✅ Create skill_loader.py
✅ Create sync scripts
✅ Test skill loading

Day 7:
✅ Complete server.py (FastAPI)
✅ Test all endpoints
✅ CORS, auth, etc

Day 8:
✅ Create skill templates
✅ Generate isabella-sdr skill
✅ Documentation
```

---

## 🔧 DEVELOPMENT COMMANDS

### Setup
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
export SUPABASE_URL='https://xxx.supabase.co'
export SUPABASE_KEY='eyJ...'
export ANTHROPIC_API_KEY='sk-ant-...'

# 4. Run migrations
psql $DATABASE_URL -f migrations/001_add_testing_columns_to_agent_versions.sql
# ... (todas as migrations)
```

### Testing
```bash
# Run single agent test
python -m src.test_runner --agent-id <UUID>

# Run tests for all pending agents
python -m src.test_runner --auto-discover

# Generate knowledge base
python scripts/generate_knowledge_base.py --agent isabella-sdr
```

### Server
```bash
# Development (hot reload)
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 📊 SUCCESS CRITERIA

**Phase 1 Complete When:**
- [ ] Migrations rodando sem erros
- [ ] Agent pode ser testado via Python
- [ ] Score é calculado corretamente
- [ ] Relatório HTML é gerado
- [ ] Resultados salvos no Supabase

**Phase 2 Complete When:**
- [ ] Agent com score < 8.0 é melhorado automaticamente
- [ ] Versão melhorada é testada
- [ ] Comparação v1 vs v2 funciona

**Phase 3 Complete When:**
- [ ] API REST funcional
- [ ] N8N pode chamar /api/test-agent
- [ ] Skills podem ser sincronizados
- [ ] KNOWLEDGE.md é gerado automaticamente

---

## 🐛 KNOWN ISSUES / NOTES

1. **Agent Simulation:** Decidir entre GHL real vs Claude local
2. **Test Cases:** Precisam ser expandidos (20+ casos por modo)
3. **Report Styling:** HTML pode ser melhorado com Tailwind
4. **Rate Limiting:** Anthropic API tem limites
5. **Parallel Testing:** Implementar depois (async)

---

## 📚 REFERENCE DOCS

### Supabase Schema
Ver: `CONTEXTO-AI-FACTORY-V3.md` (uploaded)

### Existing Workflows
Ver: `DIAGRAMA-FLUXOS.md` (uploaded)

### Architecture
Ver: Resumo no início deste documento

---

## 🚀 NEXT STEPS FOR CLAUDE CODE

1. **Read this entire HANDOFF.md**
2. **Run migrations** (copy SQL, execute)
3. **Start with `src/evaluator.py`** (highest priority)
4. **Test evaluation with mock data**
5. **Move to `src/report_generator.py`**
6. **Complete `src/test_runner.py`**
7. **End-to-end integration test**

---

## 💬 QUESTIONS? ASK MARCOS

- Slack: @marcos-daniels
- Email: marcos@mottivme.com
- Priority: Response within 4h during work hours

---

**Good luck! 🚀**  
**Build something amazing! 💪**
