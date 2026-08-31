#!/usr/bin/env python3
"""Build the frozen word lists shipped in ``src/clear_id/wordlists/``.

Sources and tooling:

* Candidate words: CC0 lists from https://github.com/dariusk/corpora
  (clone it and pass the path to its ``data`` directory as the first CLI
  argument; defaults to ``/home/user/dariusk/corpora/data``):
  ``words/adjs.json`` and ``words/nouns.json`` for the base vocabulary, plus
  concrete-noun lists (animals, fruits, vegetables, flowers, instruments,
  everyday objects) that make especially memorable identifiers.
* A small hand-curated supplement of vivid, common adjectives (colors,
  sizes, moods) that the corpora list lacks.
* Frequency filter: the ``wordfreq`` package (Zipf scale). Zipf >= 3.5
  means the word occurs at least ~3 times per million words of running
  English text — comfortably inside a native speaker's vocabulary.
* Part-of-speech validation: NLTK WordNet. The corpora lists contain
  mis-tagged entries ("accountant" as an adjective, "apologise" as a
  noun); requiring a WordNet synset of the right part of speech removes
  them.

Morphology heuristics keep the phrases reading naturally: plural nouns,
participial adjectives ("arrested", "beaten"), gerunds ("betting"), and
comparatives/superlatives ("tougher", "biggest") are dropped unless
explicitly allowlisted, and a curated blocklist removes words that make
poor user-facing identifiers (violence, illness, crude terms, first names,
trademarks, charged vocabulary).

The output is deterministic for a given corpora checkout and wordfreq /
WordNet version, and the generated files are committed, so the package
itself has no dependency on any of these tools at runtime.
"""

import json
import re
import sys
from pathlib import Path

from wordfreq import zipf_frequency

try:
    from nltk.corpus import wordnet as wn

    wn.synsets("test")
except LookupError:  # pragma: no cover - one-time setup
    import nltk

    nltk.download("wordnet", quiet=True)
    from nltk.corpus import wordnet as wn

MIN_ZIPF = 3.5
WORD_RE = re.compile(r"[a-z]{3,10}")

CONCRETE_NOUN_SOURCES = [
    ("animals/common.json", "animals"),
    ("foods/fruits.json", "fruits"),
    ("foods/vegetables.json", "vegetables"),
    ("plants/flowers.json", "flowers"),
    ("music/instruments.json", "instruments"),
    ("objects/objects.json", "objects"),
]

# Vivid, extremely common adjectives the corpora list lacks. Still subject
# to the frequency filter, so nothing obscure can slip in through here.
SUPPLEMENT_ADJECTIVES = {
    "amber", "ancient", "azure", "bold", "brave", "breezy", "bright",
    "brisk", "calm", "charming", "cheerful", "chilly", "clever", "cloudy",
    "cool", "coral", "cozy", "crimson", "crisp", "curious", "daring",
    "deep", "dusty", "eager", "early", "electric", "elegant", "emerald",
    "fancy", "fast", "fierce", "fiery", "fluffy", "flying", "foggy",
    "friendly", "frosty", "frozen", "gentle", "giant", "gifted", "gleaming",
    "glowing", "golden", "graceful", "grand", "green", "happy", "hardy",
    "hidden", "honest", "humble", "icy", "indigo", "ivory", "jade", "jolly",
    "keen", "kind", "large", "lavender", "leafy", "little", "lively",
    "loyal", "lucky", "lunar", "magenta", "magnetic", "majestic", "mellow",
    "merry", "misty", "modern", "modest", "nimble", "noble", "northern",
    "olive", "orange", "patient", "peaceful", "pink", "playful", "polar",
    "polished", "proud", "purple", "quiet", "radiant", "rainy", "rapid",
    "rare", "red", "regal", "rosy", "round", "royal", "ruby", "rustic",
    "sandy", "secret", "serene", "sharp", "silent", "silky", "silver",
    "sincere", "sleek", "small", "smart", "smooth", "snowy", "soft",
    "solar", "solid", "sparkling", "spicy", "stellar", "stormy", "strong",
    "sturdy", "sunny", "swift", "tall", "teal", "tender", "tidy", "tiny",
    "tranquil", "turquoise", "velvet", "vibrant", "violet", "vivid",
    "warm", "western", "wild", "windy", "wise", "witty", "wooden", "young",
}

# Participial (-ed) and gerund (-ing) forms that still read as natural,
# positive adjectives; everything else in those shapes is dropped.
ADJ_ED_ING_ALLOWLIST = {
    "amazing", "absorbing", "charming", "daring", "dedicated", "determined",
    "devoted", "exciting", "gifted", "gleaming", "glowing", "polished",
    "shining", "soaring", "sparkling", "spirited", "talented", "willing",
}

# Nouns ending in -ing that are ordinary nouns rather than awkward gerunds.
NOUN_ING_ALLOWLIST = {
    "building", "bowling", "painting", "lighting", "morning", "evening",
    "wedding", "pudding", "spring",
}

# Words that pass the automated filters but make poor user-facing
# identifiers: violence, illness, death, crime, crude terms, judgemental
# words, charged political/religious vocabulary, first names, trademarks,
# regional spellings, and entries whose dominant reading is the wrong part
# of speech.
BLOCKLIST = {
    # wrong dominant part of speech / not really adjectives
    "abroad", "alright", "amino", "blame", "broker", "dozen", "dread",
    "existent", "excess", "liver", "midway", "nonsense", "north",
    "outlaw", "reverend", "sometime", "summary", "sunset", "utter",
    # awkward participles/comparatives the morphology heuristics miss
    "beaten", "shaken", "laden", "sought", "healthier", "duplicate",
    "human",
    # not really nouns / determiner-like / interjections
    "hello", "means", "meantime", "nobody", "outdoors", "somewhere",
    "forefront", "vicinity", "stole", "apologise",
    # judgement / body / appearance
    "arrested", "alleged", "guilty", "stupid", "ugly", "fat", "dumb",
    "lame", "insane", "crazy", "drunk", "naked", "sexy", "obese",
    "senile", "disabled", "crippled", "blind", "deaf", "poor", "cheap",
    "fake", "corrupt", "racist", "sexist", "skinny", "adult", "virgin",
    "foolish", "jealous", "hopeless", "horrible", "useless", "worthless",
    "unpleasant", "unreliable", "unsafe", "ridiculous", "afraid",
    "aggressive", "adverse", "defective", "flawed", "fraudulent",
    "negative", "offensive", "bipolar", "hurtful",
    # violence / death / crime
    "dead", "deadly", "killer", "murder", "murderer", "suicide",
    "slaughter", "assault", "abuse", "victim", "weapon", "bomb", "bomber",
    "terror", "terrorism", "terrorist", "hostage", "slavery", "slave",
    "war", "warfare", "genocide", "massacre", "rape", "torture",
    "execution", "violent", "violence", "aggression", "brutal", "bloody",
    "attacker", "invasion", "uprising", "conflict", "hostility",
    "prisoner", "probation", "detention", "dismissal", "negligence",
    "violation", "backlash", "nuisance", "evacuation", "extinction",
    "collision", "error", "hardship", "demon",
    # illness / misfortune
    "cancer", "tumor", "disease", "plague", "infected", "sick", "anxiety",
    "disability", "cemetery",
    "depression", "trauma", "grief", "misery", "funeral", "coffin",
    "corpse", "grave", "allergy", "asthma", "pneumonia", "seizure",
    "diagnosis", "syndrome", "illness", "insanity", "madness",
    "mortality", "toxicity", "deficiency", "mutation", "nightmare",
    "horror", "injured", "suffering", "resentment", "vomiting",
    # sex / bodily / crude
    "sexual", "erotic", "nude", "breast", "rectum", "urine", "feces",
    "booty", "sperm", "underwear", "fetish", "daddy", "vampire",
    "girlfriend", "toilet", "whip",
    # charged political / religious
    "apartheid", "nazi", "fascist", "fascism", "communist", "jihad",
    "heathen", "pagan", "cult", "racism", "sexism", "partisan",
    "electoral",
    # awkward / legal / financial trouble
    "allegation", "lawsuit", "litigation", "divorce", "bankruptcy",
    "debt", "scam", "fraud", "hell", "damn", "curse", "doom", "conspiracy",
    # first names / surnames / places / trademarks
    "jenny", "jones", "joseph", "martin", "peter", "terry", "homer",
    "bonnie", "china", "google", "heath", "ipod",
    # negative-leaning leftovers
    "offense", "domination",
    # regional spelling variants (keep one convention)
    "colour", "favourable", "recognised", "neighbour", "licence", "litre",
    "metre", "storey", "whisky",
}


def load_corpora_list(path: Path, key: str) -> list[str]:
    return json.loads(path.read_text())[key]


def has_pos(word: str, pos: str) -> bool:
    if pos == "a":
        return bool(wn.synsets(word, pos="a") or wn.synsets(word, pos="s"))
    return bool(wn.synsets(word, pos=pos))


def is_word(word: str) -> bool:
    return zipf_frequency(word, "en") >= 2.5


def passes_base_filters(word: str, pos: str) -> bool:
    return (
        WORD_RE.fullmatch(word) is not None
        and word not in BLOCKLIST
        and zipf_frequency(word, "en") >= MIN_ZIPF
        and has_pos(word, pos)
    )


def filter_adjectives(words: list[str]) -> set[str]:
    kept = set()
    for word in words:
        if not passes_base_filters(word, "a"):
            continue
        if word.endswith(("ed", "ing")) and word not in ADJ_ED_ING_ALLOWLIST:
            continue
        # comparatives/superlatives: "tougher", "biggest" (but not "clever")
        if word.endswith("er") and is_word(word[:-2]):
            continue
        if word.endswith("est") and (is_word(word[:-3]) or is_word(word[:-2])):
            continue
        kept.add(word)
    return kept


def filter_nouns(words: list[str]) -> set[str]:
    kept = set()
    for word in words:
        if not passes_base_filters(word, "n"):
            continue
        if word.endswith("ing") and word not in NOUN_ING_ALLOWLIST:
            continue
        # plurals: ends in "s" and the stem is itself a word ("balls",
        # "hearts"); keeps true singulars like "oasis" and "genesis"
        if word.endswith("s") and (is_word(word[:-1]) or is_word(word[:-2])):
            continue
        kept.add(word)
    return kept


def main() -> None:
    data_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/user/dariusk/corpora/data")
    out_dir = Path(__file__).resolve().parent.parent / "src" / "clear_id" / "wordlists"
    out_dir.mkdir(parents=True, exist_ok=True)

    adjectives = filter_adjectives(
        load_corpora_list(data_dir / "words" / "adjs.json", "adjs")
    )
    adjectives |= filter_adjectives(sorted(SUPPLEMENT_ADJECTIVES))

    nouns = filter_nouns(load_corpora_list(data_dir / "words" / "nouns.json", "nouns"))
    for rel_path, key in CONCRETE_NOUN_SOURCES:
        nouns |= filter_nouns(load_corpora_list(data_dir / rel_path, key))

    # Keep the two lists disjoint so a phrase can never repeat a word across
    # positions ("orange orange fox"). Color-like supplement adjectives win
    # the adjective slot; any other overlap stays a noun.
    overlap = adjectives & nouns
    nouns -= overlap & SUPPLEMENT_ADJECTIVES
    adjectives -= overlap - SUPPLEMENT_ADJECTIVES

    for name, words in (("adjectives", adjectives), ("nouns", nouns)):
        path = out_dir / f"{name}.txt"
        path.write_text("\n".join(sorted(words)) + "\n")
        print(f"{path.name}: {len(words)} words")
    if overlap:
        print(f"resolved {len(overlap)} adjective/noun overlaps: {sorted(overlap)}")


if __name__ == "__main__":
    main()
