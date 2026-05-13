"""
SubmissionController & UI – Baseline Implementation
Sequence diagram traceability:
  Researcher -> UI: submitResearchOutput(data)
  UI -> SubmissionController: submit(data)
  SubmissionController-> Validator: validateFormat(data)
  alt [invalid] <- return error
  [valid]
    SubmissionController -> Database: saveSubmission(data)-> confirmation
    SubmissionController -> ReviewerManager: getAvailableReviewers()
    loop [assign reviewers]-> assignReview()
    SubmissionController-> EvaluationManager: startEvaluation()
    sendNotification() -> Researcher
"""

import time
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from validator import Validator
from database import Database
from reviewer_manager import ReviewerManager
from evaluation_manager import EvaluationManager
from notification_service import NotificationService


class UI:
    """
    Thin UI layer.
    Corresponds to the 'UI' lifeline in the baseline sequence diagram.
    Receives submitResearchOutput(data) from Researcher.
    """

    def __init__(self, controller: "SubmissionController"):
        self._controller = controller

    def submit_research_output(self, data: dict) -> dict:
        """
        submitResearchOutput(data) from sequence diagram.
        Researcher interacts with this entry point.
        Delegates to SubmissionController.submit(data).
        """
        return self._controller.submit(data)


class SubmissionController:
    """
    Central orchestrator in the baseline design.
    Corresponds to 'SubmissionController' lifeline in the baseline sequence diagram.

    NOTE (Baseline): The controller handles validation orchestration,
    DB coordination, reviewer assignment AND evaluation triggering –
    violating Single Responsibility (design flaw captured faithfully).
    """

    def __init__(self):
        self._validator          = Validator()
        self._database           = Database()
        self._notification_svc   = NotificationService()
        self._reviewer_manager   = ReviewerManager(self._database)
        self._evaluation_manager = EvaluationManager(self._database, self._notification_svc)

    # ------------------------------------------------------------------ #
    #  submit(data) – main flow                                            #
    # ------------------------------------------------------------------ #
    def submit(self, data: dict) -> dict:
        """
        submit(data) from sequence diagram.
        Full orchestration of the submission workflow.
        """
        call_log: list[str] = []   # Track method calls for empirical analysis

        # ── validateFormat(data) ──────────────────────────────────────── #
        call_log.append("Validator.validate_format()")
        is_valid, reason = self._validator.validate_format(data)

        # alt [invalid] → return error
        if not is_valid:
            call_log.append("UI.return_error()")
            return {"success": False, "error": reason, "call_log": call_log}

        # ── [valid] ──────────────────────────────────────────────────── #

        # saveSubmission(data) -> confirmation
        call_log.append("Database.save_submission()")
        submission_id = self._database.save_submission(data)
        call_log.append("Database.confirmation()")

        # getAvailableReviewers()-> ReviewerManager
        call_log.append("ReviewerManager.get_available_reviewers()")
        # ReviewerManager -> Database: fetchReviewers()
        call_log.append("Database.fetch_reviewers()")
        # ReviewerManager -> Reviewer: filterConflicts()
        call_log.append("ReviewerFilterHelper.filter_conflicts()")
        # ReviewerManager -> Reviewer: checkWorkload()
        call_log.append("ReviewerFilterHelper.check_workload()")
        filtered_reviewers = self._reviewer_manager.get_available_reviewers(
            submission_id, data.get("author_id", "")
        )
        call_log.append("ReviewerManager.filteredReviewers -> SubmissionController")

        # loop [assign reviewers] ->assignReview()
        call_log.append("SubmissionController.loop_assign_reviewers()")
        for r in filtered_reviewers[:3]:
            call_log.append(f"ReviewerManager.assignReview({r['id']})")
        assigned = self._reviewer_manager.assign_reviewers(filtered_reviewers)

        # Simulate reviewer scoring (each reviewer submits a score)
        for reviewer in assigned:
            # In production this would be async; here we simulate inline
            reviewer["score"] = self._simulate_reviewer_score(reviewer)

        # startEvaluation() -> EvaluationManager
        call_log.append("EvaluationManager.start_evaluation()")
        self._evaluation_manager.start_evaluation(submission_id)

        # loop [each reviewer] submitScore -> saveScore -> Database
        for reviewer in assigned:
            call_log.append(f"Reviewer.submitScore({reviewer['id']})")
            call_log.append(f"Database.save_score({reviewer['id']})")
            self._evaluation_manager.submit_score(reviewer["id"], reviewer["score"])

        # calculateAverage -> checkConsensus-> applyRules
        call_log.append("EvaluationManager.calculate_average()")
        average = self._evaluation_manager.calculate_average()
        call_log.append("EvaluationManager.check_consensus()")
        consensus = self._evaluation_manager.check_consensus()
        call_log.append("EvaluationManager.apply_rules()")
        outcome = self._evaluation_manager.apply_rules()

        # alt block-> dispatch notification
        call_log.append(f"EvaluationManager.dispatch_outcome({outcome})")
        call_log.append(f"NotificationService.notify_{outcome}()")
        self._evaluation_manager.dispatch_outcome(outcome, data.get("email", ""))

        # sendNotification() -> Researcher (final)
        call_log.append("NotificationService.send_notification()-> Researcher")

        self._database.update_submission_status(submission_id, "evaluated", outcome)

        return {
            "success": True,
            "submission_id": submission_id,
            "outcome": outcome,
            "average_score": round(average, 2),
            "consensus": consensus,
            "assigned_reviewers": [r["id"] for r in assigned],
            "call_log": call_log,
        }

    @staticmethod
    def _simulate_reviewer_score(reviewer: dict) -> float:
        """Deterministic score simulation based on reviewer workload (for benchmarking)."""
        import hashlib
        seed = int(hashlib.md5(reviewer["id"].encode()).hexdigest(), 16) % 100
        return round(4.0 + (seed % 60) / 10.0, 1)  # score in [4.0, 9.9]
