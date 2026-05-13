"""
Validator – Baseline Implementation
Sequence diagram traceability:
  validateFormat(data)-> returns valid/invalid
"""


class Validator:
    """
    Responsible for validating submission format.
    Corresponds to the 'Validator' lifeline in the baseline sequence diagram.
    """

    REQUIRED_FIELDS = {"title", "abstract", "author", "content", "file_format"}
    ALLOWED_FORMATS = {"pdf", "docx", "tex"}
    MAX_ABSTRACT_WORDS = 300

    def validate_format(self, data: dict) -> tuple[bool, str]:
        """
        validateFormat(data) from sequence diagram.
        Returns (is_valid, reason).
        """
        # Check required fields
        missing = self.REQUIRED_FIELDS - data.keys()
        if missing:
            return False, f"Missing required fields: {missing}"

        # Check file format
        if data.get("file_format", "").lower() not in self.ALLOWED_FORMATS:
            return False, f"Unsupported file format: {data.get('file_format')}"

        # Check abstract length (word count)
        abstract_words = len(data.get("abstract", "").split())
        if abstract_words > self.MAX_ABSTRACT_WORDS:
            return False, f"Abstract exceeds {self.MAX_ABSTRACT_WORDS} words ({abstract_words} found)"

        # Check title not empty
        if not data.get("title", "").strip():
            return False, "Title must not be empty"

        # Check author not empty
        if not data.get("author", "").strip():
            return False, "Author must not be empty"

        return True, "valid"
