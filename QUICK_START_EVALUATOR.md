# Quick Start - Evaluator Module

## ⚡ 60-Second Setup

```bash
# 1. Set API key
export ANTHROPIC_API_KEY='sk-ant-api03-...'

# 2. Run test
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework
python test_evaluator.py

# Expected output: 4/4 tests passed ✅
```

## 🚀 5-Minute Integration

```python
from src.evaluator import evaluate_sync

# Your agent data
agent = {
    'name': 'My Agent',
    'system_prompt': 'You are a professional SDR...'
}

# Your test results
test_results = [
    {
        'test_name': 'Qualification test',
        'input': 'User: Hi, I need help',
        'agent_response': 'Agent: Hello! Let me understand your needs...',
        'passed': True
    }
]

# Evaluate
result = evaluate_sync(agent, None, test_results)

# Check score
print(f"Score: {result['overall_score']}/10")
if result['overall_score'] >= 8.0:
    print("✅ APPROVED")
else:
    print("❌ NEEDS IMPROVEMENT")
    print("Weaknesses:", result['weaknesses'])
```

## 📊 Understanding Results

```python
{
  'overall_score': 8.5,        # Weighted average (8.0+ = approved)

  'scores': {                  # Individual dimensions
    'completeness': 8.0,       # BANT coverage (25% weight)
    'tone': 9.5,               # Professional tone (20%)
    'engagement': 9.0,         # Lead engagement (20%)
    'compliance': 9.5,         # Followed instructions (20%)
    'conversion': 7.0          # Achieved goal (15%)
  },

  'strengths': [               # What's working
    'Consultative approach',
    'Good compliance'
  ],

  'weaknesses': [              # What needs improvement
    'Incomplete BANT',
    'Rushed to close'
  ],

  'recommendations': [         # Specific actions
    'Add Timeline questions',
    'Deepen Need discovery'
  ]
}
```

## 🎯 5 Evaluation Dimensions

1. **Completeness (25%)** - BANT complete?
   - Budget discovered?
   - Authority identified?
   - Need understood?
   - Timeline explored?

2. **Tone (20%)** - Professional & consultative?
   - Empathetic language?
   - Not too aggressive?
   - Appropriate formality?

3. **Engagement (20%)** - Lead participated?
   - Asked good questions?
   - Got responses?
   - Conversation flowed?

4. **Compliance (20%)** - Followed instructions?
   - No false promises?
   - Stayed in scope?
   - Followed guardrails?

5. **Conversion (15%)** - Goal achieved?
   - Meeting booked?
   - Lead qualified?
   - Next step clear?

## 💰 Cost Reference

**Per evaluation**: ~$0.09
**Per 100 evaluations**: ~$9

Using Claude Opus 4 (most accurate).
Use Sonnet 4 for cheaper dev testing (~$0.01/eval).

## 🐛 Troubleshooting

### "API key not found"
```bash
export ANTHROPIC_API_KEY='your-key'
```

### "Evaluation failed"
Check:
1. API key valid?
2. Internet connected?
3. Test results format correct?

### "Score always 5.0"
That's the fallback score (error occurred).
Check logs for details.

## 📚 Full Documentation

- `README_EVALUATOR.md` - Complete guide
- `EVALUATOR_COMPLETE.md` - Implementation details
- `HANDOFF.md` - Project context

## 🔗 Key Files

```
src/evaluator.py              # Main implementation
test_evaluator.py             # Test suite
test_evaluation_result.json   # Sample output
```

## ✅ Quick Validation

```bash
# Should see: 4/4 tests passed
python test_evaluator.py
```

---

**Ready to integrate?** See `README_EVALUATOR.md` for advanced usage.

**Need help?** Contact Marcos Daniels (@marcos-daniels)
