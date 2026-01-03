"""
AI Factory Testing Framework - Evaluator (LLM-as-Judge)
=======================================================

Módulo de avaliação de agentes IA usando Claude Opus como juiz.
Implementa o padrão LLM-as-Judge para avaliar respostas de agentes
baseado em uma rubrica de 5 dimensões.

Rubrica de Avaliação (5 dimensões):
    1. Completeness (25%): BANT completo? Coletou todas as informações?
    2. Tone (20%): Tom consultivo e profissional?
    3. Engagement (20%): Lead engajou e permaneceu na conversa?
    4. Compliance (20%): Seguiu guardrails e instruções do prompt?
    5. Conversion (15%): Conseguiu converter/agendar/qualificar?

Example:
    >>> from src import Evaluator
    >>> evaluator = Evaluator()
    >>> result = await evaluator.evaluate(
    ...     agent=agent_data,
    ...     skill=skill_data,
    ...     test_results=test_results
    ... )
    >>> print(f"Score: {result['overall_score']}")

Environment Variables:
    ANTHROPIC_API_KEY: Chave da API Anthropic (obrigatório)

Scores:
    - 0-5.9: Reprovado (needs improvement)
    - 6.0-7.9: Aceitável mas precisa melhorar
    - 8.0-10.0: Aprovado (framework_approved=True)
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class Evaluator:
    """
    LLM-as-Judge para avaliar respostas de agentes IA.

    Usa Claude Opus para analisar conversas e atribuir scores
    baseados em uma rubrica de 5 dimensões ponderadas.

    Attributes:
        api_key (str): Chave da API Anthropic
        client (Anthropic): Cliente Anthropic
        model (str): Modelo a usar (default: claude-opus-4-20250514)
        temperature (float): Temperatura para geração (default: 0.3)
        max_tokens (int): Max tokens na resposta (default: 4000)

    Dimensões de Avaliação:
        - Completeness (25%): Qualificação BANT completa
        - Tone (20%): Tom consultivo e profissional
        - Engagement (20%): Engajamento do lead
        - Compliance (20%): Aderência às instruções
        - Conversion (15%): Conversão/agendamento

    Example:
        >>> evaluator = Evaluator()
        >>> result = await evaluator.evaluate(
        ...     agent={"name": "SDR", "system_prompt": "..."},
        ...     skill=None,
        ...     test_results=[{"name": "test1", "agent_response": "..."}]
        ... )
        >>> print(f"Score: {result['overall_score']}")
        >>> print(f"Strengths: {result['strengths']}")
        >>> print(f"Weaknesses: {result['weaknesses']}")
    """

    DEFAULT_RUBRIC = """
## Rubrica de Avaliacao de Agentes SDR

### 1. COMPLETENESS (25%)
Avalia se o agente coletou informacoes BANT completas:
- Budget: Descobriu capacidade de investimento?
- Authority: Identificou o decisor?
- Need: Entendeu a dor/necessidade real?
- Timeline: Perguntou sobre prazo/urgencia?

**Score:**
- 10: BANT completo, todas as 4 dimensoes cobertas
- 8: 3 de 4 dimensoes cobertas
- 6: 2 de 4 dimensoes cobertas
- 4: Apenas 1 dimensao coberta
- 2: Nenhuma qualificacao feita

### 2. TONE (20%)
Avalia se o tom foi adequado e profissional:
- Tom consultivo (nao vendedor agressivo)
- Linguagem apropriada ao contexto
- Empatia e escuta ativa
- Personalização da comunicação

**Score:**
- 10: Tom perfeito, consultivo, empático
- 8: Bom tom, pequenos ajustes necessários
- 6: Tom aceitável, mas genérico
- 4: Tom inadequado ou muito agressivo
- 2: Tom completamente errado

### 3. ENGAGEMENT (20%)
Avalia se o lead foi engajado na conversa:
- Fez perguntas relevantes
- Obteve respostas do lead
- Manteve conversa fluindo
- Demonstrou interesse genuíno

**Score:**
- 10: Engajamento excelente, conversa fluida
- 8: Bom engajamento, lead participativo
- 6: Engajamento médio
- 4: Lead desengajado
- 2: Conversa morreu, sem engajamento

### 4. COMPLIANCE (20%)
Avalia se seguiu as instruções e guardrails:
- Não prometeu o que não pode cumprir
- Seguiu o script/prompt do agente
- Não vazou informações sensíveis
- Manteve-se no escopo

**Score:**
- 10: 100% compliance
- 8: Pequenos desvios não críticos
- 6: Alguns desvios das instruções
- 4: Desvios significativos
- 2: Ignorou instruções completamente

### 5. CONVERSION (15%)
Avalia se atingiu o objetivo de conversão:
- Conseguiu agendar reunião/call?
- Qualificou como MQL/SQL?
- Obteve próximo passo definido?
- Lead avançou no funil?

**Score:**
- 10: Conversão completa, reunião agendada
- 8: Próximo passo claro definido
- 6: Lead qualificado mas sem conversão
- 4: Conversa inconclusiva
- 2: Lead perdido/desqualificado
"""

    EVALUATION_PROMPT_TEMPLATE = """Você é um avaliador especialista de agentes de vendas (SDR/BDR).

## INFORMAÇÕES DO AGENTE
Nome: {agent_name}
Propósito: {agent_purpose}
Instruções do Sistema (resumo):
{system_prompt_summary}

## RUBRICA DE AVALIAÇÃO
{rubric}

## CASOS DE TESTE EXECUTADOS
{test_cases_json}

## TAREFA
Analise cada caso de teste e avalie o agente nas 5 dimensões.
Para cada caso, considere:
- O input do lead
- A resposta do agente
- O comportamento esperado

## RESPOSTA OBRIGATÓRIA
Retorne um JSON válido com esta estrutura exata:

```json
{{
  "overall_score": 8.5,
  "scores": {{
    "completeness": 9.0,
    "tone": 8.5,
    "engagement": 8.0,
    "compliance": 9.0,
    "conversion": 7.5
  }},
  "test_case_evaluations": [
    {{
      "test_name": "nome do teste",
      "score": 8.5,
      "passed": true,
      "feedback": "Feedback específico sobre este caso"
    }}
  ],
  "strengths": [
    "Ponto forte 1",
    "Ponto forte 2"
  ],
  "weaknesses": [
    "Ponto a melhorar 1",
    "Ponto a melhorar 2"
  ],
  "failures": [
    "Falha crítica 1 (se houver)"
  ],
  "warnings": [
    "Alerta/risco identificado (se houver)"
  ],
  "recommendations": [
    "Recomendação de melhoria 1",
    "Recomendação de melhoria 2"
  ]
}}
```

IMPORTANTE:
- Seja objetivo e justo na avaliação
- Base os scores apenas nas evidências dos testes
- overall_score é a média ponderada: (completeness*0.25 + tone*0.20 + engagement*0.20 + compliance*0.20 + conversion*0.15)
- Todos os scores são de 0 a 10
- Se um teste não cobriu uma dimensão, baseie-se no que foi observável
- Retorne APENAS o JSON, sem texto adicional antes ou depois
"""

    def __init__(
        self,
        api_key: str = None,
        model: str = "claude-opus-4-20250514",
        temperature: float = 0.3,
        max_tokens: int = 4000
    ):
        """
        Inicializa o Evaluator.

        Args:
            api_key: Anthropic API key (default from env)
            model: Modelo a usar para avaliação
            temperature: Temperatura para geração
            max_tokens: Max tokens na resposta
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info(f"Evaluator initialized with model: {self.model}")

    async def evaluate(
        self,
        agent: Dict,
        skill: Optional[Dict],
        test_results: List[Dict]
    ) -> Dict:
        """
        Avalia um agente baseado nos resultados dos testes.

        Args:
            agent: Dados do agente (agent_version do Supabase)
            skill: Skill do agente (se existir)
            test_results: Lista de resultados de casos de teste

        Returns:
            Dict com scores, strengths, weaknesses, failures, warnings
        """
        logger.info(f"Evaluating agent: {agent.get('name', agent.get('id', 'unknown'))}")

        # Preparar contexto do agente
        agent_name = agent.get('name', 'Agente Desconhecido')
        agent_purpose = self._extract_purpose(agent)
        system_prompt_summary = self._summarize_prompt(agent.get('system_prompt', ''))

        # Usar rubrica do skill ou default
        rubric = self.DEFAULT_RUBRIC
        if skill and skill.get('rubric'):
            rubric = skill['rubric']

        # Formatar casos de teste
        test_cases_json = json.dumps(test_results, ensure_ascii=False, indent=2)

        # Montar prompt
        evaluation_prompt = self.EVALUATION_PROMPT_TEMPLATE.format(
            agent_name=agent_name,
            agent_purpose=agent_purpose,
            system_prompt_summary=system_prompt_summary,
            rubric=rubric,
            test_cases_json=test_cases_json
        )

        try:
            # Chamar Claude Opus
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": evaluation_prompt
                    }
                ]
            )

            # Extrair resposta
            response_text = response.content[0].text

            # Parsear JSON da resposta
            evaluation = self._parse_evaluation_response(response_text)

            # Validar e completar campos faltantes
            evaluation = self._validate_evaluation(evaluation)

            logger.info(
                f"Evaluation complete: overall_score={evaluation['overall_score']:.2f}"
            )

            return evaluation

        except Exception as e:
            logger.error(f"Error during evaluation: {e}", exc_info=True)
            # Retornar avaliação de fallback
            return self._fallback_evaluation(str(e))

    def _extract_purpose(self, agent: Dict) -> str:
        """
        Extrai o propósito do agente dos metadados.

        Tenta encontrar uma descrição do propósito em vários campos
        possíveis do agent_config.

        Args:
            agent: Dict com dados do agente.

        Returns:
            String descrevendo o propósito do agente.
        """
        # Tentar diferentes campos
        if agent.get('description'):
            return agent['description']

        config = agent.get('agent_config', {})
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except:
                config = {}

        if config.get('proposito'):
            return config['proposito']

        if config.get('objetivo'):
            return config['objetivo']

        # Extrair do prompt do sistema
        prompt = agent.get('system_prompt', '')
        if prompt:
            # Pegar primeira linha significativa
            lines = [l.strip() for l in prompt.split('\n') if l.strip()]
            if lines:
                return lines[0][:200]

        return "Agente SDR para qualificação de leads"

    def _summarize_prompt(self, system_prompt: str, max_chars: int = 1000) -> str:
        """
        Resume o prompt do sistema para o contexto de avaliação.

        Prioriza linhas importantes (regras, guardrails, objetivos)
        e trunca o resto para caber no limite.

        Args:
            system_prompt: Prompt completo do agente.
            max_chars: Limite de caracteres (default: 1000).

        Returns:
            Versão resumida do prompt.
        """
        if not system_prompt:
            return "(Prompt não disponível)"

        # Se for curto, retorna inteiro
        if len(system_prompt) <= max_chars:
            return system_prompt

        # Senão, extrai partes importantes
        lines = system_prompt.split('\n')
        summary_parts = []
        current_len = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Priorizar linhas com keywords importantes
            is_important = any(kw in line.lower() for kw in [
                'você é', 'voce e', 'objetivo', 'nunca', 'sempre',
                'importante', 'regra', 'guardrail', 'proibido'
            ])

            if is_important or current_len < max_chars * 0.5:
                if current_len + len(line) <= max_chars:
                    summary_parts.append(line)
                    current_len += len(line)

        return '\n'.join(summary_parts) + '\n...(resumido)'

    def _parse_evaluation_response(self, response_text: str) -> Dict:
        """
        Extrai e parseia JSON da resposta do Claude.

        Tenta múltiplas estratégias para extrair JSON válido
        da resposta, incluindo remoção de markdown.

        Args:
            response_text: Resposta bruta do Claude.

        Returns:
            Dict com a avaliação parseada.
        """
        # Tentar extrair JSON diretamente
        try:
            # Remover possíveis ```json e ``` do markdown
            text = response_text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]

            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        # Tentar encontrar JSON no texto
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Se falhou, criar estrutura a partir do texto
        logger.warning("Could not parse JSON response, using fallback")
        return self._fallback_evaluation("Failed to parse evaluation response")

    def _validate_evaluation(self, evaluation: Dict) -> Dict:
        """
        Valida e completa campos faltantes na avaliação.

        Garante que todos os campos obrigatórios existam e
        recalcula o score geral para consistência.

        Args:
            evaluation: Dict com avaliação bruta do Claude.

        Returns:
            Dict validado com todos os campos obrigatórios.
        """
        # Campos obrigatórios com defaults
        defaults = {
            'overall_score': 5.0,
            'scores': {
                'completeness': 5.0,
                'tone': 5.0,
                'engagement': 5.0,
                'compliance': 5.0,
                'conversion': 5.0
            },
            'test_case_evaluations': [],
            'strengths': [],
            'weaknesses': [],
            'failures': [],
            'warnings': [],
            'recommendations': []
        }

        for key, default_value in defaults.items():
            if key not in evaluation:
                evaluation[key] = default_value

        # Garantir que scores é um dict completo
        if 'scores' in evaluation:
            for score_key in ['completeness', 'tone', 'engagement', 'compliance', 'conversion']:
                if score_key not in evaluation['scores']:
                    evaluation['scores'][score_key] = 5.0

        # Recalcular overall_score para garantir consistência
        scores = evaluation['scores']
        calculated_overall = (
            scores['completeness'] * 0.25 +
            scores['tone'] * 0.20 +
            scores['engagement'] * 0.20 +
            scores['compliance'] * 0.20 +
            scores['conversion'] * 0.15
        )

        # Usar o calculado se diferir muito
        if abs(calculated_overall - evaluation['overall_score']) > 0.5:
            evaluation['overall_score'] = round(calculated_overall, 2)

        return evaluation

    def _fallback_evaluation(self, error_message: str) -> Dict:
        """
        Retorna avaliação de fallback em caso de erro.

        Usado quando a avaliação com Claude falha por qualquer motivo.
        Retorna score neutro (5.0) com mensagem de erro.

        Args:
            error_message: Descrição do erro ocorrido.

        Returns:
            Dict com avaliação padrão e mensagem de erro.
        """
        return {
            'overall_score': 5.0,
            'scores': {
                'completeness': 5.0,
                'tone': 5.0,
                'engagement': 5.0,
                'compliance': 5.0,
                'conversion': 5.0
            },
            'test_case_evaluations': [],
            'strengths': [],
            'weaknesses': [],
            'failures': [f"Evaluation failed: {error_message}"],
            'warnings': ["Fallback evaluation used due to error"],
            'recommendations': ["Re-run evaluation after fixing the error"]
        }

    def calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """
        Calcula score ponderado.

        Pesos:
        - completeness: 25%
        - tone: 20%
        - engagement: 20%
        - compliance: 20%
        - conversion: 15%
        """
        weights = {
            'completeness': 0.25,
            'tone': 0.20,
            'engagement': 0.20,
            'compliance': 0.20,
            'conversion': 0.15
        }

        total = sum(
            scores.get(dim, 5.0) * weight
            for dim, weight in weights.items()
        )

        return round(total, 2)


# Alias para uso direto
def evaluate_sync(
    agent: Dict,
    skill: Optional[Dict],
    test_results: List[Dict],
    api_key: str = None
) -> Dict:
    """
    Função wrapper para avaliação síncrona simplificada.

    Cria um Evaluator e executa avaliação em uma única chamada.
    Útil para scripts e uso rápido.

    Args:
        agent: Dict com dados do agente (name, system_prompt, etc).
        skill: Dict com skill do agente ou None.
        test_results: Lista de resultados de testes executados.
        api_key: Anthropic API key (opcional, usa env var).

    Returns:
        Dict com resultado da avaliação.

    Example:
        >>> result = evaluate_sync(
        ...     agent={"name": "SDR", "system_prompt": "..."},
        ...     skill=None,
        ...     test_results=[{"name": "test1", "agent_response": "Oi!"}]
        ... )
        >>> print(f"Score: {result['overall_score']}")
    """
    evaluator = Evaluator(api_key=api_key)
    return evaluator.evaluate(agent, skill, test_results)
