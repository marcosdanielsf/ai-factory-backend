# AI Factory V4 - Test Runner Complete Guide

## Overview

O `src/test_runner.py` é o componente central do AI Factory V4 Testing Framework. Ele:

1. **Carrega agentes** do Supabase (ou mock data)
2. **Executa test cases** simulando conversas com o agente via Claude
3. **Avalia resultados** usando Claude Opus como juiz (LLM-as-Judge)
4. **Gera relatórios** HTML com scores e recomendações
5. **Salva resultados** no banco de dados

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       TestRunner                             │
│                  (src/test_runner.py)                        │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
   ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐
   │  Supabase   │  │  Evaluator   │  │ ReportGenerator  │
   │  Client     │  │   (Opus)     │  │  (Jinja2/HTML)   │
   └─────────────┘  └──────────────┘  └──────────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Agent Response │
                    │ Simulator(Claude)
                    └────────────────┘
```

## Core Components

### 1. **TestRunner** (`src/test_runner.py`)

A classe principal que orquestra todo o processo de teste.

```python
runner = TestRunner(
    supabase_client=supabase,
    evaluator=evaluator,
    report_generator=reporter,
    anthropic_api_key=api_key
)

result = await runner.run_tests(
    agent_version_id="uuid-here",
    test_cases=[...]  # Optional
)
```

**Métodos principais:**

```python
async def run_tests(
    agent_version_id: str,
    test_suite_path: str = None,
    test_cases: List[Dict] = None
) -> Dict:
    """
    Executa suite completa de testes.

    Returns:
    {
        'overall_score': 8.5,
        'test_details': {...},
        'report_url': 'https://...',
        'duration_ms': 45000
    }
    """
```

### 2. **Evaluator** (`src/evaluator.py`)

Avalia agentes usando Claude Opus como juiz.

```python
evaluator = Evaluator(api_key=api_key)

evaluation = await evaluator.evaluate(
    agent=agent_data,
    skill=skill_data,
    test_results=test_results
)
```

**Rubrica de 5 dimensões:**
- **Completeness** (25%): Qualificação BANT completa
- **Tone** (20%): Tom consultivo e profissional
- **Engagement** (20%): Lead engajado
- **Compliance** (20%): Seguiu instruções/guardrails
- **Conversion** (15%): Conseguiu agendar/converter

### 3. **ReportGenerator** (`src/report_generator.py`)

Gera relatórios HTML bonitos usando Jinja2.

```python
reporter = ReportGenerator(output_dir='./reports')

report_url = await reporter.generate_html_report(
    agent=agent_data,
    evaluation=evaluation,
    test_results=test_results
)
```

## Usage Examples

### Exemplo 1: Teste Rápido Offline

```python
import asyncio
from src.test_runner import run_quick_test

async def main():
    result = await run_quick_test(
        agent_version_id="mock-isabella-001",
        test_cases=[
            {
                'name': 'Lead frio',
                'input': 'Oi',
                'expected_behavior': 'Cumprimento + pergunta aberta'
            }
        ]
    )
    print(f"Score: {result['overall_score']}")

asyncio.run(main())
```

### Exemplo 2: Teste Completo com Supabase

```python
import asyncio
import os
from src.supabase_client import SupabaseClient
from src.evaluator import Evaluator
from src.report_generator import ReportGenerator
from src.test_runner import TestRunner

async def main():
    # Componentes
    supabase = SupabaseClient(
        url=os.getenv('SUPABASE_URL'),
        key=os.getenv('SUPABASE_KEY')
    )

    evaluator = Evaluator(api_key=os.getenv('ANTHROPIC_API_KEY'))
    reporter = ReportGenerator(output_dir='./reports')

    runner = TestRunner(
        supabase_client=supabase,
        evaluator=evaluator,
        report_generator=reporter
    )

    # Executar testes
    result = await runner.run_tests(
        agent_version_id="550e8400-e29b-41d4-a716-446655440000"
    )

    print(f"Overall Score: {result['overall_score']}")
    print(f"Report: {result['report_url']}")

asyncio.run(main())
```

### Exemplo 3: Teste com Test Cases Customizados

```python
test_cases = [
    {
        'name': 'Lead frio - primeira mensagem',
        'input': 'Oi',
        'expected_behavior': 'Cumprimento amigavel + pergunta aberta',
        'rubric_focus': ['tone', 'engagement'],
        'category': 'cold_lead'
    },
    {
        'name': 'Lead pergunta preco',
        'input': 'Quanto custa?',
        'expected_behavior': 'Ancora valor antes de preco',
        'rubric_focus': ['compliance', 'completeness'],
        'category': 'price_objection'
    },
    # ... mais casos
]

result = await runner.run_tests(
    agent_version_id="uuid-here",
    test_cases=test_cases
)
```

### Exemplo 4: Teste com Skill Customizada

```python
# Carregar skill do Supabase
skill = supabase.get_skill(agent_version_id)

# Ou usar skill mock
skill = {
    'instructions': 'Você é Isabella...',
    'examples': '## Exemplo 1\n...',
    'rubric': '## Rubrica Customizada\n...',
    'test_cases': [...]
}

result = await runner.run_tests(agent_version_id, test_cases=skill['test_cases'])
```

## Test Cases Structure

Cada test case deve ter:

```python
{
    'name': 'Nome descritivo do teste',
    'input': 'Mensagem do lead',
    'expected_behavior': 'Comportamento esperado do agente',
    'rubric_focus': ['tone', 'engagement'],  # Dimensões a avaliar
    'category': 'cold_lead'  # Categoria: cold_lead, objection, qualification, etc
}
```

**Categorias disponíveis:**
- `cold_lead` - Lead frio, primeira mensagem
- `price_objection` - Lead pergunta sobre preço
- `qualification` - Lead qualificando (BANT)
- `objection` - Lead com objeção
- `hot_lead` - Lead quente, pronto para agendar
- `guardrail_test` - Testa se agente segue instruções
- `technical` - Perguntas técnicas
- `competition` - Lead comparando concorrentes
- `material_request` - Solicita material/documentação
- `disqualification` - Lead não qualificado

## Default Test Cases

O TestRunner vem com 10 test cases padrão para agentes SDR (`DEFAULT_SDR_TEST_CASES`):

```python
from src.test_runner import DEFAULT_SDR_TEST_CASES

# Usar padrão
result = await runner.run_tests(agent_version_id)
# Ou customizar
custom_cases = DEFAULT_SDR_TEST_CASES[:5]  # Usar apenas primeiros 5
result = await runner.run_tests(agent_version_id, test_cases=custom_cases)
```

## How It Works - Step by Step

### 1. Load Agent & Skill
```python
agent = supabase.get_agent_version(agent_version_id)
skill = supabase.get_skill(agent_version_id)  # Opcional
```

### 2. Load Test Cases
Prioridade:
1. `test_cases` parameter (se fornecido)
2. `skill.test_cases` (se skill tiver)
3. `DEFAULT_SDR_TEST_CASES` (padrão)

### 3. Run Tests
Para cada test case:
- Pega o input (mensagem do lead)
- Simula resposta do agente via Claude
- Armazena resultado

```python
for test_case in test_cases:
    result = await runner._run_single_test(agent, skill, test_case)
```

### 4. Evaluate Results
Claude Opus avalia todos os resultados usando a rubrica:

```python
evaluation = await evaluator.evaluate(
    agent=agent,
    skill=skill,
    test_results=results
)
```

Retorna:
```python
{
    'overall_score': 8.5,  # Score ponderado
    'scores': {
        'completeness': 9.0,
        'tone': 8.5,
        'engagement': 8.0,
        'compliance': 9.0,
        'conversion': 7.5
    },
    'strengths': [...],
    'weaknesses': [...],
    'failures': [...],
    'warnings': [...],
    'recommendations': [...]
}
```

### 5. Generate Report
Cria HTML com Jinja2 template:

```python
report_url = await reporter.generate_html_report(
    agent=agent,
    evaluation=evaluation,
    test_results=results
)
```

### 6. Save to Supabase
Opcionalmente salva resultados no banco:

```python
test_result_id = supabase.save_test_result(...)
supabase.update_agent_test_results(...)
```

## Running Tests

### CLI Commands

```bash
# Setup
export ANTHROPIC_API_KEY='sk-ant-...'
export SUPABASE_URL='https://xxx.supabase.co'
export SUPABASE_KEY='eyJ...'

# Teste offline (sem Supabase)
python test_offline.py

# Teste completo
python test_runner_comprehensive.py

# Teste rápido
python run_test_simple.py
```

### Programmatically

```python
import asyncio
from dotenv import load_dotenv
from src.test_runner import run_quick_test

load_dotenv()

async def main():
    result = await run_quick_test(
        agent_version_id="550e8400-e29b-41d4-a716-446655440000"
    )
    print(result)

asyncio.run(main())
```

### Via API (FastAPI)

```python
# server.py
from fastapi import FastAPI
from src.test_runner import TestRunner

app = FastAPI()

@app.post("/api/test-agent")
async def test_agent(agent_version_id: str):
    result = await runner.run_tests(agent_version_id)
    return result

# curl -X POST http://localhost:8000/api/test-agent?agent_version_id=uuid
```

## Environment Variables

```bash
# Obrigatórios
ANTHROPIC_API_KEY=sk-ant-...

# Supabase (se usar banco)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...

# Opcionais
REPORTS_OUTPUT_DIR=./reports
LOG_LEVEL=INFO
```

## Approving/Rejecting Agents

### Auto Approval
Agentes com score >= 8.0 são automaticamente aprovados:

```python
if evaluation['overall_score'] >= 8.0:
    supabase.update_agent_version(
        agent_id,
        status='active',
        approved=True
    )
```

### Manual Review
Scores 6.0-8.0 precisam de revisão manual.

```python
if 6.0 <= evaluation['overall_score'] < 8.0:
    status = 'pending_review'  # Esperar revisão
```

### Rejection
Scores < 6.0 são rejeitados.

```python
if evaluation['overall_score'] < 6.0:
    status = 'failed'
    # Triggerar improvement loop
```

## Troubleshooting

### ❌ "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
# Ou configure no .env
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

### ❌ "Could not simulate agent response"
- Verificar API key
- Verificar prompt do agente está correto
- Tentar aumentar max_tokens

### ❌ "Template not found"
- Verificar se existe `/templates/report.html`
- Usar fallback HTML (automático)

### ❌ "Supabase connection failed"
- Verificar SUPABASE_URL e SUPABASE_KEY
- Tentar teste offline primeiro

### ❌ "Could not parse evaluation response"
- Claude retornou JSON inválido
- Usar fallback evaluation
- Aumentar temperature (mais criativo) ou diminuir (mais determinístico)

## Performance Tuning

### Aumentar velocidade
```python
# Usar modelo mais rápido
evaluator = Evaluator(model="claude-sonnet-4-20250514")

# Reduzir número de test cases
test_cases = DEFAULT_SDR_TEST_CASES[:5]

# Executar em paralelo (future)
# await asyncio.gather(*[test1, test2, test3])
```

### Melhorar qualidade
```python
# Usar Claude Opus
evaluator = Evaluator(model="claude-opus-4-20250514")

# Aumentar temperatura
evaluator = Evaluator(temperature=0.5)

# Mais tokens para resposta
evaluator = Evaluator(max_tokens=8000)
```

## Advanced: Custom Rubric

```python
skill = {
    'rubric': """
## Custom Rubric for E-Commerce Agents

### Product Knowledge (30%)
- 10: Explains all features, benefits, use cases
- 5: Some features mentioned
- 0: No product knowledge

### Closing Technique (20%)
- 10: Hard close, customer agrees
- 5: Soft close, next step discussed
- 0: No close attempt
"""
}

evaluation = await evaluator.evaluate(
    agent=agent,
    skill=skill,
    test_results=results
)
```

## Next Steps

After testing an agent:

1. **Score >= 8.0**: Agent approved, deploy to production
2. **Score 6.0-8.0**: Review weaknesses, improve prompt
3. **Score < 6.0**: Use reflection loop to auto-improve

```python
from src.reflection_loop import improve_agent

if score < 8.0:
    new_agent_id = await improve_agent(agent_id, evaluation)
```

## Files Reference

- `src/test_runner.py` - Main orchestrator
- `src/evaluator.py` - LLM-as-Judge (Claude Opus)
- `src/report_generator.py` - HTML report generation
- `src/supabase_client.py` - Database interactions
- `test_offline.py` - Offline test example
- `test_runner_comprehensive.py` - Complete demo
- `templates/report.html` - HTML template for reports

## More Info

See also:
- `HANDOFF.md` - Project architecture
- `requirements.txt` - Python dependencies
- `.env.example` - Environment setup
