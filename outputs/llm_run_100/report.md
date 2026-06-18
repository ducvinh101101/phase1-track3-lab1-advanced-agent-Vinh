# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_100.json
- Mode: llm
- Records: 100
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.38 | 0.6 | 0.22 |
| Avg attempts | 1 | 2.14 | 1.14 |
| Avg token estimate | 1274.8 | 3690.32 | 2415.52 |
| Avg latency (ms) | 12150.58 | 35549.82 | 23399.24 |

## Failure modes
```json
{
  "react": {
    "none": 19,
    "wrong_final_answer": 31
  },
  "reflexion": {
    "none": 30,
    "wrong_final_answer": 20
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
