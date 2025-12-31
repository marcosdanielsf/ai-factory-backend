# Report Generator - START HERE

## Bem-vindo ao Report Generator!

Este é o **ponto de partida** para usar o sistema de geração de relatórios HTML do AI Factory Testing Framework.

---

## Quick Start (3 passos)

### 1. Gerar Relatório de Exemplo
```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework
python generate_sample_report.py
```

**Resultado:** Relatório HTML profissional será gerado e você verá onde foi salvo.

---

### 2. Abrir Relatório no Navegador
```bash
# Abre o último relatório gerado
open $(ls -t reports/report_*.html | head -1)
```

**Você verá:**
- Score ring animado (círculo de progresso)
- 5 dimensões de avaliação visual
- Cards de teste com status (PASSED/FAILED)
- Strengths, Weaknesses, Recommendations
- Design profissional e responsivo

---

### 3. Ver Código do Exemplo
```bash
# Ver como foi gerado
cat generate_sample_report.py
```

---

## Exemplos Disponíveis

### Exemplo 1: Básico
```bash
python generate_sample_report.py
```
- Demonstra Isabella SDR Expert
- Score: 8.8/10 - APPROVED
- 5 casos de teste

### Exemplo 2: Fluxo Completo
```bash
python example_full_flow.py
```
- Demonstra Test → Evaluate → Report
- Simula Luna Customer Success
- Score: 8.3/10 - APPROVED

### Exemplo 3: Com NLP
```bash
python nlp_integration_example.py
```
- Análise NLP avançada
- Sentiment, fluency, coherence, empathy
- Score: 9.0/10 - APPROVED

---

## Usar no Seu Código

### Código Mínimo
```python
from src.report_generator import ReportGenerator

generator = ReportGenerator()

report_path = await generator.generate_html_report(
    agent={'id': 'xxx', 'name': 'Agent Name', 'version': 1},
    evaluation={'overall_score': 8.5, 'scores': {...}, ...},
    test_results=[{...}]
)

print(f"Relatório: {report_path}")
```

### Ver Exemplo Completo
```bash
cat generate_sample_report.py
```

---

## Estrutura de Dados

### Agent (mínimo)
```python
{
    'id': 'string',
    'name': 'string',
    'version': int
}
```

### Evaluation (mínimo)
```python
{
    'overall_score': float,
    'scores': {
        'dimension1': float,
        'dimension2': float,
        # ... até 5 dimensões
    }
}
```

### Test Results (mínimo)
```python
[
    {
        'name': 'Test name',
        'input': 'Lead input',
        'agent_response': 'Agent response',
        'score': float,
        'passed': bool
    }
]
```

---

## Documentação

### Para Começar
- **Este arquivo:** START_HERE.md
- **Quick Start:** REPORT_README.md (comandos rápidos)

### Para Aprofundar
- **Guia Completo:** REPORT_GENERATOR_GUIDE.md (tudo sobre o sistema)
- **Sumário:** REPORT_GENERATOR_SUMMARY.md (visão executiva)
- **Índice:** REPORT_GENERATOR_INDEX.md (navegação)

---

## Arquivos Principais

```
src/report_generator.py      # Classe principal
templates/report.html         # Template HTML
reports/                      # Relatórios gerados aqui

generate_sample_report.py    # Exemplo 1: Básico
example_full_flow.py         # Exemplo 2: Fluxo completo
nlp_integration_example.py   # Exemplo 3: Com NLP
```

---

## Comandos Úteis

### Gerar Relatórios
```bash
python generate_sample_report.py      # Básico
python example_full_flow.py           # Fluxo completo
python nlp_integration_example.py     # Com NLP
```

### Ver Relatórios
```bash
ls -lh reports/                       # Listar
open $(ls -t reports/*.html | head -1) # Abrir último
```

### Ajuda
```bash
cat REPORT_README.md                  # Quick start
cat REPORT_GENERATOR_GUIDE.md        # Guia completo
cat REPORT_GENERATOR_INDEX.md        # Índice
```

---

## Próximos Passos

1. **Execute o exemplo básico**
   ```bash
   python generate_sample_report.py
   ```

2. **Abra o relatório gerado**
   ```bash
   open reports/report_*.html
   ```

3. **Veja o código do exemplo**
   ```bash
   cat generate_sample_report.py
   ```

4. **Leia o quick start**
   ```bash
   cat REPORT_README.md
   ```

5. **Adapte para seu caso**
   - Copie `generate_sample_report.py`
   - Substitua os dados por seus dados reais
   - Execute e veja o resultado!

---

## Troubleshooting Rápido

### Relatório não gera
```bash
# Verificar se template existe
ls templates/report.html

# Se não existir, o sistema usa fallback automático
```

### CSS não carrega
```bash
# Abrir em navegador diferente
# Ou verificar conexão internet (Tailwind CSS via CDN)
```

### Erro de import
```bash
# Verificar se está no diretório correto
pwd
# Deve ser: /Users/marcosdaniels/Downloads/ai-factory-testing-framework
```

---

## Ajuda

**Dúvidas?**
- Ver: `REPORT_GENERATOR_GUIDE.md` (seção Troubleshooting)
- Ver: `HANDOFF.md` (contexto do framework)

**Quer customizar?**
- Ver: `REPORT_GENERATOR_GUIDE.md` (seção Personalização)
- Editar: `templates/report.html`

---

## Status do Projeto

Status: PRODUCTION READY ✅

- Código: 100% funcional
- Templates: Profissionais e responsivos
- Documentação: Completa
- Exemplos: 3 funcionais
- Relatórios: 3 demonstrativos

---

**Projeto:** AI Factory Testing Framework v1.0
**Desenvolvido por:** Marcos Daniels / MOTTIVME
**Data:** 31/12/2025

---

**COMECE AGORA:**
```bash
python generate_sample_report.py
```
