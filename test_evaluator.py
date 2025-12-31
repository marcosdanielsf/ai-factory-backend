"""
Test script for Evaluator module
=================================
Validates that the Evaluator correctly evaluates agent performance.
"""

import os
import json
from src.evaluator import Evaluator, evaluate_sync
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock test data
MOCK_AGENT = {
    "id": "test-agent-001",
    "name": "Isabella SDR",
    "description": "Agente SDR para qualificação de leads B2B",
    "system_prompt": """Você é Isabella, uma SDR especializada em qualificação de leads B2B.

Seu objetivo é:
- Qualificar leads usando metodologia BANT
- Manter tom consultivo e profissional
- Agendar reuniões com leads qualificados

Regras:
- SEMPRE pergunte sobre Budget, Authority, Need e Timeline
- NUNCA faça promessas de desconto sem autorização
- Mantenha tom empático e consultivo
"""
}

MOCK_SKILL = {
    "name": "sdr-qualification",
    "rubric": None  # Will use default rubric
}

MOCK_TEST_RESULTS = [
    {
        "test_name": "Lead interessado em solução",
        "input": "Olá, gostaria de saber mais sobre a solução de vocês",
        "agent_response": "Olá! Fico feliz com seu interesse. Para eu entender melhor como podemos te ajudar, me conta: qual é o principal desafio que você está enfrentando hoje na sua operação?",
        "expected_behavior": "Engajar e fazer discovery",
        "passed": True,
        "execution_time": 2.5
    },
    {
        "test_name": "Descoberta de Budget",
        "input": "Precisamos melhorar nossa conversão de leads",
        "agent_response": "Entendo. Melhorar conversão é crucial. Me conta, você já tem algum orçamento separado para investir em uma solução que ajude com isso? É importante eu entender para recomendar a melhor opção.",
        "expected_behavior": "Perguntar sobre budget de forma consultiva",
        "passed": True,
        "execution_time": 3.1
    },
    {
        "test_name": "Identificação de Authority",
        "input": "Sim, temos orçamento. Cerca de R$ 10k/mês",
        "agent_response": "Ótimo! E você é a pessoa que toma a decisão sobre isso na empresa, ou precisa validar com alguém?",
        "expected_behavior": "Identificar decisor",
        "passed": True,
        "execution_time": 1.8
    },
    {
        "test_name": "Lead sem budget",
        "input": "Não tenho orçamento agora",
        "agent_response": "Entendo. Sem problema! Posso te enviar um material sobre ROI da nossa solução? Assim você pode avaliar a viabilidade com mais informações e voltamos a conversar no futuro.",
        "expected_behavior": "Não descartar, oferecer valor",
        "passed": True,
        "execution_time": 2.2
    },
    {
        "test_name": "Agendamento de reunião",
        "input": "Sou o decisor e temos urgência nisso",
        "agent_response": "Perfeito! Deixa eu agendar uma conversa de 30 minutos com nosso especialista. Você tem disponibilidade na próxima terça às 14h?",
        "expected_behavior": "Tentar agendar reunião",
        "passed": True,
        "execution_time": 2.0
    }
]


def test_evaluator_basic():
    """Test basic evaluator functionality"""
    print("\n" + "="*70)
    print("TEST 1: Basic Evaluator Initialization")
    print("="*70)

    try:
        evaluator = Evaluator()
        print("✓ Evaluator initialized successfully")
        print(f"  Model: {evaluator.model}")
        print(f"  Temperature: {evaluator.temperature}")
        print(f"  Max Tokens: {evaluator.max_tokens}")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize Evaluator: {e}")
        return False


def test_evaluate_sync():
    """Test synchronous evaluation"""
    print("\n" + "="*70)
    print("TEST 2: Synchronous Evaluation")
    print("="*70)

    try:
        print("Calling evaluate_sync with mock data...")
        print(f"  Agent: {MOCK_AGENT['name']}")
        print(f"  Test Cases: {len(MOCK_TEST_RESULTS)}")

        result = evaluate_sync(
            agent=MOCK_AGENT,
            skill=MOCK_SKILL,
            test_results=MOCK_TEST_RESULTS
        )

        print("\n✓ Evaluation completed successfully")
        print("\nRESULTS:")
        print(f"  Overall Score: {result['overall_score']}/10")
        print("\n  Dimension Scores:")
        for dimension, score in result['scores'].items():
            print(f"    - {dimension.capitalize()}: {score}/10")

        print(f"\n  Strengths ({len(result['strengths'])}):")
        for strength in result['strengths'][:3]:  # Show first 3
            print(f"    ✓ {strength}")

        print(f"\n  Weaknesses ({len(result['weaknesses'])}):")
        for weakness in result['weaknesses'][:3]:  # Show first 3
            print(f"    • {weakness}")

        print(f"\n  Failures: {len(result['failures'])}")
        if result['failures']:
            for failure in result['failures']:
                print(f"    ✗ {failure}")

        print(f"\n  Warnings: {len(result['warnings'])}")
        if result['warnings']:
            for warning in result['warnings']:
                print(f"    ⚠ {warning}")

        # Validate structure
        assert 'overall_score' in result, "Missing overall_score"
        assert 'scores' in result, "Missing scores"
        assert result['overall_score'] >= 0 and result['overall_score'] <= 10, "Invalid overall_score range"

        print("\n✓ Result structure is valid")

        # Save result to file for inspection
        with open('/Users/marcosdaniels/Downloads/ai-factory-testing-framework/test_evaluation_result.json', 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("\n✓ Full result saved to: test_evaluation_result.json")

        return True

    except Exception as e:
        print(f"\n✗ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_weighted_score_calculation():
    """Test weighted score calculation"""
    print("\n" + "="*70)
    print("TEST 3: Weighted Score Calculation")
    print("="*70)

    try:
        evaluator = Evaluator()

        test_scores = {
            'completeness': 9.0,
            'tone': 8.5,
            'engagement': 8.0,
            'compliance': 9.0,
            'conversion': 7.5
        }

        weighted = evaluator.calculate_weighted_score(test_scores)

        # Manual calculation
        expected = (9.0 * 0.25) + (8.5 * 0.20) + (8.0 * 0.20) + (9.0 * 0.20) + (7.5 * 0.15)

        print(f"  Test Scores: {test_scores}")
        print(f"  Calculated Weighted Score: {weighted}")
        print(f"  Expected: {expected:.2f}")

        assert abs(weighted - expected) < 0.01, f"Score mismatch: {weighted} != {expected}"

        print("✓ Weighted score calculation is correct")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_threshold_check():
    """Test if evaluation meets the 8.0 threshold"""
    print("\n" + "="*70)
    print("TEST 4: Threshold Check (8.0/10 for approval)")
    print("="*70)

    try:
        result = evaluate_sync(
            agent=MOCK_AGENT,
            skill=MOCK_SKILL,
            test_results=MOCK_TEST_RESULTS
        )

        threshold = 8.0
        score = result['overall_score']
        passed = score >= threshold

        print(f"  Overall Score: {score}/10")
        print(f"  Threshold: {threshold}/10")
        print(f"  Status: {'✓ PASSED' if passed else '✗ FAILED'}")

        if passed:
            print("\n✓ Agent meets approval threshold!")
        else:
            print(f"\n✗ Agent needs improvement (score: {score}, required: {threshold})")
            print("\n  Recommendations:")
            for rec in result.get('recommendations', [])[:3]:
                print(f"    • {rec}")

        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("AI FACTORY V4 - EVALUATOR TEST SUITE")
    print("="*70)

    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("\n✗ ERROR: ANTHROPIC_API_KEY not found in environment")
        print("  Please set it before running tests:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        return

    results = []

    # Run tests
    results.append(("Basic Initialization", test_evaluator_basic()))
    results.append(("Weighted Score Calculation", test_weighted_score_calculation()))
    results.append(("Synchronous Evaluation", test_evaluate_sync()))
    results.append(("Threshold Check", test_threshold_check()))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Evaluator is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")


if __name__ == "__main__":
    main()
