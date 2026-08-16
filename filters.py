"""
filters.py - Skip patterns and scoring logic.
"""

import re

# Listings matching these are skipped entirely
SKIP_PATTERN = re.compile(
    r'ladies|female|women|men\'?s|sober|weekly|/wk|/week|per week|a week|by the week|for \d+ week|weeks|month to month|\d+/wk|\d+ a week',
    re.IGNORECASE
)

# Listings with these words get score 0
BAD_WORDS = re.compile(
    r'shared|living room|futon|couch|trailer|rv |rv\)|parking|sober|homestay|hostel|airbnb|help:|errands|cleaning|general help|backyard',
    re.IGNORECASE
)

# These boost the score
GOOD_WORDS = re.compile(
    r'private|furnished|utilities included|pool|asu|downtown|tempe|scottsdale|chandler|gilbert|walking distance',
    re.IGNORECASE
)


def should_skip(title):
    """Return True if listing should be skipped entirely."""
    return bool(SKIP_PATTERN.search(title))


def score_listing(title, price):
    """Score a listing 0-100. Higher = better."""
    if BAD_WORDS.search(title):
        return 0

    score = 50

    if GOOD_WORDS.search(title):
        score += 20

    if 220 <= price <= 300:
        score += 15
    elif 200 <= price <= 350:
        score += 5
    elif price > 350:
        score -= 10

    if 'private' in title.lower():
        score += 15
    if 'room for rent' in title.lower() and 'shared' not in title.lower():
        score += 10
    if 'blocks from' in title.lower() or 'near' in title.lower():
        score += 5

    return max(0, min(100, score))
