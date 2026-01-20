class InvalidSimilarityDocument(Exception):
    """Exception raised when a similarity document is invalid."""

    def __init__(self, document_id: str):
        self.message = f"Invalid similarity document: {document_id}"
        super().__init__(self.message)
