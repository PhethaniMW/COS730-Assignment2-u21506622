"""
main.py – Baseline System Entry Point
Demonstrates the complete submission workflow as specified in the sequence diagram.
"""

import time
from submission_controller import SubmissionController, UI


def run_submission(data: dict) -> dict:
    """Execute one full submission through the baseline system."""
    controller = SubmissionController()
    ui = UI(controller)
    return ui.submit_research_output(data)


def benchmark(n: int = 100) -> dict:
    """
    Run n submissions and return timing statistics.
    Used for Task 6 empirical evaluation.
    """
    valid_data = {
        "title": "Deep Learning for Code Smell Detection",
        "abstract": "This paper presents a deep learning approach to detecting code smells.",
        "author": "Jane Researcher",
        "author_id": "A999",
        "content": "Full paper content goes here...",
        "file_format": "pdf",
        "email": "jane@example.com",
    }

    times = []
    call_counts = []

    for _ in range(n):
        start = time.perf_counter()
        result = run_submission(valid_data)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        call_counts.append(len(result.get("call_log", [])))

    avg_time   = sum(times) / len(times)
    avg_calls  = sum(call_counts) / len(call_counts)
    total_time = sum(times)

    return {
        "runs": n,
        "avg_time_ms": round(avg_time * 1000, 4),
        "min_time_ms": round(min(times) * 1000, 4),
        "max_time_ms": round(max(times) * 1000, 4),
        "total_time_s": round(total_time, 4),
        "avg_method_calls": round(avg_calls, 1),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("  BASELINE SYSTEM – Single Submission Demo")
    print("=" * 60)

    sample = {
        "title": "Adaptive Neural Networks for Software Fault Localisation",
        "abstract": "We propose an adaptive neural network framework for fault localisation in large-scale systems.",
        "author": "Alice Dlamini",
        "author_id": "A001_test",
        "content": "Lorem ipsum body content...",
        "file_format": "pdf",
        "email": "alice@cs.up.ac.za",
    }

    result = run_submission(sample)

    print(f"\nSubmission ID : {result.get('submission_id', 'N/A')}")
    print(f"Outcome       : {result.get('outcome', result.get('error', 'N/A')).upper()}")
    print(f"Average Score : {result.get('average_score', 'N/A')}")
    print(f"Consensus     : {result.get('consensus', 'N/A')}")
    print(f"Reviewers     : {result.get('assigned_reviewers', [])}")
    print(f"\nMethod Call Log ({len(result.get('call_log', []))} calls):")
    for i, call in enumerate(result.get("call_log", []), 1):
        print(f"  {i:02d}. {call}")

    print("\n" + "=" * 60)
    print("  BENCHMARKING (100 runs)")
    print("=" * 60)
    stats = benchmark(100)
    for k, v in stats.items():
        print(f"  {k:<25}: {v}")
