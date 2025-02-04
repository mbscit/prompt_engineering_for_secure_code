from enum import Enum


class UsageEnumeration(Enum):
    DISCOURAGED = "Discouraged"
    PROHIBITED = "Prohibited"
    ALLOWED = "Allowed"
    ALLOWED_WITH_REVIEW = "Allowed-with-Review"
