"""
EvaluationManager – Baseline Implementation
Sequence diagram traceability:
  startEvaluation()
  submitScore(score)        ← called by Reviewer (loop [each reviewer])
  saveScore(score)          → Database
  calculateAverage()
  checkConsensus()
  applyRules()
  → alt [accepted]  notifyAcceptance()  → NotificationService
  → alt [rejected]  notifyRejection()   → NotificationService
  → alt [revision]  notifyRevision()    → NotificationService
"""

from database import Database
from notification_service import NotificationService


class EvaluationManager:
    """
    Orchestrates the evaluation phase.
    Corresponds to 'EvaluationManager' lifeline in the baseline sequence diagram.

    NOTE (Baseline): EvaluationManager conflates score aggregation,
    consensus checking, rule application AND notification dispatch –
    a high-coupling design flaw captured faithfully.
    """

    ACCEPTANCE_THRESHOLD = 7.0    # Average score >= this → accepted
    REJECTION_THRESHOLD  = 4.0    # Average score <  this → rejected
    CONSENSUS_TOLERANCE  = 2.0    # Max allowed std-dev for consensus

    def __init__(self, database: Database, notification_service: NotificationService):
        self._db = database
        self._notif = notification_service
        self._scores: list[float] = []

    # ------------------------------------------------------------------ #
    #  startEvaluation()                                                   #
    # ------------------------------------------------------------------ #
    def start_evaluation(self, submission_id: str) -> None:
        """startEvaluation() from sequence diagram."""
        self._submission_id = submission_id
        self._scores = []

    # ------------------------------------------------------------------ #
    #  submitScore(score) – called per reviewer in loop                   #
    # ------------------------------------------------------------------ #
    def submit_score(self, reviewer_id: str, score: float) -> None:
        """
        submitScore(score) from sequence diagram.
        Reviewer calls this → EvaluationManager saves to DB and stores locally.
        """
        # saveScore(score) → Database
        self._db.save_score(self._submission_id, reviewer_id, score)
        self._scores.append(score)

    # ------------------------------------------------------------------ #
    #  calculateAverage()                                                  #
    # ------------------------------------------------------------------ #
    def calculate_average(self) -> float:
        """calculateAverage() from sequence diagram."""
        if not self._scores:
            return 0.0
        return sum(self._scores) / len(self._scores)

    # ------------------------------------------------------------------ #
    #  checkConsensus()                                                    #
    # ------------------------------------------------------------------ #
    def check_consensus(self) -> bool:
        """
        checkConsensus() from sequence diagram.
        Returns True if reviewers are in sufficient agreement.
        """
        if len(self._scores) < 2:
            return True
        mean = self.calculate_average()
        variance = sum((s - mean) ** 2 for s in self._scores) / len(self._scores)
        std_dev = variance ** 0.5
        return std_dev <= self.CONSENSUS_TOLERANCE

    # ------------------------------------------------------------------ #
    #  applyRules() → outcome                                              #
    # ------------------------------------------------------------------ #
    def apply_rules(self) -> str:
        """
        applyRules() from sequence diagram.
        Determines outcome based on average score.
        Returns 'accepted', 'rejected', or 'revision'.
        """
        average = self.calculate_average()
        if average >= self.ACCEPTANCE_THRESHOLD:
            return "accepted"
        elif average < self.REJECTION_THRESHOLD:
            return "rejected"
        else:
            return "revision"

    # ------------------------------------------------------------------ #
    #  Notification dispatch (alt block from sequence diagram)             #
    # ------------------------------------------------------------------ #
    def dispatch_outcome(self, outcome: str, researcher_email: str) -> None:
        """
        alt [accepted] → notifyAcceptance()
        alt [rejected] → notifyRejection()
        alt [revision] → notifyRevision()
        All route through NotificationService.
        """
        if outcome == "accepted":
            self._notif.notify_acceptance(researcher_email, self._submission_id)
        elif outcome == "rejected":
            self._notif.notify_rejection(researcher_email, self._submission_id)
        elif outcome == "revision":
            self._notif.notify_revision(researcher_email, self._submission_id)
        else:
            raise ValueError(f"Unknown outcome: {outcome}")

    # ------------------------------------------------------------------ #
    #  Full evaluation pipeline (called by SubmissionController)           #
    # ------------------------------------------------------------------ #
    def run_evaluation(self, submission_id: str, reviewers: list,
                       researcher_email: str) -> str:
        """
        Orchestrates the complete evaluation phase as shown in the
        sequence diagram after reviewer assignment.
        """
        self.start_evaluation(submission_id)

        # loop [each reviewer] → submitScore(score)
        for reviewer in reviewers:
            score = reviewer.get("score", 0.0)
            self.submit_score(reviewer["id"], score)

        # Post-loop aggregation
        self.calculate_average()
        self.check_consensus()
        outcome = self.apply_rules()

        # Update DB and dispatch notification
        self._db.update_submission_status(submission_id, "evaluated", outcome)
        self.dispatch_outcome(outcome, researcher_email)

        return outcome
