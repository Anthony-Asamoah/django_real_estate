import json
import urllib.parse
import urllib.request

from django.conf import settings


def verify(token: str, action: str) -> bool:
    secret = getattr(settings, "RECAPTCHA_SECRET_KEY", "")
    if not secret:
        return True
    data = urllib.parse.urlencode({"secret": secret, "response": token}).encode()
    try:
        with urllib.request.urlopen(
            "https://www.google.com/recaptcha/api/siteverify", data=data, timeout=5
        ) as resp:
            result = json.loads(resp.read())
    except Exception:
        return False
    threshold = getattr(settings, "RECAPTCHA_SCORE_THRESHOLD", 0.5)
    return (
        result.get("success") is True
        and result.get("action") == action
        and result.get("score", 0) >= threshold
    )
