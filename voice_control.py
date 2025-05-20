from vosk import Model, KaldiRecognizer
import pyaudio
import json
import queue
import threading
import re
from rapidfuzz import process

COMMAND_QUEUE = queue.Queue()

# 🎯 All valid grid commands (e.g., a1, t20)
valid_commands = [f"{chr(c)}{r}" for c in range(ord("a"), ord("z") + 1) for r in range(1, 31)]


phonetic_map = {
    'alpha': 'a', 'bravo': 'b', 'charlie': 'c', 'delta': 'd', 'echo': 'e',
    'foxtrot': 'f', 'golf': 'g', 'hotel': 'h', 'india': 'i', 'juliet': 'j',
    'kilo': 'k', 'lima': 'l', 'mike': 'm', 'november': 'n', 'oscar': 'o',
    'papa': 'p', 'quebec': 'q', 'romeo': 'r', 'sierra': 's', 'tango': 't',
    'uniform': 'u', 'victor': 'v', 'whiskey': 'w', 'xray': 'x', 'yankee': 'y', 'zulu': 'z'
}

def clean_command(raw_text: str) -> str:
    """Normalize input: remove filler words, convert phonetics and spoken numbers."""
    text = raw_text.lower().strip()

    # Step 1: Remove filler verbs
    text = re.sub(r'\b(move to|go to|letter|click on|select|click|press)\b', '', text)

    # Step 2: Convert phonetic words to letters
    words = text.split()
    converted = []
    for word in words:
        if word in phonetic_map:
            converted.append(phonetic_map[word])
        else:
            converted.append(word)
    text = ' '.join(converted)

    # Step 3: Convert spoken numbers to digits
    word_to_number = {
        'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
        'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
        'eleven': '11', 'twelve': '12', 'thirteen': '13', 'fourteen': '14',
        'fifteen': '15', 'sixteen': '16', 'seventeen': '17', 'eighteen': '18',
        'nineteen': '19', 'twenty': '20', 'thirty': '30'
    }

    for word, digit in word_to_number.items():
        text = re.sub(rf'\b{word}\b', digit, text)

    # Step 4: Remove spaces to match grid format (e.g., "c 9" → "c9")
    return re.sub(r'\s+', '', text)


def match_command(cleaned_text: str):
    """Find the closest matching valid grid command using fuzzy matching."""
    match, score, _ = process.extractOne(cleaned_text, valid_commands)
    return match if score > 75 else None
click_commands = {
    "left click": "left_click",
    "right click": "right_click",
    "double click": "double_click"
}

class VoiceListener:
    def __init__(self, model_path="models/vosk-model-small-en-us-0.15"):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=16000,
                                      input=True,
                                      frames_per_buffer=8192)
        self.stream.start_stream()
        self.running = True

    def listen(self):
        while self.running:
            data = self.stream.read(4096, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                result = self.recognizer.Result()
                text = json.loads(result).get("text", "").strip().lower()

                if not text:
                    continue

                cleaned = clean_command(text)
                matched = match_command(cleaned)

                if matched:
                    print(f"✅ Matched grid command: {matched}")
                    COMMAND_QUEUE.put(matched)
                elif text in click_commands:
                    print(f"✅ Matched click command: {text}")
                    COMMAND_QUEUE.put(click_commands[text])
                else:
                    print(f"❌ Could not match command: {text}")


    def start(self):
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
