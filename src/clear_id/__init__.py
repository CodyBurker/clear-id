"""clear-id: deterministic, memorable phrase digests for arbitrary strings.

Maps any string to an adjective-adjective-noun phrase such as
``brave-crimson-falcon`` by hashing the input with SHA-256 and using the
hash to index frozen word lists. The same input always produces the same
phrase, no word ever repeats within a phrase, and the word lists contain
only common English words a native speaker will recognize.

    >>> from clear_id import phrase_id
    >>> phrase_id("user-8f3a2b")
    'solid-royal-carrier'

See ``collision_probability`` / ``capacity`` for the math on how many
identifiers a namespace can hold before collisions become likely.
"""

from .digest import (
    ADJECTIVES,
    NOUNS,
    capacity,
    collision_probability,
    phrase_id,
    phrase_space,
)

__all__ = [
    "ADJECTIVES",
    "NOUNS",
    "capacity",
    "collision_probability",
    "phrase_id",
    "phrase_space",
]

__version__ = "0.1.0"
