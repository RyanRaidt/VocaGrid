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
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90, "hundred": 100, "thousand": 1000
}

def parse_number(text):
    """
    Convert a spoken number (e.g. "fifty five") into an integer (55).
    """
    text = text.lower().strip()
    parts = text.split()
    total = 0
    current = 0

    for part in parts:
        if part in word_to_number:
            scale = word_to_number[part]
            if scale == 100 or scale == 1000:
                current *= scale
            else:
                current += scale
        else:
            try:
                # Fallback: if it's already numeric
                current += int(part)
            except ValueError:
                pass

    total += current
    return total if total > 0 else 0

def clean_command(text):
    """
    Lowercase and strip extra spaces, correcting common mishears.
    """
    text = text.lower().strip()
    # Replace phonetic alphabet words with their letter equivalents
    for word, letter in phonetic_map.items():
        text = text.replace(word, letter)
    # Remove filler words
    text = re.sub(r"\bplease\b", "", text)
    text = re.sub(r"\bcomputer\b", "", text)
    return text

def match_command(cleaned_text, valid_commands):
    """
    Use fuzzy matching to find the closest valid command.
    """
    match, score, _ = process.extractOne(cleaned_text, valid_commands)
    return match

def parse_drag_or_diagonal(text):
    # Hold-to-drag
    if "hold" in text and "drag" in text:
        return "hold_drag"
    if "release" in text:
        return "release_drag"

    # Normalize text
    text = text.lower()

    # Search for diagonal movement like "move up right 30" or "move down left fifty"
    match = re.search(r"move\s+(up|down)[ -]?(left|right)\s+([a-z0-9 ]+)?", text)
    if match:
        vert = match.group(1)
        horiz = match.group(2)
        amount_text = match.group(3).strip() if match.group(3) else "50"
        try:
            amount = parse_number(amount_text) if not amount_text.isdigit() else int(amount_text)
        except:
            amount = 50
        return f"move_{vert}_{horiz}_{amount}"

    return None
