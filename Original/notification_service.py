"""
NotificationService – Baseline Implementation
Sequence diagram traceability:
  notifyAcceptance()
  notifyRejection()
  notifyRevision()
  sendNotification()   ← final call back to Researcher (UI)
"""

import time


class NotificationService:
    """
    Handles dispatching notifications to researchers.
    Corresponds to 'NotificationService' lifeline in the baseline sequence diagram.
    """

    def __init__(self):
        self._log: list[dict] = []

    # ------------------------------------------------------------------ #
    #  notifyAcceptance() – alt [accepted]                                 #
    # ------------------------------------------------------------------ #
    def notify_acceptance(self, email: str, submission_id: str) -> None:
        """notifyAcceptance() → NotificationService from sequence diagram."""
        message = (
            f"Congratulations! Your submission '{submission_id}' has been ACCEPTED. "
            "You will receive further instructions from the programme committee."
        )
        self._send_notification(email, "Submission Accepted", message, "accepted")

    # ------------------------------------------------------------------ #
    #  notifyRejection() – alt [rejected]                                  #
    # ------------------------------------------------------------------ #
    def notify_rejection(self, email: str, submission_id: str) -> None:
        """notifyRejection() → NotificationService from sequence diagram."""
        message = (
            f"We regret to inform you that submission '{submission_id}' has been REJECTED. "
            "Reviewer feedback will be shared with you shortly."
        )
        self._send_notification(email, "Submission Rejected", message, "rejected")

    # ------------------------------------------------------------------ #
    #  notifyRevision() – alt [revision]                                   #
    # ------------------------------------------------------------------ #
    def notify_revision(self, email: str, submission_id: str) -> None:
        """notifyRevision() → NotificationService from sequence diagram."""
        message = (
            f"Your submission '{submission_id}' requires MAJOR REVISION. "
            "Please address reviewer comments and resubmit within 30 days."
        )
        self._send_notification(email, "Revision Required", message, "revision")

    # ------------------------------------------------------------------ #
    #  sendNotification() – final arrow back to Researcher                 #
    # ------------------------------------------------------------------ #
    def _send_notification(self, email: str, subject: str, body: str, outcome: str) -> None:
        """
        sendNotification() from sequence diagram – the final message
        that reaches the Researcher (via UI).
        Simulated here; in production would integrate with an SMTP/push service.
        """
        notification = {
            "to": email,
            "subject": subject,
            "body": body,
            "outcome": outcome,
            "timestamp": time.time(),
        }
        self._log.append(notification)
        # Simulate delivery
        print(f"[NotificationService] → Researcher <{email}>: {subject}")

    def get_log(self) -> list[dict]:
        return list(self._log)
