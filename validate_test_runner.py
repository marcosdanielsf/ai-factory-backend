#!/usr/bin/env python3
"""
Validation Script for test_runner.py
====================================

Valida:
1. Estrutura do TestRunner
2. Métodos obrigatórios
3. Integração com Evaluator e ReportGenerator
4. Estrutura dos dados
"""

import sys
import inspect
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.test_runner import TestRunner, DEFAULT_SDR_TEST_CASES
from src.evaluator import Evaluator
from src.report_generator import ReportGenerator


def check_class_structure():
    """Valida estrutura da classe TestRunner"""
    print("Checking TestRunner class structure...")

    # Verificar classe existe
    assert TestRunner is not None, "TestRunner class not found"
    print("  ✓ TestRunner class found")

    # Verificar __init__
    assert hasattr(TestRunner, '__init__'), "Missing __init__ method"
    print("  ✓ __init__ method found")

    # Verificar métodos obrigatórios
    required_methods = [
        'run_tests',
        '_load_test_cases',
        '_get_default_test_cases',
        '_run_single_test',
        '_build_agent_prompt',
        '_simulate_agent_response'
    ]

    for method_name in required_methods:
        assert hasattr(TestRunner, method_name), f"Missing method: {method_name}"
        method = getattr(TestRunner, method_name)
        assert callable(method), f"Method {method_name} is not callable"
        print(f"  ✓ {method_name} method found")

    return True


def check_method_signatures():
    """Valida assinaturas dos métodos"""
    print("\nChecking method signatures...")

    # run_tests
    sig = inspect.signature(TestRunner.run_tests)
    params = list(sig.parameters.keys())
    assert 'self' in params, "run_tests missing self"
    assert 'agent_version_id' in params, "run_tests missing agent_version_id"
    assert inspect.iscoroutinefunction(TestRunner.run_tests), "run_tests should be async"
    print("  ✓ run_tests signature correct")

    # _run_single_test
    sig = inspect.signature(TestRunner._run_single_test)
    params = list(sig.parameters.keys())
    assert 'self' in params, "_run_single_test missing self"
    assert 'agent' in params, "_run_single_test missing agent"
    assert 'test_case' in params, "_run_single_test missing test_case"
    assert inspect.iscoroutinefunction(TestRunner._run_single_test), "_run_single_test should be async"
    print("  ✓ _run_single_test signature correct")

    # _simulate_agent_response
    sig = inspect.signature(TestRunner._simulate_agent_response)
    params = list(sig.parameters.keys())
    assert 'self' in params, "_simulate_agent_response missing self"
    assert 'system_prompt' in params, "_simulate_agent_response missing system_prompt"
    assert 'user_message' in params, "_simulate_agent_response missing user_message"
    assert inspect.iscoroutinefunction(TestRunner._simulate_agent_response), "_simulate_agent_response should be async"
    print("  ✓ _simulate_agent_response signature correct")

    return True


def check_default_test_cases():
    """Valida test cases padrão"""
    print("\nChecking DEFAULT_SDR_TEST_CASES...")

    assert isinstance(DEFAULT_SDR_TEST_CASES, list), "DEFAULT_SDR_TEST_CASES should be a list"
    assert len(DEFAULT_SDR_TEST_CASES) > 0, "DEFAULT_SDR_TEST_CASES is empty"
    print(f"  ✓ {len(DEFAULT_SDR_TEST_CASES)} test cases found")

    # Verificar estrutura de cada test case
    required_fields = ['name', 'input', 'expected_behavior', 'rubric_focus', 'category']
    for i, test_case in enumerate(DEFAULT_SDR_TEST_CASES):
        assert isinstance(test_case, dict), f"Test case {i} is not a dict"
        for field in required_fields:
            assert field in test_case, f"Test case {i} missing field: {field}"
        print(f"  ✓ Test case {i+1}: {test_case['name']}")

    return True


def check_evaluator_integration():
    """Valida integração com Evaluator"""
    print("\nChecking Evaluator integration...")

    # Verificar Evaluator tem método evaluate
    assert hasattr(Evaluator, 'evaluate'), "Evaluator missing evaluate method"
    assert inspect.iscoroutinefunction(Evaluator.evaluate), "evaluate should be async"
    print("  ✓ Evaluator.evaluate method found")

    # Verificar assinatura
    sig = inspect.signature(Evaluator.evaluate)
    params = list(sig.parameters.keys())
    assert 'agent' in params, "evaluate missing agent param"
    assert 'test_results' in params, "evaluate missing test_results param"
    print("  ✓ Evaluator.evaluate signature correct")

    return True


def check_report_generator_integration():
    """Valida integração com ReportGenerator"""
    print("\nChecking ReportGenerator integration...")

    # Verificar ReportGenerator tem método generate_html_report
    assert hasattr(ReportGenerator, 'generate_html_report'), "ReportGenerator missing generate_html_report method"
    assert inspect.iscoroutinefunction(ReportGenerator.generate_html_report), "generate_html_report should be async"
    print("  ✓ ReportGenerator.generate_html_report method found")

    # Verificar assinatura
    sig = inspect.signature(ReportGenerator.generate_html_report)
    params = list(sig.parameters.keys())
    assert 'agent' in params, "generate_html_report missing agent param"
    assert 'evaluation' in params, "generate_html_report missing evaluation param"
    assert 'test_results' in params, "generate_html_report missing test_results param"
    print("  ✓ ReportGenerator.generate_html_report signature correct")

    return True


def check_initialization():
    """Valida inicialização do TestRunner"""
    print("\nChecking TestRunner initialization...")

    try:
        runner = TestRunner(
            supabase_client=None,
            evaluator=None,
            report_generator=None,
            anthropic_api_key="test-key"
        )
        assert runner is not None, "TestRunner instance is None"
        print("  ✓ TestRunner instantiation successful")

        # Verificar atributos
        assert hasattr(runner, 'supabase'), "Missing supabase attribute"
        assert hasattr(runner, 'evaluator'), "Missing evaluator attribute"
        assert hasattr(runner, 'reporter'), "Missing reporter attribute"
        assert hasattr(runner, 'anthropic_client'), "Missing anthropic_client attribute"
        print("  ✓ All required attributes present")

    except Exception as e:
        print(f"  ✗ Initialization failed: {e}")
        return False

    return True


def check_documentation():
    """Valida documentação"""
    print("\nChecking documentation...")

    # Verificar docstrings
    assert TestRunner.__doc__ is not None, "TestRunner missing docstring"
    assert TestRunner.run_tests.__doc__ is not None, "run_tests missing docstring"
    assert TestRunner._run_single_test.__doc__ is not None, "_run_single_test missing docstring"
    print("  ✓ Docstrings present")

    # Verificar arquivos de documentação
    doc_files = [
        'TEST_RUNNER_GUIDE.md',
        'HANDOFF.md'
    ]

    for doc_file in doc_files:
        path = Path(__file__).parent / doc_file
        if path.exists():
            print(f"  ✓ {doc_file} found")
        else:
            print(f"  ⚠ {doc_file} not found")

    return True


def main():
    """Run all validations"""

    print("\n" + "="*60)
    print(" TEST_RUNNER.PY VALIDATION SUITE")
    print("="*60 + "\n")

    checks = [
        ("Class Structure", check_class_structure),
        ("Method Signatures", check_method_signatures),
        ("Default Test Cases", check_default_test_cases),
        ("Evaluator Integration", check_evaluator_integration),
        ("ReportGenerator Integration", check_report_generator_integration),
        ("Initialization", check_initialization),
        ("Documentation", check_documentation),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  ✗ {name} failed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print(" VALIDATION SUMMARY")
    print("="*60 + "\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\n{passed}/{total} checks passed")

    if passed == total:
        print("\n✓ All validations passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} validation(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
