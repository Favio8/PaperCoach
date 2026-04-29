class PaperCoachError(Exception):
    """Base application exception."""


class NotFoundError(PaperCoachError):
    """Raised when a paper or session cannot be found."""


class ValidationError(PaperCoachError):
    """Raised when a request is structurally valid but not acceptable."""
