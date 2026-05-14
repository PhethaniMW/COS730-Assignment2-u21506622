"""
ReviewerManager – Baseline Implementation
Sequence diagram traceability:
  getAvailableReviewers()          → filteredReviewers
  filterConflicts(reviewerList)    (internal call from ReviewerManager to itself/Reviewer)
  checkWorkload(reviewerList)      (internal call)
  assignReview()                   → to each Reviewer (loop)
"""

from database import Database


class ReviewerManager:
    """
    Responsible for fetching, filtering, and assigning reviewers.
    Corresponds to 'ReviewerManager' lifeline in the baseline sequence diagram.

    NOTE (Baseline): The diagram shows ReviewerManager delegating
    filterConflicts and checkWorkload to a separate Reviewer object,
    which is a design flaw captured faithfully here.
    """

    MAX_WORKLOAD = 3          # Maximum active reviews per reviewer

    def __init__(self, database: Database):
        self._db = database
        self._assigned_reviewers: list = []

    # ------------------------------------------------------------------ #
    #  getAvailableReviewers() → filteredReviewers                         #
    # ------------------------------------------------------------------ #
    def get_available_reviewers(self, submission_id: str, author_id: str) -> list:
        """
        getAvailableReviewers() from sequence diagram.
        Orchestrates fetchReviewers → filterConflicts → checkWorkload.
        Returns filteredReviewers list.
        """
        # Step 1 – fetch from DB (diagram arrow: ReviewerManager → Database)
        reviewer_list = self._db.fetch_reviewers()

        # Step 2 – delegate conflict filtering to Reviewer helper
        #          (diagram arrow: ReviewerManager → Reviewer: filterConflicts)
        reviewer_filter = ReviewerFilterHelper()
        reviewer_list = reviewer_filter.filter_conflicts(reviewer_list, submission_id, author_id)

        # Step 3 – delegate workload check to Reviewer helper
        #          (diagram arrow: ReviewerManager → Reviewer: checkWorkload)
        reviewer_list = reviewer_filter.check_workload(reviewer_list, self.MAX_WORKLOAD)

        return reviewer_list

    # ------------------------------------------------------------------ #
    #  assignReview() loop                                                 #
    # ------------------------------------------------------------------ #
    def assign_reviewers(self, filtered_reviewers: list, max_reviewers: int = 3) -> list:
        """
        loop [assign reviewers] → assignReview() from sequence diagram.
        Returns the list of assigned reviewer objects.
        """
        selected = filtered_reviewers[:max_reviewers]
        for reviewer in selected:
            reviewer["workload"] += 1   # Increment workload upon assignment
        self._assigned_reviewers = selected
        return selected

    def get_assigned_reviewers(self) -> list:
        return self._assigned_reviewers


class ReviewerFilterHelper:
    """
    Represents the 'Reviewer' lifeline in the baseline diagram that receives
    filterConflicts and checkWorkload calls from ReviewerManager.

    NOTE: Placing filtering logic here is a responsibility misallocation –
    identified as a design flaw in Task 2 analysis.
    """

    def filter_conflicts(self, reviewer_list: list, submission_id: str, author_id: str) -> list:
        """
        filterConflicts(reviewerList) from sequence diagram.
        Removes reviewers who have a conflict with this submission/author.
        """
        return [
            r for r in reviewer_list
            if submission_id not in r.get("conflicts", [])
            and author_id not in r.get("conflicts", [])
        ]

    def check_workload(self, reviewer_list: list, max_workload: int) -> list:
        """
        checkWorkload(reviewerList) from sequence diagram.
        Removes reviewers whose current workload exceeds the threshold.
        """
        return [r for r in reviewer_list if r.get("workload", 0) < max_workload]
