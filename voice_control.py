import pyaudio
import wave
import queue
import threading
import re
import time
from faster_whisper import WhisperModel

from utils import clean_command, parse_drag_or_diagonal

# Global command queue
COMMAND_QUEUE = queue.Queue()

# Valid grid commands a1–z30
valid_commands = [f"{chr(c)}{r}" for c in range(ord("a"), ord("z")+1) for r in range(1,31)]

# Click, theme, and mouse action mappings
click_commands = {
    "left click": "left_click",
    "right click": "right_click",
    "double click": "double_click"
}

theme_commands = {
    "default theme": "theme_default",
    "high contrast": "theme_high_contrast",
    "blue light": "theme_blue_light"
}

mouse_actions = {
    "scroll up": "scroll_up",
    "scroll down": "scroll_down",
    "start drag": "start_drag",
    "drop here": "drop_here"
}

# Initialize Whisper model on CPU
model = WhisperModel("base", compute_type="int8", device="cpu")

def record_audio(filename="temp.wav", duration=3):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    frames = []
    for _ in range(int(RATE / CHUNK * duration)):
        frames.append(stream.read(CHUNK))

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    return filename


def transcribe(filename="temp.wav"):
    segments, _ = model.transcribe(filename)
    for segment in segments:
        text = segment.text.strip().lower()
        # Filter out short or noisy results
        if len(text) < 2 or not text.isascii() or text in {"uh","um","hmm","the","it"}:
            return ""
        # Keep only first sentence/clause
        if "." in text:
            text = text.split(".")[0].strip()
        return text
    return ""


def extract_amount(text: str) -> str | None:
    match = re.match(r"move (right|left|up|down)( .+)?", text)
    if match:
        direction = match.group(1)
        raw = match.group(2).strip() if match.group(2) else ""
        # Extract digits only
        digits = re.sub(r"\D", "", raw)
        try:
            amount = int(digits) if digits else 50
        except ValueError:
            amount = 50
        return f"move_{direction}_{amount}"
    return None


class VoiceListener:
    def __init__(self):
        self.running = True

    def listen(self):
        while self.running:
            try:
                filename = record_audio()
                text = transcribe(filename)
                if not text:
                    continue

                print(f"Heard: {text}")

                # Early command matches
                if text == "toggle panel":
                    print("🪟 Voice command: toggle control panel")
                    COMMAND_QUEUE.put("toggle_panel")
                    continue

                if text in theme_commands:
                    print(f"🎨 Matched theme command: {text}")
                    COMMAND_QUEUE.put(theme_commands[text])
                    continue

                if text in click_commands:
                    print(f"✅ Matched click command: {text}")
                    COMMAND_QUEUE.put(click_commands[text])
                    continue

                if text in mouse_actions:
                    print(f"🖱️ Matched mouse command: {text}")
                    COMMAND_QUEUE.put(mouse_actions[text])
                    continue

                diag = parse_drag_or_diagonal(text)
                if diag:
                    print(f"🧲 Parsed drag/diagonal: {diag}")
                    COMMAND_QUEUE.put(diag)
                    continue

                move_cmd = extract_amount(text)
                if move_cmd:
                    print(f"🖱️ Parsed move command: {move_cmd}")
                    COMMAND_QUEUE.put(move_cmd)
                    continue

                # Clean for grid matching
                cleaned = text.replace(" ", "").replace("-", "")
                if re.match(r"^[a-z]\d{1,2}$", cleaned) and cleaned in valid_commands:
                    print(f"✅ Matched grid command: {cleaned}")
                    COMMAND_QUEUE.put(cleaned)
                else:
                    print(f"❌ Ignored non-command: {text}")
            except Exception as e:
                print("🎤 VoiceListener error:", e)
            time.sleep(0.5)

    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()

    def stop(self):
        self.running = False
