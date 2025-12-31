# 🚀 REFLECTION LOOP - QUICK START

**Arquivo Principal:** `src/reflection_loop.py`
**Test File:** `test_reflection.py`
**Integração:** `test_runner.py` → `reflection_loop.py` → Supabase

---

## 📚 API Reference

### Class: `ReflectionLoop`

```python
from src.reflection_loop import ReflectionLoop
from src.supabase_requests import SupabaseRequestsClient

# Inicializar
supabase = SupabaseRequestsClient()
reflection = ReflectionLoop(supabase_client=supabase)
```

---

## ✅ Método Principal: `run_reflection()`

Executa o ciclo completo de auto-melhoria.

```python
result = await reflection.run_reflection(
    agent=original_agent,      # Dict do Supabase
    test_result=test_result,   # Dict com scores
    auto_test=False            # Testar v2? (default: False)
)
```

### Return Value:
```python
{
    'status': 'success',                    # 'success' | 'skipped' | 'failed'
    'original_agent_id': 'uuid',           # ID da v1
    'original_score': 7.2,                 # Score original
    'new_agent_id': 'uuid',                # ID da v2 (se criada)
    'new_version': 'v1.1-reflection',      # Nome da nova versão
    'changes_summary': [                   # Lista de mudanças
        'Adicionei qualificação BANT',
        'Reforçei perguntas abertas',
        ...
    ],
    'expected_improvements': {             # Deltas esperados
        'completeness': '+1.5 - Qualificação BANT',
        'tone': '+0.0 - Mantido',
        'engagement': '+0.5 - Perguntas abertas',
        'compliance': '+0.0 - Mantido',
        'conversion': '+1.0 - Técnicas de fechamento'
    },
    'risk_assessment': 'Baixo',            # 'Baixo' | 'Médio' | 'Alto'
    'new_agent_status': 'pending_approval',# Status da nova versão

    # Se auto_test=True:
    'new_score': 8.3,                      # Score da v2 (se testada)
    'improvement': 1.1,                    # Delta real
}
```

---

## 🔍 Outros Métodos

### 1. `should_reflect(test_result, min_score=6.0, max_score=8.0)`
Retorna `True` se deve fazer reflection.

```python
if await reflection.should_reflect(test_result):
    # Score está em [6.0, 8.0) - bom para reflection
    pass
```

### 2. `generate_improved_prompt(agent, test_result)`
Gera novo prompt usando Claude Opus.

```python
reflection_result = await reflection.generate_improved_prompt(
    agent=agent,
    test_result=test_result
)

print(reflection_result['improved_prompt'])  # Novo prompt
print(reflection_result['changes_summary'])  # Mudanças
```

### 3. `create_new_version(original_agent, improved_prompt, reflection_result, test_result)`
Cria nova versão no Supabase.

```python
new_agent = await reflection.create_new_version(
    original_agent=agent,
    improved_prompt=improved_prompt,
    reflection_result=reflection_result,
    test_result=test_result
)

print(new_agent['id'])        # UUID da nova versão
print(new_agent['version'])   # e.g., 'v1.1-reflection'
print(new_agent['status'])    # 'pending_approval'
```

---

## 🎯 Use Cases

### Case 1: Auto-Improve com Auto-Test
```python
from src.reflection_loop import ReflectionLoop
from src.test_runner import TestRunner

# 1. Testar agente
test_result = await test_runner.run_tests(agent_id)

# 2. Se score baixo, melhorar
if test_result['overall_score'] < 8.0:
    reflection = ReflectionLoop(supabase_client=supabase)
    agent = supabase.get_agent_version(agent_id)

    result = await reflection.run_reflection(
        agent=agent,
        test_result=test_result,
        auto_test=True  # ← Testa v2 automaticamente
    )

    if result['new_score'] >= 8.0:
        print(f"✅ Improved! {result['improvement']:+.1f}")
    else:
        print(f"⚠️ Partial improvement: {result['improvement']:+.1f}")
```

### Case 2: Manual Review Workflow
```python
# 1. Gerar melhoria SEM testar
result = await reflection.run_reflection(
    agent=agent,
    test_result=test_result,
    auto_test=False  # ← Admin aprova depois
)

# 2. Admin revisa no Dashboard
# 3. Dashboard aprova → status muda para 'active'
```

### Case 3: Quick Helper Function
```python
from src.reflection_loop import reflect_and_improve

result = await reflect_and_improve(
    agent_id='550e8400...',
    test_result=test_result_dict,
    auto_test=True
)
```

### Case 4: FastAPI Endpoint
```python
from fastapi import FastAPI
from src.reflection_loop import reflect_and_improve

app = FastAPI()

@app.post("/api/agent/{agent_id}/improve")
async def improve_agent(agent_id: str, auto_test: bool = False):
    agent = supabase.get_agent_version(agent_id)
    test_result = await test_runner.run_tests(agent_id)

    result = await reflect_and_improve(
        agent_id=agent_id,
        test_result=test_result,
        auto_test=auto_test
    )

    return result
```

---

## 📊 Test File Example

```bash
# Rodar teste completo
python test_reflection.py --agent-id 550e8400-e29b-41d4-a716-446655440000

# Com auto-test
python test_reflection.py --agent-id 550e8400... --auto-test
```

O script:
1. Carrega agente do Supabase
2. Executa 5 test cases
3. Avalia com Claude Opus
4. Se score < 8.0, executa reflection
5. Se auto_test, testa v2 também
6. Mostra results comparativos

---

## 🔑 Key Configuration

No `config.yaml`:
```yaml
reflection:
  enabled: true                  # Ativar/desativar reflection
  min_score_for_reflection: 6.0  # Score mínimo
  max_iterations: 3              # Max tentativas
  improvement_threshold: 0.5     # Melhoria esperada
```

---

## 📈 Monitoring

### Ver versões criadas por reflection:
```sql
SELECT
  id,
  version,
  status,
  validation_result->>'reflection_source' as source,
  validation_result->>'original_score' as orig_score,
  validation_result->>'risk_assessment' as risk
FROM agent_versions
WHERE validation_result->>'reflection_source' = 'auto_improvement'
ORDER BY created_at DESC;
```

### Check status de nova versão:
```python
new_agent = supabase.get_agent_version(new_agent_id)
print(f"Status: {new_agent['status']}")
print(f"Active: {new_agent['is_active']}")
```

---

## ⚠️ Common Issues

### 1. "Score < 6.0 - manual review needed"
- Agent com problemas estruturais
- Requer revisão humana
- Solução: Ajustar manualmente ou criar novo agent

### 2. "No improvement detected"
- Reflexão não melhorou score
- Possíveis causas:
  - Prompt já está bom
  - Fraco estrutural
  - Rubrica muito rigorosa

### 3. "Could not parse reflection response"
- JSON response do Claude malformado
- Fallback: usa response_text puro
- Log: verificar na cloud

### 4. "Supabase error when saving version"
- Validação de schema falhou
- Verifique campos obrigatórios
- Check service_role_key permissions

---

## 🔐 Best Practices

1. **Sempre use `auto_test=True` em produção**
   - Valida melhoria antes de salvar
   - Economiza aprovações manuais
   - Mais rápido no geral

2. **Review `risk_assessment` antes de aprovar**
   - Se "Alto", test intensivo
   - Se "Médio", review mudanças
   - Se "Baixo", approve rápido

3. **Monitor `changes_summary`**
   - Mudanças devem ser específicas
   - Genéricas = prompt ruim

4. **Track `improvement` metric**
   - Maioria deve ser >= 0.5
   - Se < 0.5 frequente, avaliar rubrica

5. **Versione tudo**
   - Nunca sobrescreva original
   - Histórico completo = rastreabilidade

---

## 📚 Architecture

```
input: test_result (score < 8.0)
           ↓
    should_reflect() check
           ↓
generate_improved_prompt()
  - Claude Opus analisa weaknesses
  - Gera novo prompt estruturado
           ↓
create_new_version()
  - Salva em Supabase
  - Status: pending_approval
           ↓
run_reflection() [complete cycle]
  - auto_test=True?
    - sim: testa v2, compara scores
    - não: cria e aguarda aprovação
           ↓
output: {status, new_agent_id, improvement, ...}
```

---

## 🎓 Learning Resources

- **Reflection Prompt**: lines 33-102 em `reflection_loop.py`
- **Full Cycle**: `run_reflection()` method (linhas 354-445)
- **Test Example**: `test_reflection.py` (269 linhas)
- **Integration**: veja `test_runner.py` linha ~237

---

## ✨ Next Steps

1. Deploy em staging
2. Run test_reflection.py com agent real
3. Monitor logs (20-30 runs)
4. Integrar endpoint FastAPI
5. Criar Dashboard widget para "Pending Approval"

---

*Quick Reference - AI Factory v4 - Reflection Loop*
