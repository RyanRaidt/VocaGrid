from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QRect
import ctypes

# 🎨 Theme definitions
THEMES = {
    "default": {
        "background_alpha": 50,
        "thin_line": QColor(0, 255, 0, 100),
        "bold_line": QColor(0, 255, 0, 180),
        "font": QFont('Arial', 12, weight=QFont.Weight.Bold),
        "font_color": QColor(0, 255, 0)
    },
    "high_contrast": {
        "background_alpha": 100,
        "thin_line": QColor(255, 255, 255, 100),
        "bold_line": QColor(255, 255, 255, 200),
        "font": QFont('Arial', 12, weight=QFont.Weight.Bold),
        "font_color": QColor(255, 255, 255)
    },
    "blue_light": {
        "background_alpha": 30,
        "thin_line": QColor(0, 170, 255, 80),
        "bold_line": QColor(0, 170, 255, 180),
        "font": QFont('Arial', 12, weight=QFont.Weight.Bold),
        "font_color": QColor(0, 170, 255)
    }
}

class GridOverlay(QWidget):
    def __init__(self, columns=26, rows=30, theme="default"):
        super().__init__()
        self.columns = columns
        self.rows = rows
        self.theme = THEMES.get(theme, THEMES["default"])
        self.initUI()

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

        # 🪟 Make overlay click-through using Windows API
        hwnd = int(self.winId())
        set_click_through(hwnd)

    def paintEvent(self, event):
        screen_width = self.width()
        screen_height = self.height()
        cell_width = screen_width / self.columns
        cell_height = screen_height / self.rows

        painter = QPainter(self)

        # 1. Draw semi-transparent background
        bg_color = QColor(0, 0, 0, self.theme["background_alpha"])
        painter.fillRect(self.rect(), bg_color)

        # 2. Setup font and pens
        painter.setFont(self.theme["font"])
        thin_pen_color = self.theme["thin_line"]
        bold_pen_color = self.theme["bold_line"]
        font_color = self.theme["font_color"]

        # 3. Draw vertical lines & column labels
        for col in range(self.columns + 1):
            x = int(col * cell_width)
            is_major_line = (col % 5 == 0)

            painter.setPen(bold_pen_color if is_major_line else thin_pen_color)
            painter.drawLine(x, 0, x, screen_height)

            if col < self.columns:
                painter.setPen(font_color)
                label = chr(65 + col)
                painter.drawText(QRect(x, 0, int(cell_width), 20), Qt.AlignmentFlag.AlignCenter, label)

        # 4. Draw horizontal lines & row labels
        for row in range(self.rows + 1):
            y = int(row * cell_height)
            is_major_line = (row % 5 == 0)

            painter.setPen(bold_pen_color if is_major_line else thin_pen_color)
            painter.drawLine(0, y, screen_width, y)

            if row < self.rows:
                painter.setPen(font_color)
                label = str(row + 1)
                painter.drawText(QRect(0, y, 30, int(cell_height)), Qt.AlignmentFlag.AlignVCenter, label)

        painter.end()

# 🪟 Windows API click-through setup
def set_click_through(hwnd):
    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x80000
    WS_EX_TRANSPARENT = 0x20

    user32 = ctypes.windll.user32
    get_window_long = user32.GetWindowLongW
    set_window_long = user32.SetWindowLongW

    style = get_window_long(hwnd, GWL_EXSTYLE)
    style |= WS_EX_LAYERED | WS_EX_TRANSPARENT
    set_window_long(hwnd, GWL_EXSTYLE, style)
