# 📊 REFLECTION LOOP - VISUAL ARCHITECTURE

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI FACTORY v4 - Testing Framework           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐       ┌──────────────────┐
│  Agent Version   │       │  Test Runner     │
│   (Supabase)     │──────▶│  (test_runner)   │
└──────────────────┘       └──────────────────┘
                                    │
                                    │ runs tests
                                    ▼
                          ┌──────────────────┐
                          │  Evaluator       │
                          │ (Claude Opus)    │
                          │ LLM-as-Judge     │
                          └──────────────────┘
                                    │
                         scores: {completeness, tone,
                         engagement, compliance, conversion}
                                    │
                                    ▼
                          ┌──────────────────┐
                          │  Test Result     │
                          │  overall_score   │
                          │  weaknesses      │
                          │  failures        │
                          └──────────────────┘
                                    │
                                    │ score < 8.0?
                                    │
                          ┌─────────▼──────────┐
                          │ Reflection Loop ⭐ │
                          │                    │
                          │  AUTO-IMPROVEMENT  │
                          └────────────────────┘
```

---

## Reflection Loop - Detailed Flow

```
START: Agent Score < 8.0
│
├─ Step 1: should_reflect()
│  ├─ Check: min_score (6.0)?
│  │  └─ Too low → MANUAL REVIEW NEEDED
│  ├─ Check: max_score (8.0)?
│  │  └─ Already approved → SKIP
│  └─ Range [6.0, 8.0)? → PROCEED ✅
│
├─ Step 2: generate_improved_prompt()
│  ├─ Extract from test_result:
│  │  ├─ Weaknesses (what failed?)
│  │  ├─ Failures (specific issues)
│  │  ├─ Recommendations (next steps)
│  │  └─ Scores (5 dimensions)
│  │
│  ├─ Call Claude Opus with REFLECTION_PROMPT
│  │  └─ Input: current_prompt + analysis
│  │
│  └─ Claude returns JSON:
│     ├─ improved_prompt (new v2 prompt)
│     ├─ changes_summary (what changed)
│     ├─ expected_improvements (delta/dimension)
│     └─ risk_assessment (Baixo/Médio/Alto)
│
├─ Step 3: create_new_version()
│  ├─ Copy original agent
│  ├─ New version: v{n}.{decimal}-reflection
│  ├─ Update system_prompt with improved version
│  ├─ Status: pending_approval (NOT active)
│  ├─ Add metadata:
│  │  ├─ parent_version_id
│  │  ├─ original_score
│  │  ├─ changes_summary
│  │  ├─ expected_improvements
│  │  └─ risk_assessment
│  └─ Save to Supabase
│
├─ Step 4: auto_test? (optional)
│  │
│  ├─ Yes:
│  │  ├─ run_tests(new_agent_id)
│  │  ├─ Get new_score
│  │  ├─ Calculate improvement = new_score - original_score
│  │  │
│  │  ├─ If new_score >= 8.0:
│  │  │  └─ status = 'ready_for_approval' ✅
│  │  ├─ Else if new_score > original_score:
│  │  │  └─ status = 'improved_pending_approval' ⚠️
│  │  └─ Else:
│  │     └─ status = 'no_improvement' ❌
│  │
│  └─ No:
│     └─ status = 'pending_approval'
│        (Admin decides)
│
└─ END: Return result dict
```

---

## Data Flow - Detailed

```
┌─────────────────────────────────────────────────────────────────┐
│ Input: Test Result                                              │
├─────────────────────────────────────────────────────────────────┤
│ {                                                               │
│   overall_score: 7.2,                                           │
│   test_details: {                                               │
│     scores: {                                                   │
│       completeness: 7.0,      ← Weak point!                    │
│       tone: 8.5,              ← Good                            │
│       engagement: 6.5,        ← Weak point!                    │
│       compliance: 8.0,        ← Good                            │
│       conversion: 6.0         ← Weak point!                    │
│     },                                                          │
│     weaknesses: [             ← INPUT TO REFLECTION             │
│       "Missing BANT qualification",                             │
│       "Weak engagement techniques",                             │
│       "No clear next steps"                                     │
│     ],                                                          │
│     failures: [               ← INPUT TO REFLECTION             │
│       "Failed to qualify budget",                               │
│       "Lead dropped off mid-conversation"                       │
│     ],                                                          │
│     recommendations: [        ← INPUT TO REFLECTION             │
│       "Add structured BANT questions",                          │
│       "Use more open-ended questions",                          │
│       "Define clear next steps in closing"                      │
│     ]                                                           │
│   }                                                             │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ PROCESS
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Claude Opus Analysis (REFLECTION_PROMPT)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ System: "You are a prompt engineering expert..."               │
│                                                                 │
│ Input weaknesses → Claude analyzes                             │
│ Input current_prompt → Claude refactors                        │
│ Input scores → Claude focuses on low dimensions                │
│                                                                 │
│ Claude reasoning:                                              │
│ - Completeness 7.0: Missing BANT                              │
│   → Add 4 structured questions (Budget, Authority, Need, Time) │
│ - Engagement 6.5: Generic approach                             │
│   → Use more open-ended Q's + active listening                │
│ - Conversion 6.0: No clear closing                             │
│   → Define next steps + call-to-action                        │
│                                                                 │
│ Claude output:                                                 │
│ {                                                              │
│   "improved_prompt": "...new full prompt v2...",              │
│   "changes_summary": [                                         │
│     "Added 4-step BANT qualification framework",               │
│     "Enhanced engagement with open-ended questions",           │
│     "Added clear next step definition in closing"              │
│   ],                                                           │
│   "expected_improvements": {                                   │
│     "completeness": "+1.5",   ← 7.0 → 8.5                     │
│     "tone": "+0.0",           ← 8.5 → 8.5 (maintain)          │
│     "engagement": "+1.0",     ← 6.5 → 7.5                     │
│     "compliance": "+0.0",     ← 8.0 → 8.0 (maintain)          │
│     "conversion": "+1.0"      ← 6.0 → 7.0                     │
│   },                                                           │
│   "risk_assessment": "Baixo"  ← Low risk changes              │
│ }                                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ PROCESS
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ New Agent Version Created (Supabase)                            │
├─────────────────────────────────────────────────────────────────┤
│ {                                                               │
│   id: "550e8400-e29b-41d4-a716-446655440001",                 │
│   version: "v1.1-reflection",    ← New version number          │
│   system_prompt: "...improved prompt...",                      │
│   status: "pending_approval",    ← Requires approval           │
│   is_active: false,              ← NOT active yet              │
│   validation_result: {                                         │
│     reflection_source: "auto_improvement",                     │
│     parent_version_id: "550e8400-e29b-41d4-a716...",         │
│     original_score: 7.2,                                       │
│     changes_summary: [...],                                    │
│     expected_improvements: {...},                              │
│     risk_assessment: "Baixo",                                  │
│     generated_at: "2025-12-31T12:00:00Z"                      │
│   }                                                             │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘
                           │
                      auto_test?
                           │
        ┌──────────────────┴──────────────────┐
        │ YES                                 │ NO
        ▼                                     ▼
┌────────────────────┐               ┌──────────────────┐
│ Test v2            │               │ Await Approval   │
│                    │               │                  │
│ run_tests()        │               │ Admin reviews    │
│ ↓                  │               │ in Dashboard     │
│ new_score = 8.4    │               │ ↓                │
│ improvement = +1.2 │               │ Approve/Reject   │
│ ↓                  │               │ ↓                │
│ Status update:     │               │ status = 'active'│
│ ready_for_approval │               └──────────────────┘
│ or improved        │
│ or no_improvement  │
└────────────────────┘
```

---

## Class Structure

```python
class ReflectionLoop:
    """
    ┌────────────────────────────────────────┐
    │        ReflectionLoop                  │
    ├────────────────────────────────────────┤
    │ Properties:                            │
    │  - api_key: str                        │
    │  - client: Anthropic                   │
    │  - model: str (claude-opus-4)          │
    │  - supabase: SupabaseClient            │
    │                                        │
    │ REFLECTION_PROMPT: str (static)        │
    │  └─ Engineered for auto-improvement    │
    │                                        │
    │ Methods:                               │
    │  + should_reflect()                    │
    │  + generate_improved_prompt()          │
    │  + create_new_version()                │
    │  + run_reflection()                    │
    │  + _parse_reflection_response()        │
    │                                        │
    │ Returns: Dict with result              │
    │  - status                              │
    │  - new_agent_id                        │
    │  - improvement                         │
    │  - risk_assessment                     │
    └────────────────────────────────────────┘
    """
```

---

## Integration Points

```
┌──────────────────┐
│  Test Runner     │ Executes tests
└────────┬─────────┘
         │
         │ test_result
         │ {
         │   overall_score: 7.2,
         │   weaknesses: [...],
         │   failures: [...]
         │ }
         ▼
┌──────────────────────────────┐
│   Reflection Loop  ⭐        │ Analyzes + improves
├──────────────────────────────┤
│ generate_improved_prompt()   │──▶ Claude Opus
│ create_new_version()         │──▶ Supabase
│ run_reflection()             │
└──────────────────────────────┘
         │
         │ new_agent
         │ {
         │   id: "uuid",
         │   status: "pending_approval"
         │ }
         ▼
┌──────────────────────────────┐
│   Dashboard / Approval       │ Human review
├──────────────────────────────┤
│ Show pending versions        │
│ Compare v1 vs v2             │
│ Approve / Reject             │
│ Or auto-test first           │
└──────────────────────────────┘
```

---

## Success Scenario

```
AGENT v1.0: score 7.2 ⚠️
    │
    ├─ Weaknesses identified:
    │  - BANT qualification incomplete
    │  - Weak engagement
    │  - No clear closing
    │
    ├─ REFLECTION LOOP ⭐
    │  └─ Claude improves prompt
    │
    ├─ AGENT v1.1-reflection created
    │  ├─ status: pending_approval
    │  └─ expected_improvement: +1.2
    │
    ├─ AUTO-TEST (if enabled)
    │  └─ new_score: 8.4 ✅
    │
    └─ APPROVED
       └─ Now active as v1.1-reflection ✅
```

---

## Failure Scenarios & Recovery

```
Scenario 1: Score too low (< 6.0)
│
├─ Reason: Structural issues
├─ Action: SKIP reflection
└─ Next: Manual review required


Scenario 2: v2 score no better
│
├─ Reason: Rubric issue or already optimized
├─ Action: Create v2, status='no_improvement'
└─ Next: Different approach needed


Scenario 3: Claude API fails
│
├─ Reason: Rate limit, timeout, etc
├─ Action: Exception with context
└─ Next: Retry or manual intervention


Scenario 4: Supabase unavailable
│
├─ Reason: Network, auth, schema
├─ Action: Error log + fail gracefully
└─ Next: Check connection + retry
```

---

## Key Metrics & KPIs

```
┌─────────────────────────────┐
│ Reflection Loop Metrics     │
├─────────────────────────────┤
│                             │
│ Total Reflections Run: N    │
│ ├─ Successful: 85%          │
│ ├─ Skipped: 10%             │
│ └─ Failed: 5%               │
│                             │
│ Average Improvement: +0.8   │
│ ├─ Completeness: +1.2       │
│ ├─ Engagement: +0.7         │
│ ├─ Conversion: +0.5         │
│ └─ Other: +0.2              │
│                             │
│ Risk Assessment:            │
│ ├─ Baixo: 70%               │
│ ├─ Médio: 25%               │
│ └─ Alto: 5%                 │
│                             │
│ Approval Rate: 92%          │
│                             │
└─────────────────────────────┘
```

---

## Deployment Checklist

- [ ] Syntax check: `python -m py_compile src/reflection_loop.py`
- [ ] Imports working: `from src.reflection_loop import ReflectionLoop`
- [ ] Test file runs: `python test_reflection.py --help`
- [ ] Supabase schema ready: migrations applied
- [ ] Claude API key set: `ANTHROPIC_API_KEY`
- [ ] Logging configured: `/logs/framework.log`
- [ ] Error handling tested: all edge cases
- [ ] Documentation complete: this file + usage guide
- [ ] Dashboard ready: shows pending versions
- [ ] N8N webhook configured: (optional)
- [ ] Monitoring setup: metrics collection
- [ ] Rollout plan: staging → production

---

*Diagram Version 1.0 - AI Factory v4 - Reflection Loop*
*Created: 2025-12-31*
