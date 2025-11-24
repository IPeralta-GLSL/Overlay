import json
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPalette, QFont
from system_monitor import SystemMonitor

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.monitor = SystemMonitor()
        self.load_config()
        self.init_ui()
        self.start_timer()

    def load_config(self):
        with open('config.json', 'r') as f:
            self.config = json.load(f)

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.time_label = QLabel()
        self.cpu_label = QLabel()
        self.ram_label = QLabel()
        self.gpu_label = QLabel()

        font = QFont(self.config.get("font_family", "Arial"), self.config.get("font_size", 14))
        color = self.config.get("text_color", "#FFFFFF")
        style = f"color: {color};"

        for label in [self.time_label, self.cpu_label, self.ram_label, self.gpu_label]:
            label.setFont(font)
            label.setStyleSheet(style)
            layout.addWidget(label)

        bg_color = QColor(self.config.get("background_color", "#000000"))
        bg_color.setAlphaF(self.config.get("background_opacity", 0.5))
        palette = self.palette()
        palette.setColor(QPalette.Window, bg_color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.move(self.config.get("position_x", 10), self.config.get("position_y", 10))

    def start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(self.config.get("update_interval_ms", 1000))

    def update_stats(self):
        self.time_label.setText(f"Time: {self.monitor.get_current_time()}")
        self.cpu_label.setText(f"CPU: {self.monitor.get_cpu_usage()}%")
        self.ram_label.setText(f"RAM: {self.monitor.get_ram_usage()}%")
        self.gpu_label.setText(f"GPU: {self.monitor.get_gpu_usage():.1f}%")
