import sys
import time
from voice_control import VoiceListener, COMMAND_QUEUE
from mouse_control import move_to_grid_cell, click
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from grid_overlay import GridOverlay

class VocaGridApp(GridOverlay):
    def __init__(self, theme="default"):
        super().__init__(columns=26, rows=30, theme=theme)
        self.voice = VoiceListener()
        self.voice.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_commands)
        self.timer.start(1000)

    def check_commands(self):
        while not COMMAND_QUEUE.empty():
            command = COMMAND_QUEUE.get()
            print("Heard:", command)

            if command in ["left_click", "right_click", "double_click"]:
                click(command)
            else:
                col = command[0].upper()
                try:
                    row = int(command[1:])
                    time.sleep(0.2)
                    move_to_grid_cell(col, row, self.width(), self.height(), self.columns, self.rows)
                except ValueError:
                    print(f"⚠️ Invalid grid reference: {command}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    overlay = VocaGridApp(theme="blue_light")  # try "blue_light" or "default"
    sys.exit(app.exec())
