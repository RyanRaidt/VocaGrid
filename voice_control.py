# voice_control.py

from vosk import Model, KaldiRecognizer
import pyaudio
import json
import queue
import threading

COMMAND_QUEUE = queue.Queue()

class VoiceListener:
    def __init__(self, model_path="models/en"):
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
                text = json.loads(result).get("text", "")
                if text:
                    COMMAND_QUEUE.put(text)

    def start(self):
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
