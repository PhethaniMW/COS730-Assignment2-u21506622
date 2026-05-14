# COS730 Assignment 2
**#U21506622**
**From Behavioural Models to Optimised Implementation**

## Repository Structure

```
├── Original/               # Task 1 — Baseline implementation
│   ├── submission_controller.py   (SubmissionController + UI)
│   ├── validator.py               (Validator lifeline)
│   ├── database.py                (Database lifeline)
│   ├── reviewer_manager.py        (ReviewerManager + Reviewer lifelines)
│   ├── evaluation_manager.py      (EvaluationManager lifeline)
│   ├── notification_service.py    (NotificationService lifeline)
│   ├── main.py                    (Entry point + benchmarking)
│   └── README.md
│
├── Optimised/              # Tasks 4 & 5 — Redesigned implementation
│   ├── submission.py              (Domain entity with validation + scoring)
│   ├── decision_engine.py         (Decision table implementation)
│   ├── repository.py              (SubmissionRepository + ReviewerRepository)
│   ├── notification_service.py    (Unified notification dispatch)
│   ├── submission_service.py      (Thin orchestrator + benchmarking)
│   └── README.md
│
└── report/
    ├── COS730_Assignment2_Report.pdf   (Full technical report, 15 pages)
    ├── empirical_results.json          (Raw benchmark data)
    ├── empirical_comparison.py         (Benchmark runner)
    └── report_generator.py             (PDF generator)
```

## Quick Start

```bash
# Run baseline
cd Original && python main.py

# Run optimised
cd Optimised && python submission_service.py
```

## Summary of Results

| Metric | Baseline | Optimised | Improvement |
|---|---|---|---|
| Method calls/run | 25 | 10 | 60%  |
| Mean execution time | 0.0398 ms | 0.0269 ms | 32.4% |
| Timing std deviation | 0.2627 ms | 0.0098 ms | 96.3% |
| Source lines | 695 | 456 | 34.4% |
| Method count | 36 | 22 | 38.9% |
| Decision logic locations | 3 | 1 | 67% |
