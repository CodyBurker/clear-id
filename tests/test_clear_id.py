import itertools
import math
import random
import subprocess
import sys

import pytest

from clear_id import (
    ADJECTIVES,
    NOUNS,
    capacity,
    collision_probability,
    phrase_id,
    phrase_space,
)


class TestWordLists:
    def test_no_duplicates_within_lists(self):
        assert len(set(ADJECTIVES)) == len(ADJECTIVES)
        assert len(set(NOUNS)) == len(NOUNS)

    def test_lists_disjoint(self):
        assert not set(ADJECTIVES) & set(NOUNS)

    def test_words_are_simple_lowercase(self):
        for word in itertools.chain(ADJECTIVES, NOUNS):
            assert word.isalpha() and word.islower() and 3 <= len(word) <= 10

    def test_list_sizes(self):
        # The collision analysis in the README is computed from these
        # sizes; changing the lists means redoing that table.
        assert len(ADJECTIVES) == 214
        assert len(NOUNS) == 504


class TestPhraseId:
    def test_deterministic(self):
        assert phrase_id("hello world") == phrase_id("hello world")

    def test_known_vectors_are_stable(self):
        # Golden outputs: these must never change for existing inputs, or
        # every previously issued identifier breaks. Any word-list edit is
        # a breaking change and must bump the major version.
        assert phrase_id("hello world") == "devoted-plausible-baron"
        assert phrase_id("") == "modern-loyal-snack"
        assert phrase_id("user@example.com") == "vivid-casual-shampoo"

    def test_bytes_and_str_agree(self):
        assert phrase_id("héllo") == phrase_id("héllo".encode("utf-8"))

    def test_structure(self):
        adj1, adj2, noun = phrase_id("anything").split("-")
        assert adj1 in ADJECTIVES and adj2 in ADJECTIVES
        assert noun in NOUNS

    @pytest.mark.parametrize("adjectives", [1, 2, 3, 4])
    def test_no_repeated_words(self, adjectives):
        for i in range(2000):
            words = phrase_id(f"input-{i}", adjectives=adjectives).split("-")
            assert len(words) == adjectives + 1
            assert len(set(words)) == len(words), words

    def test_separator(self):
        assert " " in phrase_id("x", separator=" ")
        assert phrase_id("x", separator=" ").replace(" ", "-") == phrase_id("x")

    def test_adjective_count_bounds(self):
        with pytest.raises(ValueError):
            phrase_id("x", adjectives=0)
        with pytest.raises(ValueError):
            phrase_id("x", adjectives=9)

    def test_close_inputs_diverge(self):
        # Avalanche: near-identical inputs should share no relationship.
        phrases = {phrase_id(f"user-{i}") for i in range(1000)}
        assert len(phrases) >= 990  # a few birthday collisions are possible


class TestDistribution:
    def test_nouns_roughly_uniform(self):
        # Chi-squared test on the noun slot over 100k hashes. With 504
        # bins and ~198 expected per bin, the statistic is ~N(503, sqrt(2*503)):
        # 700 is ~6 sigma, so a false failure is vanishingly unlikely.
        counts = {noun: 0 for noun in NOUNS}
        samples = 100_000
        for i in range(samples):
            counts[phrase_id(f"uniformity-{i}").rsplit("-", 1)[1]] += 1
        expected = samples / len(NOUNS)
        chi2 = sum((c - expected) ** 2 / expected for c in counts.values())
        assert chi2 < 700, chi2

    def test_empirical_collision_rate_matches_birthday_bound(self):
        # 100k random inputs over a 22.97M phrase space should collide in
        # ~n^2/2M ≈ 218 pairs. Poisson(218) stays within [140, 300] with
        # overwhelming probability; a systematic bias would blow past it.
        rng = random.Random(42)
        samples = 100_000
        seen = {}
        colliding_pairs = 0
        for _ in range(samples):
            text = "%030x" % rng.getrandbits(120)
            phrase = phrase_id(text)
            colliding_pairs += seen.get(phrase, 0)
            seen[phrase] = seen.get(phrase, 0) + 1
        expected = samples**2 / (2 * phrase_space())
        assert 140 <= colliding_pairs <= 300, (colliding_pairs, expected)


class TestCollisionMath:
    def test_phrase_space(self):
        a, n = len(ADJECTIVES), len(NOUNS)
        assert phrase_space() == a * (a - 1) * n
        assert phrase_space(adjectives=3) == a * (a - 1) * (a - 2) * n
        assert phrase_space(adjectives=1) == a * n

    def test_collision_probability_edges(self):
        assert collision_probability(0) == 0
        assert collision_probability(1) == 0
        assert 0 < collision_probability(2) < 1e-6
        assert collision_probability(2) == pytest.approx(1 / phrase_space(), rel=1e-6)

    def test_capacity_is_maximal(self):
        for p in (0.0001, 0.01, 0.5):
            n = capacity(p)
            assert collision_probability(n) <= p
            assert collision_probability(n + 1) > p

    def test_documented_capacity(self):
        # The README's headline claim: ~68 identifiers stay under a 0.01%
        # total collision probability with the default 3-word phrase.
        assert capacity(0.0001) == 68
        assert capacity(0.0001, adjectives=3) == 987
        assert capacity(0.01) == 680


class TestCli:
    def test_cli_digest(self):
        result = subprocess.run(
            [sys.executable, "-m", "clear_id", "hello world"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.stdout.strip() == phrase_id("hello world")

    def test_cli_stats(self):
        result = subprocess.run(
            [sys.executable, "-m", "clear_id", "--stats"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert f"{phrase_space():,}" in result.stdout
