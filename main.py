
import sys
from voice_control import VoiceListener, COMMAND_QUEUE
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtCore import QTimer

class TransparentOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.columns = 20  # A-T
        self.rows = 20     # 1–20
        self.initUI()
        self.voice = VoiceListener()
        self.voice.start()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_commands)
        self.timer.start(1000)

    def check_commands(self):
        while not COMMAND_QUEUE.empty():
            command = COMMAND_QUEUE.get()
            print("Heard:", command)


    def initUI(self):
        self.setWindowTitle('VocaGrid Overlay')
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.showFullScreen()

    def paintEvent(self, event):
        screen_width = self.width()
        screen_height = self.height()
        cell_width = screen_width / self.columns
        cell_height = screen_height / self.rows

        painter = QPainter(self)
        painter.setPen(QColor(0, 255, 0, 100))  # Light green lines
        painter.setFont(QFont('Arial', 10))

        # Draw vertical lines & column labels (A–T)
        for col in range(self.columns + 1):
            x = int(col * cell_width)
            painter.drawLine(x, 0, x, screen_height)
            if col < self.columns:
                label = chr(65 + col)  # A-Z
                painter.drawText(QRect(x, 0, int(cell_width), 20), Qt.AlignmentFlag.AlignCenter, label)

        # Draw horizontal lines & row labels (1–20)
        for row in range(self.rows + 1):
            y = int(row * cell_height)
            painter.drawLine(0, y, screen_width, y)
            if row < self.rows:
                label = str(row + 1)
                painter.drawText(QRect(0, y, 30, int(cell_height)), Qt.AlignmentFlag.AlignVCenter, label)

        painter.end()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    overlay = TransparentOverlay()
    sys.exit(app.exec())

