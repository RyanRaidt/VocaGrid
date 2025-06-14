import sys
import time
import threading
import keyboard  # Global hotkey
import pyautogui  # For mouse movement

from voice_control import VoiceListener, COMMAND_QUEUE
from mouse_control import move_to_grid_cell, click
from grid_overlay import GridOverlay, THEMES
from control_panel import ControlPanel

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, Qt

# Global panel reference
panel = None

def move_mouse_by(dx=0, dy=0):
    pyautogui.moveRel(dx, dy, duration=0.1)

class VocaGridApp(GridOverlay):
    def __init__(self, theme="default"):
        self.theme_name = theme
        super().__init__(columns=26, rows=30, theme=theme)

        self.voice = VoiceListener()
        threading.Thread(target=self.voice.listen, daemon=True).start()


        self.timer = QTimer()
        self.timer.timeout.connect(self.check_commands)
        self.timer.start(1000)

    def check_commands(self):
        global panel
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

            elif command == "toggle_panel":
                if panel:
                    panel.toggle_visibility()

            # 🧲 Diagonal movement: check this before single‐axis moves
            elif command.startswith("move_") and len(command.split("_")) == 4:
                _, vertical, horizontal, amount = command.split("_")
                dx = int(amount) if horizontal == "right" else -int(amount)
                dy = int(amount) if vertical == "down" else -int(amount)
                print(f"🧭 Diagonal move: dx={dx}, dy={dy}")
                move_mouse_by(dx=dx, dy=dy)

            # 🧭 Single‐axis moves
            elif command.startswith("move_right_"):
                amount = int(command.split("_")[-1])
                move_mouse_by(dx=amount, dy=0)

            elif command.startswith("move_left_"):
                amount = int(command.split("_")[-1])
                move_mouse_by(dx=-amount, dy=0)

            elif command.startswith("move_up_"):
                amount = int(command.split("_")[-1])
                move_mouse_by(dx=0, dy=-amount)

            elif command.startswith("move_down_"):
                amount = int(command.split("_")[-1])
                move_mouse_by(dx=0, dy=amount)

            elif command == "hold_drag":
                print("🖱️ Holding mouse button...")
                pyautogui.mouseDown()

            elif command == "release_drag":
                print("🖱️ Releasing mouse button...")
                pyautogui.mouseUp()

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

def handle_theme_command(command: str):
    if command.startswith("theme_"):
        new_theme = command.replace("theme_", "")
        if new_theme in THEMES:
            print(f"🎨 (Panel) Switching theme to: {new_theme}")
            overlay.theme_name = new_theme
            overlay.update_theme()

def listen_for_global_shortcut():
    keyboard.add_hotkey('ctrl+alt+p', lambda: panel.toggle_visibility() if panel is not None else None)
    keyboard.wait()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    overlay = VocaGridApp(theme="default")
    panel = ControlPanel(theme_callback=handle_theme_command)

    threading.Thread(target=listen_for_global_shortcut, daemon=True).start()

    sys.exit(app.exec())
