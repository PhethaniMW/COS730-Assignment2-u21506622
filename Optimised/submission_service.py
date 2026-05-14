"""
SubmissionService – Optimised Implementation
Replaces the overloaded SubmissionController + UI pair from the baseline.

Optimised design principles applied:
  1. Validation moved into the Submission domain object (high cohesion).
  2. Filtering consolidated into DecisionEngine (single-pass, no delegation).
  3. Score aggregation belongs to the Submission object.
  4. Notification dispatched via single send() call.
  5. Repository pattern separates persistence concerns.
  6. Controller is thin – only orchestrates, never decides.
"""

import sys
import os
import time
import hashlib

sys.path.insert(0, os.path.dirname(__file__))

from submission import Submission, SubmissionStatus, SubmissionOutcome
from repository import SubmissionRepository, ReviewerRepository
from decision_engine import DecisionEngine
from notification_service import NotificationService


class SubmissionService:
    """
    Thin orchestrator – coordinates objects, makes no decisions itself.
    Decisions delegated entirely to DecisionEngine.
    """

    def __init__(self):
        self._sub_repo      = SubmissionRepository()
        self._rev_repo      = ReviewerRepository()
        self._engine        = DecisionEngine()
        self._notif         = NotificationService()

    # ------------------------------------------------------------------ #
    #  process(data) – optimised main flow                                 #
    # ------------------------------------------------------------------ #
    def process(self, data: dict) -> dict:
        """
        Streamlined workflow – fewer interactions, cleaner control flow.
        """
        call_log: list[str] = []

        # ① Build domain object & validate (no separate Validator class)
        submission = Submission(**{k: data[k] for k in Submission.__dataclass_fields__ if k in data})
        call_log.append("Submission.validate()")
        is_valid, reason = submission.validate()
        if not is_valid:
            call_log.append("return error")
            return {"success": False, "error": reason, "call_log": call_log}

        # ② Persist
        call_log.append("SubmissionRepository.save()")
        self._sub_repo.save(submission)

        # ③ Single-pass reviewer filtering (conflict + workload in one call)
        all_reviewers = self._rev_repo.find_all()
        call_log.append("ReviewerRepository.find_all()")
        call_log.append("DecisionEngine.filter_reviewers()")
        filtered = self._engine.filter_reviewers(all_reviewers, submission.submission_id, submission.author_id)
        call_log.append("DecisionEngine.select_reviewers()")
        assigned = self._engine.select_reviewers(filtered)

        # ④ Score collection (loop)
        for reviewer in assigned:
            self._rev_repo.increment_workload(reviewer["id"])
            score = self._simulate_score(reviewer)
            call_log.append(f"submission.add_score({reviewer['id']})")
            submission.add_score(reviewer["id"], score)

        # ⑤ Determine outcome via decision table
        avg = submission.average_score()
        consensus = submission.has_consensus()
        call_log.append("DecisionEngine.determine_outcome()")
        outcome, matched_rule = self._engine.determine_outcome(avg, consensus)

        # ⑥ Single notification call
        call_log.append("NotificationService.send()")
        self._notif.send(submission.email, submission.submission_id, outcome)

        # ⑦ Persist outcome
        self._sub_repo.update_outcome(submission.submission_id, outcome)

        return {
            "success": True,
            "submission_id": submission.submission_id,
            "outcome": outcome,
            "matched_rule": matched_rule.name,
            "average_score": round(avg, 2),
            "consensus": consensus,
            "assigned_reviewers": [r["id"] for r in assigned],
            "call_log": call_log,
        }

    @staticmethod
    def _simulate_score(reviewer: dict) -> float:
        """Identical scoring logic to baseline for fair empirical comparison."""
        seed = int(hashlib.md5(reviewer["id"].encode()).hexdigest(), 16) % 100
        return round(4.0 + (seed % 60) / 10.0, 1)


def benchmark(n: int = 100) -> dict:
    valid_data = {
        "title": "Deep Learning for Code Smell Detection",
        "abstract": "This paper presents a deep learning approach to detecting code smells.",
        "author": "Jane Researcher",
        "author_id": "A999",
        "content": "Full paper content goes here...",
        "file_format": "pdf",
        "email": "jane@example.com",
    }

    service = SubmissionService()
    times = []
    call_counts = []

    for _ in range(n):
        start = time.perf_counter()
        result = service.process(valid_data)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        call_counts.append(len(result.get("call_log", [])))

    avg_time  = sum(times) / len(times)
    avg_calls = sum(call_counts) / len(call_counts)

    return {
        "runs": n,
        "avg_time_ms": round(avg_time * 1000, 4),
        "min_time_ms": round(min(times) * 1000, 4),
        "max_time_ms": round(max(times) * 1000, 4),
        "total_time_s": round(sum(times), 4),
        "avg_method_calls": round(avg_calls, 1),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("  OPTIMISED SYSTEM – Single Submission Demo")
    print("=" * 60)

    sample = {
        "title": "Adaptive Neural Networks for Software Fault Localisation",
        "abstract": "We propose an adaptive neural network framework for fault localisation.",
        "author": "Alice Dlamini",
        "author_id": "A001_test",
        "content": "Lorem ipsum body content...",
        "file_format": "pdf",
        "email": "alice@cs.up.ac.za",
    }

    service = SubmissionService()
    result = service.process(sample)

    print(f"\nSubmission ID  : {result.get('submission_id', 'N/A')}")
    print(f"Outcome        : {result.get('outcome', result.get('error', 'N/A')).upper()}")
    print(f"Matched Rule   : {result.get('matched_rule', 'N/A')}")
    print(f"Average Score  : {result.get('average_score', 'N/A')}")
    print(f"Consensus      : {result.get('consensus', 'N/A')}")
    print(f"Reviewers      : {result.get('assigned_reviewers', [])}")
    print(f"\nMethod Call Log ({len(result.get('call_log', []))} calls):")
    for i, call in enumerate(result.get("call_log", []), 1):
        print(f"  {i:02d}. {call}")

    print("\n" + "=" * 60)
    print("  BENCHMARKING (100 runs)")
    print("=" * 60)
    stats = benchmark(100)
    for k, v in stats.items():
        print(f"  {k:<25}: {v}")
