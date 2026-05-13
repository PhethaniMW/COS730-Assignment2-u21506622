"""
Database – Baseline Implementation
Sequence diagram traceability:
  saveSubmission(data)-> confirmation
  fetchReviewers()     -> reviewerList
  saveScore(score)
"""

import uuid
import time
from typing import Optional


class Database:
    """
    Responsible for all persistence operations.
    Corresponds to the 'Database' lifeline in the baseline sequence diagram.
    """

    def __init__(self):
        self._submissions: dict = {}
        self._reviewers: list = self._seed_reviewers()
        self._scores: dict = {}

    # ------------------------------------------------------------------ #
    #  Seed Data                                                           #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _seed_reviewers() -> list:
        return [
            {"id": "R001", "name": "Prof. Dlamini",   "domain": "AI",       "workload": 2, "conflicts": []},
            {"id": "R002", "name": "Dr. Nkosi",        "domain": "SE",       "workload": 3, "conflicts": ["A001"]},
            {"id": "R003", "name": "Prof. Van Wyk",    "domain": "Networks", "workload": 1, "conflicts": []},
            {"id": "R004", "name": "Dr. Mahlangu",     "domain": "AI",       "workload": 4, "conflicts": []},
            {"id": "R005", "name": "Dr. Botha",        "domain": "SE",       "workload": 2, "conflicts": ["A002"]},
            {"id": "R006", "name": "Prof. Sithole",    "domain": "HCI",      "workload": 0, "conflicts": []},
        ]

    # ------------------------------------------------------------------ #
    #  saveSubmission(data) → confirmation                                 #
    # ------------------------------------------------------------------ #
    def save_submission(self, data: dict) -> str:
        """
        saveSubmission(data) from sequence diagram.
        Returns a confirmation/submission ID.
        """
        submission_id = f"SUB-{uuid.uuid4().hex[:8].upper()}"
        self._submissions[submission_id] = {
            **data,
            "submission_id": submission_id,
            "timestamp": time.time(),
            "status": "pending",
        }
        return submission_id

    # ------------------------------------------------------------------ #
    #  fetchReviewers() -> reviewerList                                     #
    # ------------------------------------------------------------------ #
    def fetch_reviewers(self) -> list:
        """
        fetchReviewers() from sequence diagram.
        Returns the full list of reviewers (unfiltered).
        """
        return list(self._reviewers)

    # ------------------------------------------------------------------ #
    #  saveScore(score)                                                    #
    # ------------------------------------------------------------------ #
    def save_score(self, submission_id: str, reviewer_id: str, score: float) -> None:
        """
        saveScore(score) from sequence diagram.
        """
        key = f"{submission_id}:{reviewer_id}"
        self._scores[key] = score

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #
    def get_scores_for_submission(self, submission_id: str) -> list[float]:
        return [
            v for k, v in self._scores.items()
            if k.startswith(f"{submission_id}:")
        ]

    def update_submission_status(self, submission_id: str, status: str, outcome: Optional[str] = None):
        if submission_id in self._submissions:
            self._submissions[submission_id]["status"] = status
            if outcome:
                self._submissions[submission_id]["outcome"] = outcome

    def get_submission(self, submission_id: str) -> Optional[dict]:
        return self._submissions.get(submission_id)
