"""Booking reference generation.

Six characters from an alphabet with the ambiguous glyphs removed — no 0/O,
1/I or 5/S — because this is a code a human reads off a screen and types back in,
or reads aloud over a phone.
"""

import secrets

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
LENGTH = 6

# 32**6 ≈ 1.07 billion. Collisions are vanishingly unlikely at this scale, but
# `reference` is UNIQUE, so the insert is still retried rather than trusted.
MAX_ATTEMPTS = 5


def generate_reference() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(LENGTH))
