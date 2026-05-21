import logging

from .provider import EmailProvider, logger


class DjangoSMTPProvider(EmailProvider):
    """Email provider using Django's configured SMTP backend."""

    def send(self, to: str, subject: str, text_body: str, html_body: str = None) -> bool:
        from django.core.mail import send_mail
        try:
            send_mail(
                subject=subject,
                message=text_body,
                from_email=None,  # Uses DEFAULT_FROM_EMAIL
                recipient_list=[to],
                html_message=html_body,
                fail_silently=False,
            )
            logger.info(f"Email sent via SMTP to {to}")
            return True
        except Exception as e:
            logger.error(f"SMTP send failed to {to}: {e}")
            return False


class ResendProvider(EmailProvider):
    """Email provider using the Resend API."""

    def __init__(self, api_key: str = None):
        from django.conf import settings
        self.api_key = api_key or getattr(settings, 'EMAIL_API_KEY', None)
        if not self.api_key:
            raise ValueError("EMAIL_API_KEY is not configured")

    def send(self, to: str, subject: str, text_body: str, html_body: str = None) -> bool:
        from django.conf import settings
        try:
            import requests
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
            payload = {
                "from": from_email,
                "to": to,
                "subject": subject,
                "text": text_body,
            }
            if html_body:
                payload["html"] = html_body

            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            if response.status_code == 200:
                logger.info(f"Email sent via Resend to {to}")
                return True
            logger.error(f"Resend API error ({response.status_code}): {response.text}")
            return False
        except Exception as e:
            logger.error(f"Resend send failed to {to}: {e}")
            return False


def get_email_provider() -> EmailProvider:
    """Return the configured email provider."""
    from django.conf import settings
    provider = getattr(settings, 'EMAIL_PROVIDER', 'django_smtp').lower()
    if provider == 'resend':
        return ResendProvider()
    return DjangoSMTPProvider()
