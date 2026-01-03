"""
AI Factory Testing Framework - Evaluator (LLM-as-Judge)
=======================================================
Avalia agentes usando Claude Opus como juiz.
Com retry logic, logging estruturado e error handling robusto.

Rubrica de Avaliacao (5 dimensoes):
1. Completeness (25%): BANT completo? Coletou todas as informacoes necessarias?
2. Tone (20%): Tom consultivo e profissional?
3. Engagement (20%): Lead engajou e permaneceu na conversa?
4. Compliance (20%): Seguiu guardrails e instrucoes do prompt?
5. Conversion (15%): Conseguiu converter/agendar/qualificar?
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from anthropic import Anthropic, APIError, RateLimitError as AnthropicRateLimitError

from src.core.logging_config import get_logger, LogContext, Timer
from src.core.retry import with_retry, ANTHROPIC_RETRY_CONFIG, RetryConfig
from src.core.exceptions import (
    AnthropicAPIError,
    AnthropicRateLimitError as CustomRateLimitError,
    ValidationError,
)

logger = get_logger(__name__)


# Custom retry config for evaluation (longer timeouts, more retries)
EVALUATOR_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    initial_delay_seconds=3.0,
    max_delay_seconds=180.0,
    exponential_base=2.0,
    jitter=True,
    retry_on_exceptions=(
        AnthropicAPIError,
        CustomRateLimitError,
        APIError,
        AnthropicRateLimitError,
        ConnectionError,
        TimeoutError,
    ),
)


class Evaluator:
    """
    LLM-as-Judge para avaliar respostas de agentes IA.

    Usa Claude Opus para analisar conversas e atribuir scores
    baseados em uma rubrica de 5 dimensoes.

    Features:
    - Retry automático em chamadas à API Anthropic
    - Logging estruturado com métricas de performance
    - Error handling específico para diferentes tipos de falha
    - Tracking de tokens utilizados
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
        max_tokens: int = 4000,
    ):
        """
        Inicializa o Evaluator.

        Args:
            api_key: Anthropic API key (default from env)
            model: Modelo a usar para avaliação
            temperature: Temperatura para geração
            max_tokens: Max tokens na resposta

        Raises:
            ValidationError: If API key is not configured
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValidationError(
                message="ANTHROPIC_API_KEY must be set",
                field="api_key",
            )

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info(
            "Evaluator initialized",
            extra_fields={
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
        )

    @with_retry(config=EVALUATOR_RETRY_CONFIG)
    async def _call_anthropic(self, prompt: str) -> Dict[str, Any]:
        """
        Call Anthropic API with retry logic.

        Args:
            prompt: The evaluation prompt

        Returns:
            Dict with response text and token usage

        Raises:
            AnthropicAPIError: On API failures after retries exhausted
        """
        with Timer() as timer:
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                # Extract usage metrics
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                response_text = response.content[0].text

                logger.info(
                    "Anthropic API call completed",
                    extra_fields={
                        "model": self.model,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens,
                        "duration_ms": timer.duration_ms,
                    },
                )

                return {
                    "text": response_text,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "duration_ms": timer.duration_ms,
                }

            except AnthropicRateLimitError as e:
                logger.warning(
                    "Anthropic rate limit hit",
                    extra_fields={
                        "model": self.model,
                        "error": str(e),
                    },
                )
                raise CustomRateLimitError(
                    message="Anthropic API rate limit exceeded",
                    retry_after=60,
                    original_error=e,
                )

            except APIError as e:
                logger.error(
                    "Anthropic API error",
                    extra_fields={
                        "model": self.model,
                        "status_code": getattr(e, 'status_code', None),
                        "error": str(e),
                    },
                )
                raise AnthropicAPIError(
                    message=f"Anthropic API error: {str(e)}",
                    details={"status_code": getattr(e, 'status_code', None)},
                    original_error=e,
                )

            except Exception as e:
                logger.error(
                    "Unexpected error calling Anthropic",
                    extra_fields={
                        "model": self.model,
                        "error_type": type(e).__name__,
                        "error": str(e),
                    },
                )
                raise AnthropicAPIError(
                    message=f"Unexpected error: {str(e)}",
                    original_error=e,
                )

    async def evaluate(
        self,
        agent: Dict,
        skill: Optional[Dict],
        test_results: List[Dict],
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
        agent_name = agent.get('name', agent.get('id', 'unknown'))

        with LogContext(operation="evaluate_agent", agent_name=agent_name):
            with Timer() as total_timer:
                logger.info(
                    "Starting agent evaluation",
                    extra_fields={
                        "agent_id": agent.get('id'),
                        "test_count": len(test_results),
                    },
                )

                # Preparar contexto do agente
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
                    test_cases_json=test_cases_json,
                )

                try:
                    # Chamar Claude Opus com retry
                    api_response = await self._call_anthropic(evaluation_prompt)

                    # Parsear JSON da resposta
                    evaluation = self._parse_evaluation_response(api_response["text"])

                    # Validar e completar campos faltantes
                    evaluation = self._validate_evaluation(evaluation)

                    # Adicionar métricas da API
                    evaluation["_metadata"] = {
                        "model": self.model,
                        "input_tokens": api_response["input_tokens"],
                        "output_tokens": api_response["output_tokens"],
                        "api_duration_ms": api_response["duration_ms"],
                        "total_duration_ms": total_timer.duration_ms,
                    }

                    logger.info(
                        "Agent evaluation completed",
                        extra_fields={
                            "agent_id": agent.get('id'),
                            "overall_score": evaluation['overall_score'],
                            "input_tokens": api_response["input_tokens"],
                            "output_tokens": api_response["output_tokens"],
                            "duration_ms": total_timer.duration_ms,
                        },
                    )

                    return evaluation

                except (AnthropicAPIError, CustomRateLimitError) as e:
                    logger.error(
                        "Evaluation failed due to API error",
                        extra_fields={
                            "agent_id": agent.get('id'),
                            "error_code": getattr(e, 'error_code', None),
                            "error": str(e),
                        },
                    )
                    # Retornar avaliação de fallback
                    return self._fallback_evaluation(str(e))

                except Exception as e:
                    logger.error(
                        "Unexpected error during evaluation",
                        extra_fields={
                            "agent_id": agent.get('id'),
                            "error_type": type(e).__name__,
                            "error": str(e),
                        },
                        exc_info=True,
                    )
                    return self._fallback_evaluation(str(e))

    def _extract_purpose(self, agent: Dict) -> str:
        """Extrai o propósito do agente dos metadados"""
        # Tentar diferentes campos
        if agent.get('description'):
            return agent['description']

        config = agent.get('agent_config', {})
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except json.JSONDecodeError:
                config = {}

        if config.get('proposito'):
            return config['proposito']

        if config.get('objetivo'):
            return config['objetivo']

        # Extrair do prompt do sistema
        prompt = agent.get('system_prompt', '')
        if prompt:
            # Pegar primeira linha significativa
            lines = [line.strip() for line in prompt.split('\n') if line.strip()]
            if lines:
                return lines[0][:200]

        return "Agente SDR para qualificação de leads"

    def _summarize_prompt(self, system_prompt: str, max_chars: int = 1000) -> str:
        """Resume o prompt do sistema para o contexto"""
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
        """Extrai JSON da resposta do Claude"""
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
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Se falhou, criar estrutura a partir do texto
        logger.warning(
            "Could not parse JSON response, using fallback",
            extra_fields={"response_length": len(response_text)},
        )
        return self._fallback_evaluation("Failed to parse evaluation response")

    def _validate_evaluation(self, evaluation: Dict) -> Dict:
        """Valida e completa campos faltantes"""
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
        """Retorna avaliação de fallback em caso de erro"""
        logger.warning(
            "Using fallback evaluation",
            extra_fields={"error": error_message},
        )
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
            'recommendations': ["Re-run evaluation after fixing the error"],
            '_metadata': {
                'is_fallback': True,
                'error': error_message,
            }
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
async def evaluate_async(
    agent: Dict,
    skill: Optional[Dict],
    test_results: List[Dict],
    api_key: str = None,
) -> Dict:
    """
    Avaliação assíncrona - função wrapper para uso simples.
    """
    evaluator = Evaluator(api_key=api_key)
    return await evaluator.evaluate(agent, skill, test_results)
