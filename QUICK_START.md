# Quick Start Guide - AI Factory V4 Test Runner

Get up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- Anthropic API key
- (Optional) Supabase credentials

## 1. Setup (2 min)

```bash
# Clone/navigate to project
cd ai-factory-testing-framework

# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

## 2. Run Offline Test (2 min)

Test without Supabase:

```bash
python test_offline.py
```

Expected output: Agent evaluation with score 8.0+

## 3. Run Comprehensive Demo (1 min)

See all features working:

```bash
python test_runner_comprehensive.py
```

This runs 4 complete tests showing all capabilities.

## 4. Validate Installation (1 min)

Verify everything is set up correctly:

```bash
python validate_test_runner.py
```

Expected: `7/7 checks passed ✅`

## 5. Use in Your Code (3 min)

```python
import asyncio
from src.test_runner import run_quick_test

async def main():
    result = await run_quick_test(
        agent_version_id="mock-agent-001"
    )
    print(f"Score: {result['overall_score']:.1f}/10")
    print(f"Report: {result['report_url']}")

asyncio.run(main())
```

## Quick Facts

- **Agent Simulation**: Local with Claude Sonnet
- **Evaluation**: LLM-as-Judge with Claude Opus
- **Reports**: Beautiful HTML with Tailwind CSS
- **Test Cases**: 10 default SDR scenarios
- **Score Ranges**: 0-10 (8.0+ = approved)
- **Async**: Full async/await support

## Files to Know

- `src/test_runner.py` - Main orchestrator
- `test_offline.py` - Quick demo
- `TEST_RUNNER_GUIDE.md` - Full documentation
- `./reports/` - Generated reports location

## Troubleshooting

```bash
# API key missing?
export ANTHROPIC_API_KEY='sk-ant-...'

# Missing modules?
pip install -r requirements.txt

# Want to see everything?
python test_runner_comprehensive.py
```

## Score Interpretation

- **8.0+**: ✅ APPROVED (production ready)
- **6.0-7.9**: ⚠️ NEEDS IMPROVEMENT (review weaknesses)
- **<6.0**: ❌ FAILED (significant rework needed)

## Next Steps

1. Read `COMPLETION_REPORT.md` for full status
2. Read `TEST_RUNNER_GUIDE.md` for detailed docs
3. Test your own agent with Supabase credentials
4. Use reflection loop for auto-improvement

---

✅ Ready to test! Run `python test_offline.py` now!
