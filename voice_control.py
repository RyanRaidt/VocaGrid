from vosk import Model, KaldiRecognizer
import pyaudio
import json
import queue
import threading

from utils import clean_command, match_command

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

                #  Voice control: Toggle control panel
                if text == "toggle panel":
                    print("🪟 Voice command: toggle control panel")
                    COMMAND_QUEUE.put("toggle_panel")
                    continue

                #  Theme commands
                if text in theme_commands:
                    print(f"🎨 Matched theme command: {text}")
                    COMMAND_QUEUE.put(theme_commands[text])
                    continue

                #  Click commands
                if text in click_commands:
                    print(f"✅ Matched click command: {text}")
                    COMMAND_QUEUE.put(click_commands[text])
                    continue

                #  Grid command
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
