from abc import ABC, abstractmethod
import logging

logger = logging.getLogger("kace.infrastructure.email")


class EmailProvider(ABC):
    """Abstract base for email providers."""

    @abstractmethod
    def send(self, to: str, subject: str, text_body: str, html_body: str = None) -> bool:
        """
        Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            text_body: Plain text fallback
            html_body: Optional HTML content

        Returns: True if sent successfully, False otherwise
        """
        pass
