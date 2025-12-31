# Evaluator Module - Complete Implementation

## Overview

The `src/evaluator.py` module is **COMPLETE** and implements the LLM-as-Judge pattern using Claude Opus to evaluate AI agent performance.

## Features

### 1. Evaluator Class
- **Model**: Claude Opus 4.5 (configurable)
- **Method**: `evaluate(agent, skill, test_results)` → returns evaluation dict
- **Temperature**: 0.3 (for consistent evaluation)
- **Max Tokens**: 4000

### 2. Evaluation Rubric (5 Dimensions)

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Completeness** | 25% | BANT complete? (Budget, Authority, Need, Timeline) |
| **Tone** | 20% | Consultative and professional tone? |
| **Engagement** | 20% | Lead engaged in conversation? |
| **Compliance** | 20% | Followed guardrails and instructions? |
| **Conversion** | 15% | Achieved conversion goal (meeting booked, etc)? |

**Approval Threshold**: 8.0/10

### 3. Output Structure

```python
{
  'overall_score': 8.5,  # Weighted average
  'scores': {
    'completeness': 9.0,
    'tone': 8.5,
    'engagement': 8.0,
    'compliance': 9.5,
    'conversion': 7.5
  },
  'test_case_evaluations': [
    {
      'test_name': 'test name',
      'score': 8.5,
      'passed': True,
      'feedback': 'specific feedback'
    }
  ],
  'strengths': ['strength 1', 'strength 2', ...],
  'weaknesses': ['weakness 1', 'weakness 2', ...],
  'failures': ['critical failure 1', ...],
  'warnings': ['warning 1', ...],
  'recommendations': ['recommendation 1', ...]
}
```

## Usage

### Basic Usage

```python
from src.evaluator import Evaluator

# Initialize
evaluator = Evaluator()

# Agent data
agent = {
    'id': 'agent-123',
    'name': 'Isabella SDR',
    'description': 'SDR agent for B2B qualification',
    'system_prompt': 'You are Isabella, a professional SDR...'
}

# Skill (optional, uses default rubric if None)
skill = {
    'name': 'sdr-qualification',
    'rubric': None  # or custom rubric markdown
}

# Test results
test_results = [
    {
        'test_name': 'Lead interested',
        'input': 'Hi, I want to know more',
        'agent_response': 'Hello! I would love to help...',
        'expected_behavior': 'Engage and ask discovery questions',
        'passed': True,
        'execution_time': 2.5
    },
    # ... more test cases
]

# Evaluate
evaluation = evaluator.evaluate(agent, skill, test_results)

print(f"Overall Score: {evaluation['overall_score']}/10")
print(f"Passed: {evaluation['overall_score'] >= 8.0}")
```

### Using the Sync Helper

```python
from src.evaluator import evaluate_sync

result = evaluate_sync(agent, skill, test_results)
```

## Testing

Run the test suite to validate the evaluator:

```bash
# Make sure you have ANTHROPIC_API_KEY set
export ANTHROPIC_API_KEY='sk-ant-api03-...'

# Run tests
python test_evaluator.py
```

The test suite includes:
1. ✓ Basic initialization
2. ✓ Weighted score calculation
3. ✓ Full evaluation with Claude Opus
4. ✓ Threshold check (8.0/10)

## Environment Variables

Required:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

Optional (from config.yaml):
```bash
# Override model (default: claude-opus-4-20250514)
ANTHROPIC_MODEL=claude-opus-4

# Override temperature (default: 0.3)
ANTHROPIC_TEMPERATURE=0.3

# Override max tokens (default: 4000)
ANTHROPIC_MAX_TOKENS=4000
```

## Files

```
ai-factory-testing-framework/
├── src/
│   └── evaluator.py           # Main evaluator implementation (COMPLETE)
├── test_evaluator.py          # Test suite
├── config.yaml                # Configuration
├── requirements.txt           # Dependencies
└── README_EVALUATOR.md        # This file
```

## Implementation Details

### Prompt Engineering

The evaluator uses a structured prompt that includes:
1. **Agent Information**: Name, purpose, system prompt summary
2. **Rubric**: Complete evaluation criteria (5 dimensions)
3. **Test Results**: All test cases with inputs/outputs
4. **Output Format**: JSON schema for structured response

### Error Handling

- **API Failures**: Returns fallback evaluation (5.0 score + error message)
- **JSON Parsing**: Multiple strategies to extract JSON from response
- **Missing Fields**: Validates and fills defaults for all required fields
- **Score Validation**: Recalculates weighted score to ensure consistency

### Rubric Customization

You can provide a custom rubric via the `skill` parameter:

```python
skill = {
    'rubric': """
    ## Custom Evaluation Rubric

    ### 1. CUSTOM_DIMENSION_1 (30%)
    Description...

    ### 2. CUSTOM_DIMENSION_2 (30%)
    Description...

    # ... etc
    """
}
```

The evaluator will use the custom rubric instead of the default BANT-focused one.

### Model Selection

Default: `claude-opus-4-20250514` (Claude Opus 4.5)

Why Opus?
- Best reasoning capabilities for complex evaluation
- More consistent scoring
- Better at following JSON output format
- Worth the extra cost for evaluation quality

For faster/cheaper evaluation during development:
```python
evaluator = Evaluator(model='claude-sonnet-4-20250514')
```

## Next Steps

After evaluator is validated:

1. **Report Generator** (`src/report_generator.py`) - Generate HTML reports
2. **Test Runner** (`src/test_runner.py`) - Complete the test execution
3. **Reflection Loop** (`src/reflection_loop.py`) - Auto-improvement
4. **Integration** - Connect all components

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not found"
**Solution**: Set environment variable
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### Issue: Evaluation returns fallback scores (5.0)
**Solution**: Check:
- API key is valid
- Model name is correct
- Network connection
- Check logs for detailed error

### Issue: JSON parsing fails
**Solution**: The evaluator has fallback parsing strategies. If still failing:
- Check Claude's response in logs
- Verify prompt template is correct
- Try increasing `max_tokens`

## API Cost Estimate

Using Claude Opus 4:
- Input: ~$15 per 1M tokens
- Output: ~$75 per 1M tokens

Typical evaluation:
- Input: ~2,000 tokens (rubric + test cases)
- Output: ~1,000 tokens (evaluation JSON)
- Cost per evaluation: ~$0.09

For 100 evaluations/day: ~$9/day = ~$270/month

**Optimization**: Use Sonnet for development, Opus for production.

## Support

Issues? Check:
1. HANDOFF.md (Section A)
2. Test suite output
3. Logs in `logs/framework.log`

Contact: Marcos Daniels (@marcos-daniels)
