# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_golden.json
- Mode: llm
- Records: 40
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.8 | 0.9 | 0.1 |
| Avg attempts | 1 | 1.3 | 0.3 |
| Avg token estimate | 840.45 | 1344.65 | 504.2 |
| Avg latency (ms) | 10627.1 | 14370.5 | 3743.4 |

## Failure modes
```json
{
  "react": {
    "none": 16,
    "wrong_final_answer": 4
  },
  "reflexion": {
    "none": 18,
    "wrong_final_answer": 2
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json
- mock_mode_for_autograding

## Discussion
Reflexion helps when the first attempt stops after the first hop or drifts to a wrong second-hop entity. The tradeoff is higher attempts, token cost, and latency. In a real report, students should explain when the reflection memory was useful, which failure modes remained, and whether evaluator quality limited gains.
