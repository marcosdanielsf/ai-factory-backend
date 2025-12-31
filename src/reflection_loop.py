"""
AI Factory Testing Framework - Reflection Loop
===============================================
Auto-melhoria de agentes usando Claude Opus.

Workflow:
1. Recebe resultado de teste com score < 8.0
2. Analisa weaknesses e failures
3. Gera novo prompt melhorado (v2)
4. Salva nova versão como 'pending_approval'
5. (Opcional) Testa automaticamente a v2
6. Se v2 > v1: marca como 'ready_for_approval'
7. Admin aprova no Dashboard -> status = 'active'
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ReflectionLoop:
    """
    Motor de auto-melhoria de agentes.

    Usa Claude Opus para analisar falhas e gerar prompts melhorados.
    """

    REFLECTION_PROMPT = """Você é um especialista em engenharia de prompts para agentes SDR/BDR.

## CONTEXTO
Um agente de IA foi testado e recebeu score {score}/10 (mínimo para aprovação: 8.0).

## AGENTE ATUAL
Nome: {agent_name}
Versão: {current_version}

### System Prompt Atual:
```
{current_prompt}
```

## RESULTADO DO TESTE

### Scores por Dimensão:
- Completeness (25%): {scores[completeness]}/10
- Tone (20%): {scores[tone]}/10
- Engagement (20%): {scores[engagement]}/10
- Compliance (20%): {scores[compliance]}/10
- Conversion (15%): {scores[conversion]}/10

### Pontos Fortes:
{strengths}

### Pontos Fracos (CRÍTICO - FOCO DA MELHORIA):
{weaknesses}

### Falhas Identificadas:
{failures}

### Recomendações do Avaliador:
{recommendations}

## SUA TAREFA

Reescreva o System Prompt do agente para corrigir os pontos fracos identificados.

### Regras:
1. MANTENHA a persona e tom original (não mude o nome/personalidade)
2. MANTENHA as regras de compliance que já existem
3. ADICIONE instruções específicas para corrigir cada ponto fraco
4. REFORCE comportamentos que já estão bons
5. Seja ESPECÍFICO nas instruções (não genérico)
6. Use exemplos concretos quando apropriado
7. Não remova funcionalidades existentes

### Formato de Resposta:
Retorne um JSON com esta estrutura:

```json
{{
  "improved_prompt": "O novo system prompt completo aqui...",
  "changes_summary": [
    "Mudança 1: Descrição do que foi alterado",
    "Mudança 2: Descrição do que foi alterado"
  ],
  "expected_improvements": {{
    "completeness": "+1.5 - Adicionei instruções para qualificação BANT completa",
    "tone": "+0.0 - Mantido (já estava bom)",
    "engagement": "+0.5 - Reforçei perguntas abertas",
    "compliance": "+0.0 - Mantido (já estava bom)",
    "conversion": "+1.0 - Adicionei técnicas de fechamento"
  }},
  "risk_assessment": "Baixo/Médio/Alto - Explicação do risco das mudanças"
}}
```

IMPORTANTE: Retorne APENAS o JSON, sem texto adicional."""

    def __init__(
        self,
        api_key: str = None,
        model: str = "claude-opus-4-20250514",
        supabase_client = None
    ):
        """
        Inicializa o ReflectionLoop.

        Args:
            api_key: Anthropic API key
            model: Modelo para gerar melhorias
            supabase_client: Cliente Supabase para salvar novas versões
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.supabase = supabase_client

        logger.info(f"ReflectionLoop initialized with model: {self.model}")

    async def should_reflect(
        self,
        test_result: Dict,
        min_score: float = 6.0,
        max_score: float = 8.0
    ) -> bool:
        """
        Determina se o agente deve passar pelo reflection loop.

        Args:
            test_result: Resultado do teste
            min_score: Score mínimo para tentar melhorar (muito baixo = problema estrutural)
            max_score: Score máximo (acima disso já está aprovado)

        Returns:
            True se deve tentar melhorar
        """
        score = test_result.get('overall_score', 0)

        # Se score muito baixo, precisa revisão manual
        if score < min_score:
            logger.info(f"Score {score} too low for auto-reflection (min: {min_score})")
            return False

        # Se score já bom, não precisa melhorar
        if score >= max_score:
            logger.info(f"Score {score} already good (threshold: {max_score})")
            return False

        # Score entre min e max: pode tentar melhorar
        logger.info(f"Score {score} eligible for reflection")
        return True

    async def generate_improved_prompt(
        self,
        agent: Dict,
        test_result: Dict
    ) -> Dict:
        """
        Gera um prompt melhorado baseado nos resultados do teste.

        Args:
            agent: Dados do agente atual
            test_result: Resultado completo do teste

        Returns:
            Dict com improved_prompt, changes_summary, expected_improvements
        """
        logger.info(f"Generating improved prompt for agent {agent.get('id', 'unknown')}")

        # Extrair dados do teste
        overall_score = test_result.get('overall_score', 0)
        test_details = test_result.get('test_details', {})
        scores = test_details.get('scores', {})

        # Formatar listas para o prompt
        strengths = "\n".join(f"- {s}" for s in test_details.get('strengths', [])) or "- Nenhum identificado"
        weaknesses = "\n".join(f"- {w}" for w in test_details.get('weaknesses', [])) or "- Nenhum identificado"
        failures = "\n".join(f"- {f}" for f in test_details.get('failures', [])) or "- Nenhuma"
        recommendations = "\n".join(f"- {r}" for r in test_details.get('recommendations', [])) or "- Nenhuma"

        # Montar prompt
        reflection_prompt = self.REFLECTION_PROMPT.format(
            score=overall_score,
            agent_name=agent.get('name') or agent.get('version', 'Unknown'),
            current_version=agent.get('version', 'v1'),
            current_prompt=agent.get('system_prompt', ''),
            scores=scores,
            strengths=strengths,
            weaknesses=weaknesses,
            failures=failures,
            recommendations=recommendations
        )

        try:
            # Chamar Claude Opus
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": reflection_prompt}
                ]
            )

            response_text = response.content[0].text

            # Parsear JSON
            result = self._parse_reflection_response(response_text)

            logger.info(f"Generated improved prompt with {len(result.get('changes_summary', []))} changes")

            return result

        except Exception as e:
            logger.error(f"Error generating improved prompt: {e}")
            raise

    def _parse_reflection_response(self, response_text: str) -> Dict:
        """Extrai JSON da resposta do Claude"""
        import re

        # Tentar extrair JSON diretamente
        try:
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

        # Fallback
        logger.warning("Could not parse reflection response as JSON")
        return {
            'improved_prompt': response_text,
            'changes_summary': ['Could not parse structured response'],
            'expected_improvements': {},
            'risk_assessment': 'Unknown'
        }

    async def create_new_version(
        self,
        original_agent: Dict,
        improved_prompt: str,
        reflection_result: Dict,
        test_result: Dict
    ) -> Dict:
        """
        Cria uma nova versão do agente no Supabase.

        Args:
            original_agent: Agente original
            improved_prompt: Novo prompt gerado
            reflection_result: Resultado completo da reflection
            test_result: Resultado do teste que triggou a reflection

        Returns:
            Nova agent_version criada
        """
        if not self.supabase:
            logger.warning("No Supabase client - cannot save new version")
            return None

        # Determinar nova versão
        current_version = original_agent.get('version', 'v1')
        if current_version.startswith('v'):
            try:
                version_num = float(current_version[1:].split('-')[0])
                new_version = f"v{version_num + 0.1:.1f}-reflection"
            except:
                new_version = f"{current_version}-reflection"
        else:
            new_version = f"{current_version}-v2"

        # Preparar dados da nova versão (copiar campos relevantes do original)
        new_agent_data = {
            # Campos de identificação
            'client_id': original_agent.get('client_id'),
            'location_id': original_agent.get('location_id'),
            'sub_account_id': original_agent.get('sub_account_id'),
            'agent_name': original_agent.get('agent_name'),

            # Nova versão
            'version': new_version,
            'system_prompt': improved_prompt,

            # Copiar configurações existentes
            'tools_config': original_agent.get('tools_config') or {},
            'personality_config': original_agent.get('personality_config') or {},
            'qualification_config': original_agent.get('qualification_config') or {},
            'compliance_rules': original_agent.get('compliance_rules') or {},
            'business_config': original_agent.get('business_config') or {},
            'hyperpersonalization': original_agent.get('hyperpersonalization') or {},

            # Status e metadata
            'status': 'pending_approval',  # Precisa aprovação do admin
            'is_active': False,  # Não ativar automaticamente
            'reflection_count': (original_agent.get('reflection_count') or 0) + 1,
        }

        # Adicionar metadata de reflection como JSON em validation_result
        reflection_metadata = {
            'reflection_source': 'auto_improvement',
            'parent_version_id': original_agent.get('id'),
            'original_score': test_result.get('overall_score'),
            'changes_summary': reflection_result.get('changes_summary', []),
            'expected_improvements': reflection_result.get('expected_improvements', {}),
            'risk_assessment': reflection_result.get('risk_assessment'),
            'generated_at': datetime.utcnow().isoformat()
        }
        new_agent_data['validation_result'] = reflection_metadata

        try:
            # Inserir no Supabase
            response = self.supabase._request(
                'POST',
                'agent_versions',
                json_data=new_agent_data,
                use_service_role=True
            )

            if response.status_code in [200, 201]:
                new_agent = response.json()[0]
                logger.info(f"Created new agent version: {new_agent['id']} ({new_version})")
                return new_agent
            else:
                logger.error(f"Failed to create new version: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error creating new version: {e}")
            raise

    async def run_reflection(
        self,
        agent: Dict,
        test_result: Dict,
        auto_test: bool = False
    ) -> Dict:
        """
        Executa o ciclo completo de reflection.

        Args:
            agent: Agente a ser melhorado
            test_result: Resultado do teste
            auto_test: Se True, testa a nova versão automaticamente

        Returns:
            Dict com resultado da reflection
        """
        logger.info("=" * 50)
        logger.info("REFLECTION LOOP STARTED")
        logger.info("=" * 50)

        # 1. Verificar se deve fazer reflection
        if not await self.should_reflect(test_result):
            return {
                'status': 'skipped',
                'reason': 'Score not in reflection range',
                'original_score': test_result.get('overall_score')
            }

        # 2. Gerar prompt melhorado
        logger.info("Generating improved prompt...")
        reflection_result = await self.generate_improved_prompt(agent, test_result)

        improved_prompt = reflection_result.get('improved_prompt', '')
        if not improved_prompt:
            return {
                'status': 'failed',
                'reason': 'Could not generate improved prompt'
            }

        # 3. Criar nova versão no Supabase
        logger.info("Creating new agent version...")
        new_agent = await self.create_new_version(
            original_agent=agent,
            improved_prompt=improved_prompt,
            reflection_result=reflection_result,
            test_result=test_result
        )

        result = {
            'status': 'success',
            'original_agent_id': agent.get('id'),
            'original_score': test_result.get('overall_score'),
            'new_agent_id': new_agent.get('id') if new_agent else None,
            'new_version': new_agent.get('version') if new_agent else None,
            'changes_summary': reflection_result.get('changes_summary', []),
            'expected_improvements': reflection_result.get('expected_improvements', {}),
            'risk_assessment': reflection_result.get('risk_assessment'),
            'new_agent_status': 'pending_approval'
        }

        # 4. (Opcional) Testar nova versão
        if auto_test and new_agent:
            logger.info("Auto-testing new version...")
            # Importar aqui para evitar circular import
            from .test_runner import run_quick_test

            try:
                new_test_result = await run_quick_test(new_agent['id'])
                result['new_score'] = new_test_result.get('overall_score')
                result['improvement'] = result['new_score'] - result['original_score']

                # Atualizar status baseado no resultado
                if result['new_score'] >= 8.0:
                    result['new_agent_status'] = 'ready_for_approval'
                    logger.info(f"New version passed! Score: {result['new_score']}")
                elif result['new_score'] > result['original_score']:
                    result['new_agent_status'] = 'improved_pending_approval'
                    logger.info(f"New version improved: {result['original_score']} -> {result['new_score']}")
                else:
                    result['new_agent_status'] = 'no_improvement'
                    logger.warning(f"New version did not improve: {result['original_score']} -> {result['new_score']}")

            except Exception as e:
                logger.error(f"Auto-test failed: {e}")
                result['auto_test_error'] = str(e)

        logger.info("=" * 50)
        logger.info(f"REFLECTION COMPLETE: {result['new_agent_status']}")
        logger.info("=" * 50)

        return result


# Helper function for quick reflection
async def reflect_and_improve(
    agent_id: str,
    test_result: Dict,
    auto_test: bool = False
) -> Dict:
    """
    Função helper para rodar reflection rapidamente.

    Usage:
        result = await reflect_and_improve(
            agent_id="uuid",
            test_result=test_result_dict,
            auto_test=True
        )
    """
    from .supabase_requests import SupabaseRequestsClient

    supabase = SupabaseRequestsClient()
    agent = supabase.get_agent_version(agent_id)

    if not agent:
        raise ValueError(f"Agent {agent_id} not found")

    loop = ReflectionLoop(supabase_client=supabase)

    return await loop.run_reflection(
        agent=agent,
        test_result=test_result,
        auto_test=auto_test
    )
