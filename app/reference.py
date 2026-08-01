"""Booking reference generation.

Six characters from an alphabet with the ambiguous glyphs removed, because this
is a code a human reads off a screen and types back in, or reads aloud over a
phone.

Excluded: 0/O, 1/I, and 5/S.

NOTE: PLAN.md §2 states that exclusion list in prose but then gives a literal
alphabet — "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" — that still contains S and 5.
The two contradict each other. This follows the stated intent rather than the
literal string, since 5/S is exactly the confusion the rule exists to prevent.
"""

import secrets

ALPHABET = "ABCDEFGHJKLMNPQRTUVWXYZ2346789"  # 30 characters
LENGTH = 6

# 30**6 ≈ 729 million. Collisions are vanishingly unlikely at this scale, but
# `reference` is UNIQUE, so the insert is still retried rather than trusted.
MAX_ATTEMPTS = 5


def generate_reference() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(LENGTH))
