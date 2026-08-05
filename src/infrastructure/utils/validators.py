import phonenumbers
from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .profanity import contains_profanity

# Tags Quill's toolbar (bold/italic/underline/lists) can produce.
ALLOWED_MESSAGE_TAGS = {'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li'}


def sanitize_message_html(value):
    """Whitelist-sanitize Quill-authored HTML before saving to a RichTextField.

    Wagtail's admin editor parses RichTextField content as strict HTML,
    which requires void elements like <br> to be self-closed. The browser's
    `innerHTML` serialization (what a rich text form submits) emits bare
    <br>, and any disallowed tag (e.g. an injected <script>) would be stored
    verbatim, so content must be parsed and re-serialized through a
    whitelist rather than saved raw.
    """
    soup = BeautifulSoup(value or '', 'html.parser')
    for tag in soup.find_all(True):
        if tag.name not in ALLOWED_MESSAGE_TAGS:
            tag.unwrap()
        else:
            tag.attrs = {}
    return str(soup)


def is_message_blank(sanitized_html):
    """True if sanitized rich text HTML has no visible text (e.g. '<p><br/></p>')."""
    return not BeautifulSoup(sanitized_html or '', 'html.parser').get_text(strip=True)


def validate_message(sanitized_html):
    """Raise ValueError with a user-facing message if sanitized_html is blank or profane."""
    if is_message_blank(sanitized_html):
        raise ValueError('Please enter a message.')
    text = BeautifulSoup(sanitized_html, 'html.parser').get_text(' ', strip=True)
    if contains_profanity(text):
        raise ValueError('Please remove inappropriate language from your message.')


def validate_phone(raw_phone, region='GH'):
    """Return an E.164-formatted phone number, or None if raw_phone is blank.

    Raises ValueError with a user-facing message if raw_phone is non-blank
    but not a valid number.
    """
    if not raw_phone:
        return None
    try:
        parsed = phonenumbers.parse(raw_phone, region)
    except phonenumbers.NumberParseException:
        raise ValueError('Please enter a valid phone number.')
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError('Please enter a valid phone number.')
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)


def validate_contact_email(raw_email):
    """Return a stripped email address, or None if raw_email is blank.

    Raises ValueError with a user-facing message if raw_email is non-blank
    but not a well-formed address.
    """
    raw_email = (raw_email or '').strip()
    if not raw_email:
        return None
    try:
        validate_email(raw_email)
    except ValidationError:
        raise ValueError('Please enter a valid email address.')
    return raw_email
