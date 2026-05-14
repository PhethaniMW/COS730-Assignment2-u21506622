"""
NotificationService – Optimised Implementation
Interface unchanged for functional equivalence.
Optimisation: outcome-to-message mapping eliminates the
three separate notifyX() methods – replaced with a single dispatch.
"""

import time


class NotificationService:
    """
    Lean notification service.  Single public method; message templates
    are data, not methods.
    """

    _TEMPLATES: dict[str, tuple[str, str]] = {
        "accepted": (
            "Submission Accepted",
            "Congratulations! Your submission '{sid}' has been ACCEPTED. "
            "You will receive further instructions from the programme committee.",
        ),
        "rejected": (
            "Submission Rejected",
            "We regret to inform you that submission '{sid}' has been REJECTED. "
            "Reviewer feedback will be shared with you shortly.",
        ),
        "revision": (
            "Revision Required",
            "Your submission '{sid}' requires MAJOR REVISION. "
            "Please address reviewer comments and resubmit within 30 days.",
        ),
    }

    def __init__(self):
        self._log: list[dict] = []

    def send(self, email: str, submission_id: str, outcome: str) -> None:
        """
        Single unified notification dispatch.
        Replaces notifyAcceptance() + notifyRejection() + notifyRevision()
        from the baseline design.
        """
        subject, body_template = self._TEMPLATES[outcome]
        body = body_template.format(sid=submission_id)
        entry = {"to": email, "subject": subject, "body": body,
                 "outcome": outcome, "timestamp": time.time()}
        self._log.append(entry)
        print(f"[NotificationService] → {email}: {subject}")

    def get_log(self) -> list[dict]:
        return list(self._log)
