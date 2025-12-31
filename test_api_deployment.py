#!/usr/bin/env python3
"""
API Deployment Validation Script
================================
Tests all endpoints to ensure production deployment is working correctly.

Usage:
    python test_api_deployment.py https://your-railway-app.railway.app
    python test_api_deployment.py http://localhost:8000
"""

import sys
import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Tuple
import httpx
from collections import defaultdict


class APITester:
    """Test API endpoints and collect metrics."""

    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize tester with base URL."""
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        self.results: List[Dict] = []
        self.metrics: Dict[str, List[float]] = defaultdict(list)

    def test_health_check(self) -> bool:
        """Test health check endpoint."""
        print("\n[TEST] Health Check Endpoint")
        print("-" * 50)

        try:
            start = time.time()
            response = self.client.get(f"{self.base_url}/health")
            duration = (time.time() - start) * 1000

            self.metrics['health_check'].append(duration)

            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status Code: {response.status_code}")
                print(f"✓ Response Time: {duration:.2f}ms")
                print(f"✓ Status: {data.get('status')}")
                print(f"✓ Database: {data.get('database')}")
                print(f"✓ Version: {data.get('version')}")

                self.results.append({
                    'endpoint': '/health',
                    'status': 'PASS',
                    'response_time_ms': duration
                })
                return True
            else:
                print(f"✗ Status Code: {response.status_code}")
                print(f"✗ Response: {response.text}")
                self.results.append({
                    'endpoint': '/health',
                    'status': 'FAIL',
                    'error': f"Status {response.status_code}"
                })
                return False

        except Exception as e:
            print(f"✗ Error: {e}")
            self.results.append({
                'endpoint': '/health',
                'status': 'ERROR',
                'error': str(e)
            })
            return False

    def test_ping(self) -> bool:
        """Test ping endpoint."""
        print("\n[TEST] Ping Endpoint")
        print("-" * 50)

        try:
            start = time.time()
            response = self.client.get(f"{self.base_url}/ping")
            duration = (time.time() - start) * 1000

            self.metrics['ping'].append(duration)

            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status Code: {response.status_code}")
                print(f"✓ Response Time: {duration:.2f}ms")
                print(f"✓ Message: {data.get('message')}")

                self.results.append({
                    'endpoint': '/ping',
                    'status': 'PASS',
                    'response_time_ms': duration
                })
                return True
            else:
                print(f"✗ Status Code: {response.status_code}")
                self.results.append({
                    'endpoint': '/ping',
                    'status': 'FAIL',
                    'error': f"Status {response.status_code}"
                })
                return False

        except Exception as e:
            print(f"✗ Error: {e}")
            self.results.append({
                'endpoint': '/ping',
                'status': 'ERROR',
                'error': str(e)
            })
            return False

    def test_single_test_run(self) -> bool:
        """Test single test run endpoint."""
        print("\n[TEST] Single Test Run Endpoint")
        print("-" * 50)

        payload = {
            "agent_id": "test-agent-001",
            "test_name": "Deployment Test",
            "input_text": "Oi",
            "expected_behavior": "Friendly greeting",
            "rubric_focus": ["tone", "engagement"]
        }

        try:
            start = time.time()
            response = self.client.post(
                f"{self.base_url}/api/v1/test/run",
                json=payload
            )
            duration = (time.time() - start) * 1000

            self.metrics['test_run'].append(duration)

            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status Code: {response.status_code}")
                print(f"✓ Response Time: {duration:.2f}ms")
                print(f"✓ Test ID: {data.get('test_id')}")
                print(f"✓ Status: {data.get('status')}")
                print(f"✓ Score: {data.get('score')}")

                self.results.append({
                    'endpoint': '/api/v1/test/run',
                    'status': 'PASS',
                    'response_time_ms': duration
                })
                return True
            else:
                print(f"✗ Status Code: {response.status_code}")
                print(f"✗ Response: {response.text[:200]}")
                self.results.append({
                    'endpoint': '/api/v1/test/run',
                    'status': 'FAIL',
                    'error': f"Status {response.status_code}"
                })
                return False

        except Exception as e:
            print(f"✗ Error: {e}")
            self.results.append({
                'endpoint': '/api/v1/test/run',
                'status': 'ERROR',
                'error': str(e)
            })
            return False

    def test_batch_submission(self) -> bool:
        """Test batch test submission."""
        print("\n[TEST] Batch Test Submission")
        print("-" * 50)

        payload = {
            "agent_id": "test-agent-001",
            "test_cases": [
                {
                    "test_name": "Test 1",
                    "input_text": "Oi",
                    "expected_behavior": "Friendly greeting",
                    "rubric_focus": ["tone"]
                },
                {
                    "test_name": "Test 2",
                    "input_text": "Quanto custa?",
                    "expected_behavior": "Anchor value before price",
                    "rubric_focus": ["compliance"]
                }
            ]
        }

        try:
            start = time.time()
            response = self.client.post(
                f"{self.base_url}/api/v1/test/batch",
                json=payload
            )
            duration = (time.time() - start) * 1000

            self.metrics['batch_submit'].append(duration)

            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status Code: {response.status_code}")
                print(f"✓ Response Time: {duration:.2f}ms")
                print(f"✓ Run ID: {data.get('run_id')}")
                print(f"✓ Test Count: {data.get('test_count')}")
                print(f"✓ Status: {data.get('status')}")

                self.results.append({
                    'endpoint': '/api/v1/test/batch',
                    'status': 'PASS',
                    'response_time_ms': duration
                })
                return True
            else:
                print(f"✗ Status Code: {response.status_code}")
                self.results.append({
                    'endpoint': '/api/v1/test/batch',
                    'status': 'FAIL',
                    'error': f"Status {response.status_code}"
                })
                return False

        except Exception as e:
            print(f"✗ Error: {e}")
            self.results.append({
                'endpoint': '/api/v1/test/batch',
                'status': 'ERROR',
                'error': str(e)
            })
            return False

    def test_agent_results(self) -> bool:
        """Test getting agent results."""
        print("\n[TEST] Get Agent Results")
        print("-" * 50)

        try:
            start = time.time()
            response = self.client.get(
                f"{self.base_url}/api/v1/agents/test-agent-001/results?limit=5"
            )
            duration = (time.time() - start) * 1000

            self.metrics['agent_results'].append(duration)

            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status Code: {response.status_code}")
                print(f"✓ Response Time: {duration:.2f}ms")
                print(f"✓ Results Count: {data.get('count', 0)}")

                self.results.append({
                    'endpoint': '/api/v1/agents/{id}/results',
                    'status': 'PASS',
                    'response_time_ms': duration
                })
                return True
            else:
                print(f"✗ Status Code: {response.status_code}")
                self.results.append({
                    'endpoint': '/api/v1/agents/{id}/results',
                    'status': 'FAIL',
                    'error': f"Status {response.status_code}"
                })
                return False

        except Exception as e:
            print(f"✗ Error: {e}")
            self.results.append({
                'endpoint': '/api/v1/agents/{id}/results',
                'status': 'ERROR',
                'error': str(e)
            })
            return False

    def test_metrics(self) -> bool:
        """Test getting metrics."""
        print("\n[TEST] Get Metrics")
        print("-" * 50)

        try:
            start = time.time()
            response = self.client.get(f"{self.base_url}/api/v1/metrics")
            duration = (time.time() - start) * 1000

            self.metrics['metrics'].append(duration)

            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status Code: {response.status_code}")
                print(f"✓ Response Time: {duration:.2f}ms")
                print(f"✓ Timestamp: {data.get('timestamp')}")

                self.results.append({
                    'endpoint': '/api/v1/metrics',
                    'status': 'PASS',
                    'response_time_ms': duration
                })
                return True
            else:
                print(f"✗ Status Code: {response.status_code}")
                self.results.append({
                    'endpoint': '/api/v1/metrics',
                    'status': 'FAIL',
                    'error': f"Status {response.status_code}"
                })
                return False

        except Exception as e:
            print(f"✗ Error: {e}")
            self.results.append({
                'endpoint': '/api/v1/metrics',
                'status': 'ERROR',
                'error': str(e)
            })
            return False

    def run_all_tests(self) -> bool:
        """Run all tests."""
        print("\n" + "=" * 50)
        print("  AI FACTORY API - DEPLOYMENT TEST SUITE")
        print("=" * 50)
        print(f"\nTesting: {self.base_url}")
        print(f"Started: {datetime.now().isoformat()}")

        tests = [
            self.test_ping,
            self.test_health_check,
            self.test_agent_results,
            self.test_metrics,
            self.test_single_test_run,
            self.test_batch_submission,
        ]

        results = [test() for test in tests]

        return all(results)

    def print_summary(self) -> None:
        """Print test summary."""
        print("\n" + "=" * 50)
        print("  TEST SUMMARY")
        print("=" * 50)

        # Results by status
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        errors = sum(1 for r in self.results if r['status'] == 'ERROR')

        print(f"\nTotal Tests: {len(self.results)}")
        print(f"✓ Passed: {passed}")
        print(f"✗ Failed: {failed}")
        print(f"⚠ Errors: {errors}")

        # Performance metrics
        print(f"\n{'Endpoint':<40} {'Avg (ms)':<12} {'Min (ms)':<12} {'Max (ms)':<12}")
        print("-" * 80)

        for endpoint, times in sorted(self.metrics.items()):
            if times:
                avg = statistics.mean(times)
                min_time = min(times)
                max_time = max(times)
                print(f"{endpoint:<40} {avg:<12.2f} {min_time:<12.2f} {max_time:<12.2f}")

        # Overall status
        print("\n" + "=" * 50)
        if failed == 0 and errors == 0:
            print("✓ DEPLOYMENT VALIDATION SUCCESSFUL")
            return True
        else:
            print("✗ DEPLOYMENT VALIDATION FAILED")
            return False

    def close(self) -> None:
        """Close HTTP client."""
        self.client.close()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python test_api_deployment.py <base_url>")
        print("\nExample:")
        print("  python test_api_deployment.py https://your-app.railway.app")
        print("  python test_api_deployment.py http://localhost:8000")
        sys.exit(1)

    base_url = sys.argv[1]

    tester = APITester(base_url)
    try:
        success = tester.run_all_tests()
        tester.print_summary()
        sys.exit(0 if success else 1)
    finally:
        tester.close()


if __name__ == "__main__":
    main()
