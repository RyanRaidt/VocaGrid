import sys
import time
from voice_control import VoiceListener, COMMAND_QUEUE
from mouse_control import move_to_grid_cell, click
from grid_overlay import GridOverlay, THEMES
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

class VocaGridApp(GridOverlay):
    def __init__(self, theme="default"):
        self.theme_name = theme
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

            elif command.startswith("theme_"):
                new_theme = command.replace("theme_", "")
                if new_theme in THEMES:
                    print(f"🎨 Switching theme to: {new_theme}")
                    self.theme_name = new_theme
                    self.update_theme()
                else:
                    print(f"⚠️ Unknown theme: {new_theme}")

            else:
                col = command[0].upper()
                try:
                    row = int(command[1:])
                    time.sleep(0.2)
                    move_to_grid_cell(col, row, self.width(), self.height(), self.columns, self.rows)
                except ValueError:
                    print(f"⚠️ Invalid grid reference: {command}")

    def update_theme(self):
        self.theme = THEMES[self.theme_name]
        self.repaint()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    overlay = VocaGridApp(theme="default")  # try "high_contrast" or "blue_light"
    sys.exit(app.exec())
