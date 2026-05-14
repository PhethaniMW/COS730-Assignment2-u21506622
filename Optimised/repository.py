"""
SubmissionRepository – Optimised Implementation
Follows the Repository pattern: single responsibility for persistence.
Replaces the overloaded Database class from the baseline.
"""

import uuid
import time
from typing import Optional
from submission import Submission, SubmissionOutcome


class ReviewerRepository:
    """Responsible only for reviewer data access."""

    def __init__(self):
        self._reviewers: list = self._seed()

    @staticmethod
    def _seed() -> list:
        return [
            {"id": "R001", "name": "Prof. Dlamini",   "domain": "AI",       "workload": 2, "conflicts": []},
            {"id": "R002", "name": "Dr. Nkosi",        "domain": "SE",       "workload": 3, "conflicts": ["A001"]},
            {"id": "R003", "name": "Prof. Van Wyk",    "domain": "Networks", "workload": 1, "conflicts": []},
            {"id": "R004", "name": "Dr. Mahlangu",     "domain": "AI",       "workload": 4, "conflicts": []},
            {"id": "R005", "name": "Dr. Botha",        "domain": "SE",       "workload": 2, "conflicts": ["A002"]},
            {"id": "R006", "name": "Prof. Sithole",    "domain": "HCI",      "workload": 0, "conflicts": []},
        ]

    def find_all(self) -> list:
        return list(self._reviewers)

    def increment_workload(self, reviewer_id: str) -> None:
        for r in self._reviewers:
            if r["id"] == reviewer_id:
                r["workload"] += 1
                return


class SubmissionRepository:
    """Responsible only for submission persistence."""

    def __init__(self):
        self._store: dict[str, Submission] = {}

    def save(self, submission: Submission) -> None:
        self._store[submission.submission_id] = submission

    def find_by_id(self, submission_id: str) -> Optional[Submission]:
        return self._store.get(submission_id)

    def update_outcome(self, submission_id: str, outcome: str) -> None:
        sub = self._store.get(submission_id)
        if sub:
            sub.outcome = SubmissionOutcome(outcome)
