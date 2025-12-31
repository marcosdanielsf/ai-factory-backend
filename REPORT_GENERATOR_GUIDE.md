# AI Factory - Report Generator Guide

## Visão Geral

O **Report Generator** é o módulo responsável por transformar resultados de testes de agentes em relatórios HTML profissionais e visualmente atraentes.

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    REPORT GENERATOR                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input:                                                      │
│  ├─ Agent Data (nome, versão, descrição)                   │
│  ├─ Evaluation Results (scores, feedback)                   │
│  └─ Test Results (casos de teste executados)               │
│                                                              │
│  Processing:                                                 │
│  ├─ Template Jinja2 (templates/report.html)                │
│  ├─ Context Preparation (_prepare_context)                  │
│  ├─ Custom Filters (format_score, score_class)             │
│  └─ HTML Rendering                                          │
│                                                              │
│  Output:                                                     │
│  └─ Beautiful HTML Report (reports/report_{id}_{ts}.html)   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Componentes

### 1. ReportGenerator Class

**Localização:** `/Users/marcosdaniels/Downloads/ai-factory-testing-framework/src/report_generator.py`

**Responsabilidades:**
- Renderizar templates Jinja2
- Preparar contexto de dados
- Aplicar filtros customizados
- Salvar relatórios HTML
- Gerar URLs ou paths de acesso

**Métodos Principais:**

```python
# Método principal - gera relatório completo
async def generate_html_report(
    agent: Dict,
    evaluation: Dict,
    test_results: List[Dict]
) -> str:
    """
    Gera relatório HTML completo.

    Returns:
        URL ou caminho do relatório gerado
    """

# Prepara dados para o template
def _prepare_context(
    agent: Dict,
    evaluation: Dict,
    test_results: List[Dict]
) -> Dict:
    """
    Prepara contexto completo para renderização.

    Returns:
        Dict com todos os dados formatados
    """

# Fallback caso template não esteja disponível
def _generate_fallback_html(context: Dict) -> str:
    """
    Gera HTML inline como backup.
    """
```

### 2. Template HTML

**Localização:** `/Users/marcosdaniels/Downloads/ai-factory-testing-framework/templates/report.html`

**Features do Template:**

#### 📊 Design Visual
- **Tailwind CSS** via CDN
- **Google Fonts** (Inter) para tipografia profissional
- **Gradientes** e **sombras** suaves
- **Animações CSS** (fadeIn, score bars)
- **Responsivo** (mobile-first design)

#### 🎨 Componentes

##### Header Section
```html
- Logo do agente (ícone gradiente)
- Nome e versão
- Overall Score (círculo animado)
- Status Badge (APPROVED/NEEDS IMPROVEMENT)
```

##### Score Breakdown Section
```html
- 5 dimensões de avaliação:
  1. Completeness (25%)
  2. Tone (20%)
  3. Engagement (20%)
  4. Compliance (20%)
  5. Conversion (15%)
- Barras de progresso animadas
- Cores baseadas em score (verde ≥8, amarelo ≥6, vermelho <6)
```

##### Test Results Section
```html
- Cards de estatísticas (Total, Passed, Failed, Pass Rate)
- Lista de casos de teste com:
  - Input do lead
  - Resposta do agente
  - Score individual
  - Feedback do avaliador
  - Status visual (PASSED/FAILED)
```

##### Feedback Section
```html
- Grid 2 colunas:
  - Strengths (pontos fortes)
  - Weaknesses (pontos fracos)
- Ícones SVG inline
- Background colorido por categoria
```

##### Issues & Recommendations Section
```html
- Failures (erros críticos) - vermelho
- Warnings (alertas) - amarelo
- Recommendations (melhorias) - azul
```

##### Footer
```html
- Framework version
- Evaluator model (Claude Opus)
- Timestamp de geração
```

#### 🎭 Filtros Jinja2 Customizados

```python
# Formatar score com 1 casa decimal
{{ score | format_score }}  # 8.5

# Classe CSS baseada em score
{{ score | score_class }}   # "text-green-600"

# Formatar datetime
{{ datetime | format_datetime }}  # "2025-12-31 09:45:11"

# Truncar texto
{{ text | truncate_text(200) }}   # "Texto longe..."
```

---

## Uso

### Exemplo Básico

```python
from src.report_generator import ReportGenerator

# Dados do agente
agent = {
    'id': 'uuid-do-agente',
    'name': 'Isabella SDR',
    'version': 2,
    'description': 'Agente especializado em vendas B2B'
}

# Resultados de avaliação
evaluation = {
    'overall_score': 8.5,
    'scores': {
        'completeness': 9.0,
        'tone': 8.5,
        'engagement': 8.0,
        'compliance': 9.0,
        'conversion': 7.5
    },
    'strengths': ['Excelente tom consultivo', 'BANT completo'],
    'weaknesses': ['Poderia personalizar mais'],
    'recommendations': ['Adicionar casos de sucesso']
}

# Resultados dos testes
test_results = [
    {
        'name': 'Teste 1',
        'input': 'Pergunta do lead',
        'agent_response': 'Resposta do agente',
        'score': 8.5,
        'passed': True,
        'feedback': 'Ótima abordagem'
    }
]

# Gerar relatório
generator = ReportGenerator(
    output_dir='./reports/'
)

report_path = await generator.generate_html_report(
    agent=agent,
    evaluation=evaluation,
    test_results=test_results
)

print(f"Relatório gerado: {report_path}")
```

### Exemplo com Helper Function

```python
from src.report_generator import generate_report

# Mais simples - usa defaults
report_path = await generate_report(
    agent=agent,
    evaluation=evaluation,
    test_results=test_results,
    output_dir='./reports/'
)
```

### Gerar Relatório de Exemplo

```bash
# Usar script de demonstração
python generate_sample_report.py

# Saída:
# ✅ Relatório gerado com sucesso!
# 📍 Localização: ./reports/report_a1b2c3d4_20251231_094511.html
```

---

## Estrutura de Dados

### Agent Dictionary

```python
{
    'id': 'uuid',               # Obrigatório
    'name': 'string',           # Obrigatório
    'version': int,             # Obrigatório
    'description': 'string',    # Opcional
    'system_prompt': 'string'   # Opcional (não renderizado no report)
}
```

### Evaluation Dictionary

```python
{
    'overall_score': float,     # 0-10
    'scores': {
        'completeness': float,  # 0-10
        'tone': float,
        'engagement': float,
        'compliance': float,
        'conversion': float
    },
    'test_case_evaluations': [
        {
            'test_name': 'string',
            'score': float,
            'passed': bool,
            'feedback': 'string'
        }
    ],
    'strengths': ['string'],
    'weaknesses': ['string'],
    'failures': ['string'],      # Erros críticos
    'warnings': ['string'],       # Alertas
    'recommendations': ['string']
}
```

### Test Result Dictionary

```python
{
    'name': 'string',            # Nome do caso de teste
    'input': 'string',           # Input do lead
    'agent_response': 'string',  # Resposta do agente
    'expected_behavior': 'string', # Comportamento esperado
    'score': float,              # 0-10
    'passed': bool,              # True/False
    'feedback': 'string'         # Feedback do avaliador
}
```

---

## Configuração

### Variáveis de Ambiente

```bash
# Diretório de saída (opcional)
export REPORTS_OUTPUT_DIR="/path/to/reports"

# URL base pública (opcional - para links)
export REPORTS_PUBLIC_URL="https://reports.aifactory.com"
```

### Customização

#### Mudar Template

```python
generator = ReportGenerator(
    templates_dir='/custom/templates/path/'
)
```

#### Mudar Output Dir

```python
generator = ReportGenerator(
    output_dir='/custom/reports/path/'
)
```

#### Adicionar URL Pública

```python
generator = ReportGenerator(
    public_url_base='https://reports.domain.com'
)

# Retorna: https://reports.domain.com/report_xxx_timestamp.html
```

---

## Features Avançadas

### 1. Fallback HTML

Se o template Jinja2 não estiver disponível, o sistema gera HTML inline automaticamente usando o método `_generate_fallback_html()`.

```python
# Template não encontrado -> usa fallback
html_content = self._generate_fallback_html(context)
```

### 2. Animações CSS

```css
/* Barras de score animam ao carregar */
.score-bar {
    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Fade in sequencial das seções */
.animate-fade-in {
    animation: fadeIn 0.5s ease-out forwards;
}
```

### 3. Score Ring (Círculo de Progresso)

```css
.score-ring {
    --progress: 85; /* 0-100 */
    background: conic-gradient(
        var(--ring-color) calc(var(--progress) * 3.6deg),
        #e5e7eb calc(var(--progress) * 3.6deg)
    );
}
```

### 4. Responsive Design

```html
<!-- Grid adapta para mobile -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <!-- Conteúdo -->
</div>

<!-- Flexbox adapta direção -->
<div class="flex flex-col md:flex-row">
    <!-- Conteúdo -->
</div>
```

---

## Cores e Temas

### Score Colors

```python
# Verde: Score ≥ 8.0
'text-green-600', 'bg-green-100', 'border-green-200'

# Amarelo: Score ≥ 6.0
'text-yellow-600', 'bg-yellow-100', 'border-yellow-200'

# Vermelho: Score < 6.0
'text-red-600', 'bg-red-100', 'border-red-200'
```

### Gradientes

```css
/* Header icon */
background: linear-gradient(135deg, #4f46e5, #7c3aed);

/* Score bars */
background: linear-gradient(90deg, #34d399, #10b981);
```

---

## Testing

### Testar com Dados Mock

```python
# Usar generate_sample_report.py
python generate_sample_report.py

# Verifica:
# ✓ Template rendering
# ✓ Score calculations
# ✓ CSS animations
# ✓ Responsive layout
# ✓ Data formatting
```

### Testar Fallback

```python
# Renomear template temporariamente
mv templates/report.html templates/report.html.bak

# Gerar relatório (usa fallback)
python generate_sample_report.py

# Restaurar
mv templates/report.html.bak templates/report.html
```

---

## Performance

### Otimizações Implementadas

1. **CDN Assets**: Tailwind CSS e Google Fonts via CDN
2. **Lazy Loading**: JavaScript no final do body
3. **CSS Animations**: GPU-accelerated (transform, opacity)
4. **HTML Minification**: Remover espaços desnecessários (futuro)
5. **Image Optimization**: SVG inline (leve)

### Tamanho Médio do Relatório

- **HTML**: ~40-45 KB
- **Load Time**: < 1s (com CDN)
- **Render Time**: < 100ms

---

## Roadmap / Melhorias Futuras

### Curto Prazo
- [ ] Exportar para PDF (weasyprint ou puppeteer)
- [ ] Gráficos interativos (Chart.js)
- [ ] Dark mode toggle
- [ ] Comparação entre versões (v1 vs v2)

### Médio Prazo
- [ ] Multi-idioma (i18n)
- [ ] Temas customizáveis por empresa
- [ ] Embedding de vídeos (avatar responses)
- [ ] Sharing links (gerar URL curta)

### Longo Prazo
- [ ] Dashboard de relatórios (lista, filtros)
- [ ] Analytics de relatórios (views, shares)
- [ ] Integração com Slack/Teams (notificações)
- [ ] API de geração de relatórios

---

## Troubleshooting

### Template Not Found

```python
# Erro: jinja2.exceptions.TemplateNotFound: report.html

# Solução 1: Verificar path
print(generator.templates_dir)

# Solução 2: Especificar path absoluto
generator = ReportGenerator(
    templates_dir='/absolute/path/to/templates/'
)

# Solução 3: Usar fallback (automático)
```

### Scores Não Aparecem

```python
# Verificar estrutura de dados
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

### CSS Não Carrega

```html
<!-- Verificar CDN no template -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- Verificar conexão internet -->
<!-- Fallback: copiar Tailwind CSS inline -->
```

---

## Arquivos Relacionados

```
ai-factory-testing-framework/
├── src/
│   └── report_generator.py       # Classe principal
├── templates/
│   └── report.html                # Template Jinja2
├── reports/                       # Relatórios gerados
│   └── report_*.html
├── generate_sample_report.py      # Script de exemplo
└── REPORT_GENERATOR_GUIDE.md      # Esta documentação
```

---

## Contato e Suporte

**Projeto:** AI Factory Testing Framework v1.0
**Desenvolvido por:** Marcos Daniels / MOTTIVME
**Data:** Dezembro 2025

Para dúvidas ou sugestões, consulte:
- `HANDOFF.md` - Documentação geral do framework
- `README.md` - Quick start guide

---

**Status:** ✅ Production Ready
**Última atualização:** 31/12/2025
