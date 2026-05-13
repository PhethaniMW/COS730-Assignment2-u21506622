"""
Submission – Optimised Domain Model
A rich domain object that encapsulates submission state and self-validates.
Eliminates the need for scattered validation calls across controllers.
"""

import uuid
import time
from dataclasses import dataclass, field
from enum import Enum


class SubmissionStatus(Enum):
    PENDING    = "pending"
    VALIDATED  = "validated"
    UNDER_REVIEW = "under_review"
    EVALUATED  = "evaluated"


class SubmissionOutcome(Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REVISION = "revision"
    PENDING  = "pending"


@dataclass
class Submission:
    """
    Rich domain object encapsulating all submission data and state.
    Optimised design: state lives here, not spread across the controller.
    """
    title:        str
    abstract:     str
    author:       str
    author_id:    str
    content:      str
    file_format:  str
    email:        str
    submission_id: str          = field(default_factory=lambda: f"SUB-{uuid.uuid4().hex[:8].upper()}")
    timestamp:    float         = field(default_factory=time.time)
    status:       SubmissionStatus  = SubmissionStatus.PENDING
    outcome:      SubmissionOutcome = SubmissionOutcome.PENDING
    scores:       list[float]   = field(default_factory=list)
    reviewer_ids: list[str]     = field(default_factory=list)

    # ------------------------------------------------------------------ #
    #  Validation (in the domain object – high cohesion)                  #
    # ------------------------------------------------------------------ #
    REQUIRED_FIELDS   = ("title", "abstract", "author", "author_id", "content", "file_format", "email")
    ALLOWED_FORMATS   = {"pdf", "docx", "tex"}
    MAX_ABSTRACT_WORDS = 300

    def validate(self) -> tuple[bool, str]:
        """Single validation entry-point – no separate Validator class needed."""
        if not self.title.strip():
            return False, "Title must not be empty"
        if not self.author.strip():
            return False, "Author must not be empty"
        if self.file_format.lower() not in self.ALLOWED_FORMATS:
            return False, f"Unsupported format: {self.file_format}"
        words = len(self.abstract.split())
        if words > self.MAX_ABSTRACT_WORDS:
            return False, f"Abstract too long ({words} words, max {self.MAX_ABSTRACT_WORDS})"
        return True, "valid"

    # ------------------------------------------------------------------ #
    #  Score aggregation (belongs to the Submission, not EvaluationManager)
    # ------------------------------------------------------------------ #
    def add_score(self, reviewer_id: str, score: float) -> None:
        self.scores.append(score)
        if reviewer_id not in self.reviewer_ids:
            self.reviewer_ids.append(reviewer_id)

    def average_score(self) -> float:
        return sum(self.scores) / len(self.scores) if self.scores else 0.0

    def has_consensus(self, tolerance: float = 2.0) -> bool:
        if len(self.scores) < 2:
            return True
        mean = self.average_score()
        variance = sum((s - mean) ** 2 for s in self.scores) / len(self.scores)
        return variance ** 0.5 <= tolerance
