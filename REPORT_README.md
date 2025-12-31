# Report Generator - Quick Start

## Geração de Relatórios HTML Profissionais

### 1. Gerar Relatório de Exemplo

```bash
# Na raiz do projeto
python generate_sample_report.py

# Abre automaticamente no navegador
open reports/report_*.html
```

### 2. Usar no Código

```python
from src.report_generator import ReportGenerator

# Configurar
generator = ReportGenerator(
    output_dir='./reports/'
)

# Gerar relatório
report_path = await generator.generate_html_report(
    agent={
        'id': 'uuid',
        'name': 'Nome do Agente',
        'version': 1,
        'description': 'Descrição'
    },
    evaluation={
        'overall_score': 8.5,
        'scores': {
            'completeness': 9.0,
            'tone': 8.5,
            'engagement': 8.0,
            'compliance': 9.0,
            'conversion': 7.5
        },
        'strengths': ['Ponto forte 1', 'Ponto forte 2'],
        'weaknesses': ['Ponto fraco 1'],
        'recommendations': ['Melhoria 1']
    },
    test_results=[
        {
            'name': 'Teste 1',
            'input': 'Input do lead',
            'agent_response': 'Resposta do agente',
            'score': 8.5,
            'passed': True,
            'feedback': 'Feedback detalhado'
        }
    ]
)

print(f"Relatório: {report_path}")
```

### 3. Ver Relatório Gerado

```bash
# Listar relatórios
ls -lh reports/

# Abrir último relatório
open $(ls -t reports/report_*.html | head -1)
```

---

## Features Visuais

- **Score Ring**: Círculo de progresso animado
- **5 Dimensões**: Completeness, Tone, Engagement, Compliance, Conversion
- **Test Cards**: Visual de cada caso de teste
- **Feedback Sections**: Strengths, Weaknesses, Recommendations
- **Responsive**: Funciona em mobile e desktop
- **Animações**: Fade in e barras de progresso animadas

---

## Estrutura dos Dados

### Agent
```python
{
    'id': 'string (uuid)',
    'name': 'string',
    'version': int,
    'description': 'string (opcional)'
}
```

### Evaluation
```python
{
    'overall_score': float (0-10),
    'scores': {
        'completeness': float,
        'tone': float,
        'engagement': float,
        'compliance': float,
        'conversion': float
    },
    'strengths': List[str],
    'weaknesses': List[str],
    'recommendations': List[str],
    'failures': List[str] (opcional),
    'warnings': List[str] (opcional)
}
```

### Test Results
```python
[
    {
        'name': 'string',
        'input': 'string',
        'agent_response': 'string',
        'score': float (0-10),
        'passed': bool,
        'feedback': 'string'
    }
]
```

---

## Troubleshooting

### Erro: Template Not Found
```bash
# Verificar se templates/report.html existe
ls templates/report.html

# Sistema usa fallback automático se não encontrar
```

### Relatório sem CSS
```bash
# Verificar conexão internet (Tailwind CSS via CDN)
# Ou abrir em navegador diferente
```

### Scores não aparecem
```python
# Garantir que evaluation tenha 'overall_score' e 'scores'
evaluation = {
    'overall_score': 8.5,  # Obrigatório
    'scores': {
        'completeness': 9.0,  # Todos obrigatórios
        'tone': 8.5,
        'engagement': 8.0,
        'compliance': 9.0,
        'conversion': 7.5
    }
}
```

---

## Documentação Completa

Ver: `REPORT_GENERATOR_GUIDE.md`

---

## Arquivos

- `src/report_generator.py` - Classe principal
- `templates/report.html` - Template Jinja2
- `generate_sample_report.py` - Script de exemplo
- `REPORT_GENERATOR_GUIDE.md` - Documentação detalhada
- `reports/` - Relatórios gerados

---

**Status:** Production Ready ✅
