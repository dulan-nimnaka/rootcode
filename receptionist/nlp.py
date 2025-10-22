import re
from typing import Optional

NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12
}

def _word_to_number(token: str) -> Optional[int]:
    token = token.lower()
    if token.isdigit():
        return int(token)
    if token in NUMBER_WORDS:
        return NUMBER_WORDS[token]
    # handle 'a' as 1
    if token in ("a", "an"):
        return 1
    return None

def parse_party_size(text: str) -> Optional[int]:
    """Basic heuristic NLP to extract party size from a phrase.

    Examples:
      - "a table for six" -> 6
      - "just me and my wife" -> 2
      - "I have two friends with me" -> 3

    This is intentionally simple for an offline simulation. For production,
    integrate a proper NLU engine (Dialogflow/Rasa).
    """
    if not text:
        return None
    text = text.lower()

    # common patterns
    # look for explicit "for X"
    m = re.search(r"for (\w+)", text)
    if m:
        num = _word_to_number(m.group(1))
        if num is not None:
            return num

    # look for explicit numbers
    tokens = re.findall(r"\w+", text)
    # count occurrences like 'me and my wife' -> count pronouns/people words
    people_words = {"me", "i", "wife", "husband", "friend", "friends", "guest", "guests", "son", "daughter", "child", "kids"}
    people_count = sum(1 for t in tokens if t in people_words)
    # heuristics: if phrase contains 'me' plus another person words, count them
    if people_count >= 2:
        return people_count

    # try to find any number word in tokens
    for t in tokens:
        n = _word_to_number(t)
        if n is not None:
            # special case: "two friends and me" -> friends(2) + me(1)
            if 'me' in tokens and t not in ('me', 'i'):
                # sum number + 1
                return n + 1
            return n

    # fallback: if phrase mentions "just me" or "just me and my wife"
    if 'just me' in text or text.strip() in ("me", "just me"):
        return 1

    return None
