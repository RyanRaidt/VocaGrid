import re
from rapidfuzz import process

# Phonetic alphabet mapping
phonetic_map = {
    'alpha': 'a', 'bravo': 'b', 'charlie': 'c', 'delta': 'd', 'echo': 'e',
    'foxtrot': 'f', 'golf': 'g', 'hotel': 'h', 'india': 'i', 'juliet': 'j',
    'kilo': 'k', 'lima': 'l', 'mike': 'm', 'november': 'n', 'oscar': 'o',
    'papa': 'p', 'quebec': 'q', 'romeo': 'r', 'sierra': 's', 'tango': 't',
    'uniform': 'u', 'victor': 'v', 'whiskey': 'w', 'xray': 'x', 'yankee': 'y', 'zulu': 'z'
}

# Spoken word numbers
word_to_number = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30
}

def clean_command(raw_text: str) -> str:
    """Normalize input: remove filler words, convert phonetics and spoken numbers."""
    text = raw_text.lower().strip()
    text = re.sub(r'\b(move to|go to|letter|click on|select|click|press)\b', '', text)

    # Convert phonetics to letters
    words = text.split()
    converted = [phonetic_map.get(word, word) for word in words]
    text = ' '.join(converted)

    # Handle compound and single numbers
    words = text.split()
    result = []
    i = 0
    while i < len(words):
        word = words[i]
        next_word = words[i + 1] if i + 1 < len(words) else ""
        if word in ["twenty", "thirty"] and next_word in word_to_number:
            result.append(str(word_to_number[word] + word_to_number[next_word]))
            i += 2
        elif word in word_to_number:
            result.append(str(word_to_number[word]))
            i += 1
        else:
            result.append(word)
            i += 1

    return re.sub(r'\s+', '', ''.join(result))

def match_command(cleaned_text: str, valid_commands: list[str], threshold: int = 70) -> str | None:
    match, score, _ = process.extractOne(cleaned_text, valid_commands)
    print(f"🔍 Fuzzy match: {cleaned_text} → {match} (score: {score})")
    return match if score >= threshold else None
