"""
DecisionEngine – Optimised Implementation
Implements the decision table from Task 3 as a single, centralised,
rule-based engine.  Replaces scattered applyRules / alt logic.

Decision Table:
┌──────────────────┬───────────┬──────────┬──────────┬──────────────┐
│ Condition        │ Rule 1    │ Rule 2   │ Rule 3   │ Rule 4       │
├──────────────────┼───────────┼──────────┼──────────┼──────────────┤
│ avg ≥ 7.0        │  TRUE     │  FALSE   │  FALSE   │  FALSE       │
│ avg ≥ 4.0        │  -        │  TRUE    │  TRUE    │  FALSE       │
│ consensus        │  -        │  TRUE    │  FALSE   │  -           │
├──────────────────┼───────────┼──────────┼──────────┼──────────────┤
│ Action           │ ACCEPTED  │ ACCEPTED │ REVISION │  REJECTED    │
└──────────────────┴───────────┴──────────┴──────────┴──────────────┘

Additional validation decision table:
┌────────────────────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
│ Condition              │ Rule A  │ Rule B  │ Rule C  │ Rule D  │ Rule E  │
├────────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ Title non-empty        │  TRUE   │  FALSE  │  -      │  -      │  -      │
│ Author non-empty       │  TRUE   │  -      │  FALSE  │  -      │  -      │
│ Format valid           │  TRUE   │  -      │  -      │  FALSE  │  -      │
│ Abstract ≤ 300 words   │  TRUE   │  -      │  -      │  -      │  FALSE  │
├────────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ Action                 │  VALID  │  ERROR  │  ERROR  │  ERROR  │  ERROR  │
└────────────────────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionRule:
    name: str
    description: str


class DecisionEngine:
    """
    Centralised decision logic for both validation and outcome determination.
    Implements the decision tables defined in Task 3.
    """

    # ── Outcome thresholds ────────────────────────────────────────────── #
    ACCEPTANCE_THRESHOLD = 7.0
    REJECTION_THRESHOLD  = 4.0

    # ── Named rules (traceability to decision table) ─────────────────── #
    RULE_1 = DecisionRule("Rule 1", "avg≥7.0 → ACCEPTED (consensus irrelevant)")
    RULE_2 = DecisionRule("Rule 2", "4≤avg<7, consensus=TRUE → ACCEPTED")
    RULE_3 = DecisionRule("Rule 3", "4≤avg<7, consensus=FALSE → REVISION")
    RULE_4 = DecisionRule("Rule 4", "avg<4 → REJECTED")

    # ── Reviewer selection constants ─────────────────────────────────── #
    MAX_WORKLOAD   = 3
    MAX_REVIEWERS  = 3

    # ------------------------------------------------------------------ #
    #  Outcome decision (replaces EvaluationManager.applyRules + alt block)
    # ------------------------------------------------------------------ #
    def determine_outcome(self, average: float, consensus: bool) -> tuple[str, DecisionRule]:
        """
        Apply the decision table to produce a final outcome.
        Returns (outcome_string, matched_rule) for full traceability.
        """
        if average >= self.ACCEPTANCE_THRESHOLD:
            return "accepted", self.RULE_1
        if average >= self.REJECTION_THRESHOLD:
            if consensus:
                return "accepted", self.RULE_2
            return "revision", self.RULE_3
        return "rejected", self.RULE_4

    # ------------------------------------------------------------------ #
    #  Reviewer filtering (replaces scattered filterConflicts+checkWorkload)
    # ------------------------------------------------------------------ #
    def filter_reviewers(self, reviewers: list, submission_id: str, author_id: str) -> list:
        """
        Single-pass filtering: conflict check + workload check.
        Replaces two separate delegated calls in the baseline design.
        """
        return [
            r for r in reviewers
            if submission_id not in r.get("conflicts", [])
            and author_id not in r.get("conflicts", [])
            and r.get("workload", 0) < self.MAX_WORKLOAD
        ]

    def select_reviewers(self, filtered: list) -> list:
        """Cap to MAX_REVIEWERS."""
        return filtered[:self.MAX_REVIEWERS]
