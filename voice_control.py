from vosk import Model, KaldiRecognizer
import pyaudio
import json
import queue
import threading
import re
from word2number import w2n

from utils import clean_command, match_command, parse_drag_or_diagonal

COMMAND_QUEUE = queue.Queue()

# All valid grid commands (a1–z30)
valid_commands = [f"{chr(c)}{r}" for c in range(ord("a"), ord("z") + 1) for r in range(1, 31)]

# Click commands
click_commands = {
    "left click": "left_click",
    "right click": "right_click",
    "double click": "double_click"
}

# Theme commands
theme_commands = {
    "default theme": "theme_default",
    "high contrast": "theme_high_contrast",
    "blue light": "theme_blue_light"
}

# Mouse movement & scroll
mouse_actions = {
    "scroll up": "scroll_up",
    "scroll down": "scroll_down",
    "start drag": "start_drag",
    "drop here": "drop_here"
}


def extract_amount(text: str) -> str | None:
    """
    Parse spoken movement like 'move right one hundred' → 'move_right_100'.
    Defaults to 50 if no amount is spoken or understood.
    """
    match = re.match(r"move (right|left|up|down)( .+)?", text)
    if match:
        direction = match.group(1)
        raw_amount = match.group(2).strip() if match.group(2) else ""
        try:
            amount = w2n.word_to_num(raw_amount) if raw_amount else 50
        except ValueError:
            amount = 50
        return f"move_{direction}_{amount}"
    return None


class VoiceListener:
    def __init__(self, model_path="models/vosk-model-small-en-us-0.15"):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8192
        )
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

                # 🪟 Panel toggle
                if text == "toggle panel":
                    print("🪟 Voice command: toggle control panel")
                    COMMAND_QUEUE.put("toggle_panel")
                    continue

                # 🎨 Theme change
                if text in theme_commands:
                    print(f"🎨 Matched theme command: {text}")
                    COMMAND_QUEUE.put(theme_commands[text])
                    continue

                # ✅ Click commands
                if text in click_commands:
                    print(f"✅ Matched click command: {text}")
                    COMMAND_QUEUE.put(click_commands[text])
                    continue

                # 🖱️ Scroll / drag-drop
                if text in mouse_actions:
                    print(f"🖱️ Matched mouse command: {text}")
                    COMMAND_QUEUE.put(mouse_actions[text])
                    continue

                    # 🧲 Drag or diagonal
                drag_or_diag = parse_drag_or_diagonal(text)
                if drag_or_diag:
                    print(f"🧲 Parsed drag/diagonal command: {text} → {drag_or_diag}")
                    COMMAND_QUEUE.put(drag_or_diag)
                    continue

                    # 🖱️ Mouse move
                move_cmd = extract_amount(text)
                if move_cmd:
                    print(f"🖱️ Parsed move command: {text} → {move_cmd}")
                    COMMAND_QUEUE.put(move_cmd)
                    continue


                # 🧩 Grid cell
                cleaned = clean_command(text)
                matched = match_command(cleaned, valid_commands)
                if matched:
                    print(f"✅ Matched grid command: {matched}")
                    COMMAND_QUEUE.put(matched)
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
