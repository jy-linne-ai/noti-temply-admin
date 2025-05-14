"""템플릿 아이템"""

from enum import Enum


class TemplateItems(str, Enum):
    """템플릿 아이템"""

    HTML_EMAIL = "HTML_EMAIL"
    TEXT_EMAIL = "TEXT_EMAIL"
    TEXT_WEBPUSH = "TEXT_WEBPUSH"
    TEXT_EMAIL_SUBJECT = "TEXT_EMAIL_SUBJECT"
    TEXT_WEBPUSH_TITLE = "TEXT_WEBPUSH_TITLE"
    TEXT_WEBPUSH_URL = "TEXT_WEBPUSH_URL"
