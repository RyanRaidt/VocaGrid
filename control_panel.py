from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap

class ControlPanel(QWidget):
    toggle_requested = pyqtSignal()

    def __init__(self, theme_callback):
        super().__init__()
        self.theme_callback = theme_callback
        self.drag_position = None
        self.mic_status = True  # Assume always listening for now
        self.mic_icon = QLabel()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("VocaGrid Control Panel")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedSize(220, 240)
        self.setStyleSheet("background-color: #222; color: white; border: 1px solid #555;")

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title bar with mic icon and minimize button
        title_bar = QHBoxLayout()
        title_label = QLabel("🎛 Theme Presets")
        title_label.setStyleSheet("font-weight: bold;")
        title_bar.addWidget(title_label)

        self.update_mic_icon()
        title_bar.addWidget(self.mic_icon)

        minimize_btn = QPushButton("–")
        minimize_btn.setFixedWidth(20)
        minimize_btn.setStyleSheet("background-color: #444; color: white;")
        minimize_btn.clicked.connect(self.hide)
        title_bar.addWidget(minimize_btn)

        layout.addLayout(title_bar)

        # Theme buttons
        for name, command in [
            ("Default", "theme_default"),
            ("High Contrast", "theme_high_contrast"),
            ("Blue Light", "theme_blue_light")
        ]:
            btn = QPushButton(name)
            btn.setStyleSheet("background-color: #444; color: white; border-radius: 5px; padding: 5px;")
            btn.clicked.connect(lambda _, cmd=command: self.theme_callback(cmd))
            layout.addWidget(btn)

        self.setLayout(layout)
        self.move(50, 50)
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def toggle_visibility(self):
        self.setVisible(not self.isVisible())

    def update_mic_icon(self, active=True):
        self.mic_status = active
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.green if self.mic_status else Qt.GlobalColor.red)
        self.mic_icon.setPixmap(pixmap)
