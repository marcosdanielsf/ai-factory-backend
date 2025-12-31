/**
 * k6 Performance Test Script for AI Factory API
 * ==============================================
 * Tests the API under load to measure performance metrics.
 *
 * Installation:
 *   brew install k6  (macOS)
 *   choco install k6 (Windows)
 *
 * Usage:
 *   k6 run performance-test.js
 *   k6 run performance-test.js --vus 100 --duration 5m
 *   k6 run performance-test.js --stage 10s:50 --stage 30s:100 --stage 10s:0
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';

// Configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const AGENT_ID = __ENV.AGENT_ID || 'test-agent-001';

// Custom metrics
const errorRate = new Rate('errors');
const healthCheckDuration = new Trend('health_check_duration');
const testRunDuration = new Trend('test_run_duration');
const batchTestDuration = new Trend('batch_test_duration');
const requestCounter = new Counter('requests');
const successRate = new Rate('success');

export const options = {
  // VUs and duration
  vus: 10,
  duration: '1m',

  // Thresholds - performance budgets
  thresholds: {
    'health_check_duration': ['p(95)<200', 'p(99)<500'],
    'test_run_duration': ['p(95)<10000', 'p(99)<30000'],
    'batch_test_duration': ['p(95)<500'],
    'errors': ['rate<0.1'], // Less than 10% error rate
    'http_req_failed': ['rate<0.1'],
    'success': ['rate>0.9'], // More than 90% success rate
  },

  // Stages - ramp up gradually
  stages: [
    { duration: '10s', target: 10 },   // Ramp up to 10 VUs
    { duration: '30s', target: 50 },   // Ramp up to 50 VUs
    { duration: '20s', target: 50 },   // Stay at 50 VUs
    { duration: '10s', target: 0 },    // Ramp down to 0 VUs
  ],
};

/**
 * Health check test
 */
function testHealthCheck() {
  group('Health Checks', () => {
    // Test /health endpoint
    const healthRes = http.get(`${BASE_URL}/health`);
    const duration = healthRes.timings.duration;

    healthCheckDuration.add(duration);
    requestCounter.add(1);

    const healthCheck = check(healthRes, {
      'health endpoint status is 200': (r) => r.status === 200,
      'health endpoint response time < 200ms': (r) => r.timings.duration < 200,
      'health endpoint has database status': (r) =>
        r.json('database') !== null,
    });

    successRate.add(healthCheck);
    errorRate.add(!healthCheck);
    sleep(0.5);

    // Test /ping endpoint
    const pingRes = http.get(`${BASE_URL}/ping`);
    requestCounter.add(1);

    const pingCheck = check(pingRes, {
      'ping endpoint status is 200': (r) => r.status === 200,
      'ping endpoint response < 50ms': (r) => r.timings.duration < 50,
    });

    successRate.add(pingCheck);
    errorRate.add(!pingCheck);
  });
}

/**
 * Single test run
 */
function testSingleTestRun() {
  group('Single Test Run', () => {
    const payload = {
      agent_id: AGENT_ID,
      test_name: 'Load Test - Cold Lead',
      input_text: 'Oi',
      expected_behavior: 'Friendly greeting with open-ended question',
      rubric_focus: ['tone', 'engagement'],
    };

    const res = http.post(`${BASE_URL}/api/v1/test/run`, JSON.stringify(payload), {
      headers: { 'Content-Type': 'application/json' },
    });

    testRunDuration.add(res.timings.duration);
    requestCounter.add(1);

    const testCheck = check(res, {
      'test run status is 200': (r) => r.status === 200,
      'test run response time < 30s': (r) => r.timings.duration < 30000,
      'test run has test_id': (r) => r.json('test_id') !== null,
      'test run has score': (r) => r.json('score') !== null,
    });

    successRate.add(testCheck);
    errorRate.add(!testCheck);
  });
}

/**
 * Batch test submission
 */
function testBatchTestSubmission() {
  group('Batch Test Submission', () => {
    const payload = {
      agent_id: AGENT_ID,
      test_cases: [
        {
          test_name: 'Load Test - Cold Lead',
          input_text: 'Oi',
          expected_behavior: 'Friendly greeting',
          rubric_focus: ['tone'],
        },
        {
          test_name: 'Load Test - Price Question',
          input_text: 'Quanto custa?',
          expected_behavior: 'Anchor value before price',
          rubric_focus: ['compliance'],
        },
      ],
      run_name: 'Performance Test Run',
    };

    const res = http.post(`${BASE_URL}/api/v1/test/batch`, JSON.stringify(payload), {
      headers: { 'Content-Type': 'application/json' },
    });

    batchTestDuration.add(res.timings.duration);
    requestCounter.add(1);

    const batchCheck = check(res, {
      'batch submission status is 200': (r) => r.status === 200,
      'batch submission response time < 500ms': (r) => r.timings.duration < 500,
      'batch submission has run_id': (r) => r.json('run_id') !== null,
      'batch submission has status endpoint': (r) =>
        r.json('status_endpoint') !== null,
    });

    successRate.add(batchCheck);
    errorRate.add(!batchCheck);

    // Store run_id for status check
    if (res.status === 200) {
      const runId = res.json('run_id');
      sleep(1);
      testBatchStatus(runId);
    }
  });
}

/**
 * Check batch test status
 */
function testBatchStatus(runId) {
  const res = http.get(`${BASE_URL}/api/v1/test/status/${runId}`);
  requestCounter.add(1);

  const statusCheck = check(res, {
    'status endpoint status is 200': (r) => r.status === 200,
    'status endpoint has status field': (r) => r.json('status') !== null,
  });

  successRate.add(statusCheck);
  errorRate.add(!statusCheck);
}

/**
 * Get agent results
 */
function testGetAgentResults() {
  group('Agent Results', () => {
    const res = http.get(`${BASE_URL}/api/v1/agents/${AGENT_ID}/results?limit=10`);
    requestCounter.add(1);

    const resultsCheck = check(res, {
      'results endpoint status is 200': (r) => r.status === 200,
      'results endpoint has count': (r) => r.json('count') !== null,
      'results endpoint is array': (r) => Array.isArray(r.json('results')),
    });

    successRate.add(resultsCheck);
    errorRate.add(!resultsCheck);
  });
}

/**
 * Get metrics
 */
function testGetMetrics() {
  group('Metrics', () => {
    const res = http.get(`${BASE_URL}/api/v1/metrics`);
    requestCounter.add(1);

    const metricsCheck = check(res, {
      'metrics endpoint status is 200': (r) => r.status === 200,
      'metrics endpoint has timestamp': (r) => r.json('timestamp') !== null,
      'metrics endpoint has metrics': (r) => r.json('metrics') !== null,
    });

    successRate.add(metricsCheck);
    errorRate.add(!metricsCheck);
  });
}

/**
 * Main test function
 */
export default function () {
  // Run tests in sequence with some randomization
  const testChoice = Math.random();

  if (testChoice < 0.3) {
    testHealthCheck();
  } else if (testChoice < 0.5) {
    testSingleTestRun();
  } else if (testChoice < 0.8) {
    testBatchTestSubmission();
  } else if (testChoice < 0.9) {
    testGetAgentResults();
  } else {
    testGetMetrics();
  }

  sleep(Math.random() * 2);
}

/**
 * Teardown - runs after test completes
 */
export function teardown(data) {
  console.log('=== Performance Test Summary ===');
  console.log(`Total Requests: ${requestCounter.value}`);
  console.log(`Success Rate: ${successRate.value * 100}%`);
  console.log(`Error Rate: ${errorRate.value * 100}%`);
}
