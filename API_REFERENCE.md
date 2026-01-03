# API Reference - AI Factory Testing Framework

Documentação completa da API REST e módulos Python.

---

## Sumário

1. [REST API Endpoints](#rest-api-endpoints)
2. [Módulos Python](#módulos-python)
3. [Schemas de Dados](#schemas-de-dados)
4. [Exemplos de Integração](#exemplos-de-integração)

---

## REST API Endpoints

Base URL: `http://localhost:8000` (desenvolvimento) ou URL do Railway em produção.

---

### Health Check

#### GET /health

Verifica status do servidor e conexão com banco de dados.

**Request:**
```bash
curl -X GET http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0.0",
  "database": "connected"
}
```

**Response (503 Service Unavailable):**
```json
{
  "detail": "Service unavailable"
}
```

---

#### GET /ping

Endpoint simples para load balancers e health probes.

**Request:**
```bash
curl -X GET http://localhost:8000/ping
```

**Response (200 OK):**
```json
{
  "message": "pong",
  "timestamp": "2024-01-15T10:30:00.123Z"
}
```

---

### Testing

#### POST /api/v1/test/run

Executa um único caso de teste contra um agente.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/test/run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "abc123-def456",
    "test_name": "Lead frio - primeira mensagem",
    "input_text": "Oi",
    "expected_behavior": "Cumprimento amigável + pergunta aberta sobre interesse",
    "rubric_focus": ["tone", "engagement"]
  }'
```

**Request Body Schema:**
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| agent_id | string | Sim | UUID do agent_version no Supabase |
| test_name | string | Sim | Nome descritivo do teste |
| input_text | string | Sim | Mensagem do lead/usuário |
| expected_behavior | string | Sim | Comportamento esperado do agente |
| rubric_focus | string[] | Não | Dimensões a focar: completeness, tone, engagement, compliance, conversion |

**Response (200 OK):**
```json
{
  "test_id": "test_1705312200",
  "agent_id": "abc123-def456",
  "test_name": "Lead frio - primeira mensagem",
  "status": "completed",
  "score": 8.5,
  "feedback": "Boa abertura com tom amigável. Pergunta aberta bem formulada...",
  "execution_time": 2.34,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Response (503 Service Unavailable):**
```json
{
  "detail": "Test runner not initialized"
}
```

---

#### POST /api/v1/test/batch

Enfileira múltiplos casos de teste para execução em background.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/test/batch \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "abc123-def456",
    "run_name": "Teste Completo SDR v1",
    "test_cases": [
      {
        "agent_id": "abc123-def456",
        "test_name": "Lead frio",
        "input_text": "Oi",
        "expected_behavior": "Cumprimento + pergunta",
        "rubric_focus": ["tone", "engagement"]
      },
      {
        "agent_id": "abc123-def456",
        "test_name": "Pergunta de preço",
        "input_text": "Quanto custa?",
        "expected_behavior": "Âncora valor + qualificação",
        "rubric_focus": ["compliance", "completeness"]
      }
    ]
  }'
```

**Request Body Schema:**
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| agent_id | string | Sim | UUID do agent_version |
| run_name | string | Não | Nome identificador do batch |
| test_cases | TestCaseInput[] | Sim | Lista de casos de teste |

**Response (200 OK):**
```json
{
  "run_id": "batch_1705312200123",
  "agent_id": "abc123-def456",
  "test_count": 2,
  "status": "queued",
  "status_endpoint": "/api/v1/test/status/batch_1705312200123",
  "timestamp": "2024-01-15T10:30:00.123Z"
}
```

---

#### GET /api/v1/test/status/{run_id}

Consulta status de um batch de testes.

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/test/status/batch_1705312200123
```

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| run_id | string | ID do batch retornado pelo POST /test/batch |

**Response (200 OK - Em Progresso):**
```json
{
  "run_id": "batch_1705312200123",
  "status": "processing",
  "completed": 1,
  "total": 2,
  "progress_percent": 50
}
```

**Response (200 OK - Completo):**
```json
{
  "run_id": "batch_1705312200123",
  "status": "completed",
  "overall_score": 8.2,
  "results": [
    {
      "test_name": "Lead frio",
      "score": 8.5,
      "passed": true
    },
    {
      "test_name": "Pergunta de preço",
      "score": 7.9,
      "passed": false
    }
  ],
  "report_url": "https://..."
}
```

---

### Agents

#### GET /api/v1/agents/{agent_id}/results

Busca histórico de resultados de testes de um agente.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/agents/abc123-def456/results?limit=10&offset=0"
```

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| agent_id | string | UUID do agent_version |

**Query Parameters:**
| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| limit | int | 10 | Resultados por página (max: 100) |
| offset | int | 0 | Resultados a pular |

**Response (200 OK):**
```json
{
  "agent_id": "abc123-def456",
  "count": 10,
  "results": [
    {
      "id": "result-uuid-1",
      "overall_score": 8.5,
      "test_details": {
        "scores": {
          "completeness": 9.0,
          "tone": 8.5,
          "engagement": 8.0,
          "compliance": 8.5,
          "conversion": 8.0
        },
        "strengths": ["Boa qualificação BANT"],
        "weaknesses": ["Tom às vezes agressivo"]
      },
      "report_url": "https://...",
      "created_at": "2024-01-15T10:30:00.000Z"
    }
  ]
}
```

---

### Metrics

#### GET /api/v1/metrics

Retorna métricas gerais do sistema.

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/metrics
```

**Response (200 OK):**
```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "metrics": {
    "total_agents": 15,
    "total_tests": 234,
    "avg_score": 7.8,
    "tests_today": 12,
    "approval_rate": 0.73
  }
}
```

---

## Módulos Python

### SupabaseClient

Cliente para interação com Supabase.

```python
from src import SupabaseClient

client = SupabaseClient(
    url="https://xxx.supabase.co",  # opcional, usa SUPABASE_URL
    key="eyJhb..."                   # opcional, usa SUPABASE_KEY
)
```

#### Métodos

##### get_agent_version(agent_id: str) -> Optional[Dict]

Busca agent_version pelo ID.

```python
agent = client.get_agent_version("uuid-aqui")
if agent:
    print(agent['name'])
    print(agent['system_prompt'])
```

##### get_agents_needing_testing(limit: int = 100) -> List[Dict]

Busca agentes pendentes de teste.

```python
pending = client.get_agents_needing_testing(limit=10)
for agent in pending:
    print(f"{agent['name']} - último teste: {agent['last_test_at']}")
```

##### update_agent_test_results(agent_id, score, report_url, test_result_id)

Atualiza agente com resultados do teste.

```python
client.update_agent_test_results(
    agent_id="uuid",
    score=8.5,
    report_url="https://...",
    test_result_id="test-uuid"
)
```

##### save_test_result(...) -> str

Salva resultado de teste e retorna ID.

```python
test_id = client.save_test_result(
    agent_version_id="uuid",
    overall_score=8.5,
    test_details={"scores": {...}},
    report_url="https://...",
    test_duration_ms=45000
)
```

##### get_skill(agent_version_id: str) -> Optional[Dict]

Busca skill mais recente do agente.

```python
skill = client.get_skill("uuid")
if skill:
    print(f"Version: {skill['version']}")
    print(skill['instructions'])
```

##### save_skill(...) -> str

Salva nova versão de skill.

```python
skill_id = client.save_skill(
    agent_version_id="uuid",
    instructions="Você é um SDR...",
    examples="Exemplo: ...",
    rubric="## Critérios..."
)
```

---

### Evaluator

Avaliador LLM-as-Judge usando Claude Opus.

```python
from src import Evaluator

evaluator = Evaluator(
    api_key="sk-ant-...",           # opcional, usa ANTHROPIC_API_KEY
    model="claude-opus-4-20250514", # modelo de avaliação
    temperature=0.3,                 # temperatura (0.0-1.0)
    max_tokens=4000                  # max tokens na resposta
)
```

#### Métodos

##### async evaluate(agent, skill, test_results) -> Dict

Avalia agente baseado nos resultados dos testes.

```python
result = await evaluator.evaluate(
    agent={"name": "SDR", "system_prompt": "..."},
    skill=None,  # ou dict com skill
    test_results=[
        {
            "name": "test1",
            "input": "Oi",
            "agent_response": "Olá! Como posso ajudar?",
            "expected_behavior": "Cumprimento amigável"
        }
    ]
)

print(result['overall_score'])  # 8.5
print(result['scores'])         # {completeness: 9.0, tone: 8.5, ...}
print(result['strengths'])      # ["Boa abertura", ...]
print(result['weaknesses'])     # ["Faltou qualificação", ...]
print(result['recommendations'])# ["Adicionar pergunta BANT", ...]
```

##### calculate_weighted_score(scores: Dict) -> float

Calcula score ponderado.

```python
score = evaluator.calculate_weighted_score({
    'completeness': 9.0,
    'tone': 8.5,
    'engagement': 8.0,
    'compliance': 9.0,
    'conversion': 7.5
})
# Retorna: 8.45 (média ponderada)
```

---

### TestRunner

Orquestrador de testes.

```python
from src import TestRunner, Evaluator, ReportGenerator, SupabaseClient

runner = TestRunner(
    supabase_client=SupabaseClient(),
    evaluator=Evaluator(),
    report_generator=ReportGenerator(),
    config={},                    # configurações extras
    anthropic_api_key="sk-..."   # para simulação de agentes
)
```

#### Métodos

##### async run_tests(agent_version_id, test_suite_path=None, test_cases=None) -> Dict

Executa suite completa de testes.

```python
result = await runner.run_tests(
    agent_version_id="uuid-do-agente",
    test_cases=[  # opcional, usa default SDR se não fornecido
        {"name": "test1", "input": "Oi", "expected_behavior": "..."}
    ]
)

print(result['overall_score'])   # 8.5
print(result['report_url'])      # URL do relatório HTML
print(result['duration_ms'])     # 45000 (tempo em ms)
print(result['test_details'])    # Detalhes completos
```

---

### ReportGenerator

Gerador de relatórios HTML.

```python
from src import ReportGenerator

reporter = ReportGenerator(
    output_dir="./reports",                    # diretório de saída
    templates_dir="./templates",               # templates Jinja2
    public_url_base="https://reports.xyz.com"  # URL base pública
)
```

#### Métodos

##### async generate_html_report(agent, evaluation, test_results) -> str

Gera relatório HTML e retorna URL/caminho.

```python
url = await reporter.generate_html_report(
    agent={"id": "uuid", "name": "SDR", "version": 1},
    evaluation={
        "overall_score": 8.5,
        "scores": {...},
        "strengths": [...],
        "weaknesses": [...]
    },
    test_results=[...]
)

print(url)  # ./reports/report_abc123_20240115_103000.html
            # ou https://reports.xyz.com/report_abc123_20240115_103000.html
```

---

### Funções Helper

#### run_quick_test

Executa teste rápido sem setup manual.

```python
from src import run_quick_test

result = await run_quick_test(
    agent_version_id="uuid",
    supabase_url="https://...",      # opcional
    supabase_key="eyJ...",           # opcional
    anthropic_key="sk-ant-...",      # opcional
    output_dir="./reports",          # opcional
    test_cases=[...]                 # opcional
)
```

#### evaluate_sync

Avaliação síncrona simplificada.

```python
from src.evaluator import evaluate_sync

result = evaluate_sync(
    agent={"name": "SDR", "system_prompt": "..."},
    skill=None,
    test_results=[...],
    api_key="sk-ant-..."
)
```

#### generate_report

Gera relatório de forma simplificada.

```python
from src.report_generator import generate_report

url = await generate_report(
    agent={...},
    evaluation={...},
    test_results=[...],
    output_dir="./reports"
)
```

---

## Schemas de Dados

### TestCaseInput

```json
{
  "agent_id": "string (UUID)",
  "test_name": "string",
  "input_text": "string",
  "expected_behavior": "string",
  "rubric_focus": ["string"]
}
```

### TestResult

```json
{
  "test_id": "string",
  "agent_id": "string (UUID)",
  "test_name": "string",
  "status": "string (completed|failed|error)",
  "score": "float (0-10)",
  "feedback": "string",
  "execution_time": "float (seconds)",
  "timestamp": "string (ISO 8601)"
}
```

### EvaluationResult

```json
{
  "overall_score": "float (0-10)",
  "scores": {
    "completeness": "float",
    "tone": "float",
    "engagement": "float",
    "compliance": "float",
    "conversion": "float"
  },
  "test_case_evaluations": [
    {
      "test_name": "string",
      "score": "float",
      "passed": "boolean",
      "feedback": "string"
    }
  ],
  "strengths": ["string"],
  "weaknesses": ["string"],
  "failures": ["string"],
  "warnings": ["string"],
  "recommendations": ["string"]
}
```

### AgentVersion (Supabase)

```json
{
  "id": "UUID",
  "name": "string",
  "version": "int",
  "system_prompt": "string",
  "agent_config": "JSONB",
  "last_test_score": "float (0-10)",
  "last_test_at": "timestamp",
  "framework_approved": "boolean",
  "test_report_url": "string",
  "status": "string (active|needs_improvement|draft)"
}
```

### Skill (Supabase)

```json
{
  "id": "UUID",
  "agent_version_id": "UUID",
  "version": "int",
  "instructions": "string",
  "examples": "string",
  "rubric": "string",
  "test_cases": "JSONB",
  "local_file_path": "string",
  "last_synced_at": "timestamp"
}
```

---

## Exemplos de Integração

### Integração com n8n

Webhook para testar agente após criação:

```javascript
// n8n Code Node
const agentId = $node["CreateAgent"].json.id;

const response = await $http.request({
  method: 'POST',
  url: 'https://api.aifactory.com/api/v1/test/batch',
  body: {
    agent_id: agentId,
    run_name: `Auto-test ${new Date().toISOString()}`
  },
  json: true
});

return {
  run_id: response.run_id,
  status_url: response.status_endpoint
};
```

### Polling de Status

```python
import asyncio
import httpx

async def wait_for_completion(run_id: str, max_wait: int = 300):
    """Aguarda conclusão de batch com polling."""
    start = asyncio.get_event_loop().time()

    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(
                f"http://localhost:8000/api/v1/test/status/{run_id}"
            )
            data = response.json()

            if data['status'] == 'completed':
                return data

            if data['status'] == 'failed':
                raise Exception(f"Batch failed: {data.get('error')}")

            elapsed = asyncio.get_event_loop().time() - start
            if elapsed > max_wait:
                raise TimeoutError(f"Batch {run_id} timeout after {max_wait}s")

            await asyncio.sleep(5)  # Poll a cada 5 segundos

# Uso
result = await wait_for_completion("batch_123456789")
print(f"Score final: {result['overall_score']}")
```

### Webhook de Notificação

Configure webhook para ser chamado quando teste completar:

```python
# Em config.yaml
notifications:
  webhook_url: "https://hooks.slack.com/services/xxx"
  notify_on: ["completed", "failed"]
  notify_if_score_below: 8.0
```

---

## Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 400 | Bad Request - dados inválidos |
| 404 | Not Found - recurso não encontrado |
| 500 | Internal Server Error |
| 503 | Service Unavailable - componente não inicializado |

---

## Rate Limits

- Teste individual: 10 req/min
- Batch: 5 req/min
- Status polling: 60 req/min
- Resultados: 30 req/min

---

## Changelog

### v1.0.0 (2024-01)
- API REST inicial
- Endpoints de teste (run, batch, status)
- Endpoints de agentes (results)
- Endpoints de métricas
- Módulos Python completos

---

**Documentação gerada para AI Factory Testing Framework v1.0.0**
