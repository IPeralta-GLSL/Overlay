from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPalette, QFont, QGuiApplication, QPainter, QBrush
from src.core.system_monitor import SystemMonitor
from src.utils.translations import TRANSLATIONS

class OverlayWindow(QWidget):
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.monitor = SystemMonitor()
        self.load_config()
        self.init_ui()
        self.start_timer()

    def load_config(self):
        self.config = self.config_manager.config
        self.lang = self.config.get("language", "es")
        self.trans = TRANSLATIONS.get(self.lang, TRANSLATIONS["en"])

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        if self.layout():
            QWidget().setLayout(self.layout()) # Clear existing layout
            
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.time_label = QLabel()
        self.cpu_label = QLabel()
        self.ram_label = QLabel()
        self.gpu_label = QLabel()

        self.apply_styles()

        for label in [self.time_label, self.cpu_label, self.ram_label, self.gpu_label]:
            layout.addWidget(label)

        self.update_position()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        bg_color = QColor(self.config.get("background_color", "#000000"))
        bg_color.setAlphaF(self.config.get("background_opacity", 0.5))
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

    def apply_styles(self):
        font = QFont(self.config.get("font_family", "Arial"), self.config.get("font_size", 14))
        color = self.config.get("text_color", "#FFFFFF")
        style = f"color: {color};"

        self.time_label.setVisible(self.config.get("show_time", True))
        self.cpu_label.setVisible(self.config.get("show_cpu", True))
        self.ram_label.setVisible(self.config.get("show_ram", True))
        self.gpu_label.setVisible(self.config.get("show_gpu", True))

        for label in [self.time_label, self.cpu_label, self.ram_label, self.gpu_label]:
            label.setFont(font)
            label.setStyleSheet(style)

        # Background is handled in paintEvent now
        self.update() # Trigger repaint
        
        self.adjustSize()
        self.update_position()

    def update_position(self):
        preset = self.config.get("position_preset", "custom")
        screen = QGuiApplication.primaryScreen().availableGeometry()
        
        x, y = 10, 10
        margin = 10
        
        if preset == "top-left":
            x, y = margin, margin
        elif preset == "top-center":
            x = (screen.width() - self.width()) // 2
            y = margin
        elif preset == "top-right":
            x = screen.width() - self.width() - margin
            y = margin
        elif preset == "bottom-left":
            x = margin
            y = screen.height() - self.height() - margin
        elif preset == "bottom-center":
            x = (screen.width() - self.width()) // 2
            y = screen.height() - self.height() - margin
        elif preset == "bottom-right":
            x = screen.width() - self.width() - margin
            y = screen.height() - self.height() - margin
        else: # custom
            x = self.config.get("position_x", 10)
            y = self.config.get("position_y", 10)
            
        self.move(x, y)

    def reload_settings(self):
        self.load_config()
        self.apply_styles()

    def start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(self.config.get("update_interval_ms", 1000))

    def update_stats(self):
        self.time_label.setText(f"{self.trans['time']}: {self.monitor.get_current_time()}")
        self.cpu_label.setText(f"{self.trans['cpu']}: {self.monitor.get_cpu_usage()}%")
        self.ram_label.setText(f"{self.trans['ram']}: {self.monitor.get_ram_usage()}%")
        gpu_name = self.monitor.get_gpu_name()
        self.gpu_label.setText(f"{gpu_name}: {self.monitor.get_gpu_usage():.1f}%")
