from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QGuiApplication, QPainter, QBrush
from src.core.system_monitor import SystemMonitor
from src.utils.translations import TRANSLATIONS

class OverlayWindow(QWidget):
    positionChanged = Signal(int, int)

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
            QWidget().setLayout(self.layout())

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.time_label = QLabel()
        self.cpu_label = QLabel()
        self.cpu_temp_label = QLabel()
        self.ram_label = QLabel()
        self.gpu_label = QLabel()
        self.gpu_temp_label = QLabel()

        for label in [self.time_label, self.cpu_label, self.cpu_temp_label,
                      self.ram_label, self.gpu_label, self.gpu_temp_label]:
            layout.addWidget(label)

        self.apply_styles()
        self.update_stats()
        self.adjustSize()
        QTimer.singleShot(100, self.update_position)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        bg_color = QColor(self.config.get("background_color", "#000000"))
        bg_color.setAlphaF(self.config.get("background_opacity", 0.5))
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

    def apply_styles(self):
        self.font = QFont(self.config.get("font_family", "Arial"), self.config.get("font_size", 14))
        self.base_color = self.config.get("text_color", "#FFFFFF")
        self.dynamic_colors = self.config.get("dynamic_colors", False)
        self.color_only_value = self.config.get("color_only_value", False)
        self.color_low = self.config.get("color_low", "#4CAF50")
        self.color_medium = self.config.get("color_medium", "#FFC107")
        self.color_high = self.config.get("color_high", "#F44336")

        self.time_label.setVisible(self.config.get("show_time", True))
        self.cpu_label.setVisible(self.config.get("show_cpu", True))
        self.cpu_temp_label.setVisible(self.config.get("show_cpu_temp", False))
        self.ram_label.setVisible(self.config.get("show_ram", True))
        self.gpu_temp_label.setVisible(self.config.get("show_gpu_temp", False))

        for label in [self.time_label, self.cpu_label, self.cpu_temp_label,
                      self.ram_label, self.gpu_label, self.gpu_temp_label]:
            label.setFont(self.font)
            label.setStyleSheet(f"color: {self.base_color};")

        self.update()
        self.adjustSize()
        self.update_position()

    def _format_with_color(self, label_text, value_text, color):
        if not self.dynamic_colors:
            return f"{label_text}: {value_text}", self.base_color
        if self.color_only_value:
            return f"<span style='color:{self.base_color}'>{label_text}: </span><span style='color:{color}'>{value_text}</span>", None
        return f"{label_text}: {value_text}", color

    def _apply_label_style(self, label, text, color):
        if color is None:
            label.setTextFormat(Qt.RichText)
            label.setText(text)
        else:
            label.setTextFormat(Qt.PlainText)
            label.setText(text)
            label.setStyleSheet(f"color: {color};")

    def _get_color_for_percentage(self, percentage):
        if not self.dynamic_colors:
            return self.base_color
        if percentage < 50:
            return self.color_low
        elif percentage < 80:
            return self.color_medium
        else:
            return self.color_high

    def _get_color_for_temp(self, temp):
        if not self.dynamic_colors:
            return self.base_color
        if temp < 50:
            return self.color_low
        elif temp < 75:
            return self.color_medium
        else:
            return self.color_high

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
        else:
            x = self.config.get("position_x", 10)
            y = self.config.get("position_y", 10)

        self.move(x, y)

    def reload_settings(self):
        self.load_config()
        self.apply_styles()
        new_interval = self.config.get("update_interval_ms", 1000)
        if self.timer.interval() != new_interval:
            self.timer.setInterval(new_interval)

    def start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(self.config.get("update_interval_ms", 1000))

    def _clean_manufacturer(self, name, show_manufacturer):
        if show_manufacturer:
            return name

        manufacturers = ["Intel(R)", "Intel", "AMD", "NVIDIA", "Nvidia", "GeForce", "Radeon"]
        cleaned_name = name
        for m in manufacturers:
            if cleaned_name.lower().startswith(m.lower()):
                cleaned_name = cleaned_name[len(m):].strip()

        for m in manufacturers:
            if cleaned_name.lower().startswith(m.lower()):
                cleaned_name = cleaned_name[len(m):].strip()

        artifacts = ["(R)", "(TM)", "Core(TM)"]
        for a in artifacts:
            if cleaned_name.lower().startswith(a.lower()):
                cleaned_name = cleaned_name[len(a):].strip()

        return cleaned_name if cleaned_name else name

    def update_stats(self):
        self.time_label.setText(f"{self.trans['time']}: {self.monitor.get_current_time()}")
        self.time_label.setStyleSheet(f"color: {self.base_color};")

        show_cpu_name = self.config.get("show_cpu_name", False)
        show_cpu_manufacturer = self.config.get("show_cpu_manufacturer", True)

        if show_cpu_name:
            cpu_name = self.monitor.cpu_name
            cpu_label_text = self._clean_manufacturer(cpu_name, show_cpu_manufacturer)
        else:
            cpu_label_text = self.trans['cpu']

        cpu_usage = self.monitor.get_cpu_usage()
        cpu_color = self._get_color_for_percentage(cpu_usage)
        text, color = self._format_with_color(cpu_label_text, f"{cpu_usage}%", cpu_color)
        self._apply_label_style(self.cpu_label, text, color)

        if self.config.get("show_cpu_temp", False):
            cpu_temp = self.monitor.get_cpu_temperature()
            if cpu_temp is not None:
                temp_color = self._get_color_for_temp(cpu_temp)
                text, color = self._format_with_color(self.trans.get('cpu_temp', 'CPU Temp'), f"{cpu_temp:.1f}°C", temp_color)
                self._apply_label_style(self.cpu_temp_label, text, color)
            else:
                self.cpu_temp_label.setText(f"{self.trans.get('cpu_temp', 'CPU Temp')}: N/A")
                self.cpu_temp_label.setStyleSheet(f"color: {self.base_color};")
            self.cpu_temp_label.setVisible(True)
        else:
            self.cpu_temp_label.setVisible(False)

        ram_usage = self.monitor.get_ram_usage()
        ram_color = self._get_color_for_percentage(ram_usage)
        text, color = self._format_with_color(self.trans['ram'], f"{ram_usage}%", ram_color)
        self._apply_label_style(self.ram_label, text, color)

        if not self.config.get("show_gpu", True):
            self.gpu_label.setVisible(False)
            self.gpu_temp_label.setVisible(False)
            self.adjustSize()
            return

        gpu_info = self.monitor.get_gpu_info()
        gpu_visibility = self.config.get("gpu_visibility", {})
        show_gpu_name = self.config.get("show_gpu_name", False)
        show_gpu_manufacturer = self.config.get("show_gpu_manufacturer", False)

        visible_gpus = []
        gpu_colors = []
        if gpu_info:
            for i, (name, usage) in enumerate(gpu_info):
                if gpu_visibility.get(name, True):
                    if show_gpu_name:
                        display_name = self._clean_manufacturer(name, show_gpu_manufacturer)
                    else:
                        display_name = f"GPU {i + 1}" if len(gpu_info) > 1 else "GPU"
                    gpu_color = self._get_color_for_percentage(usage)
                    text, color = self._format_with_color(display_name, f"{usage:.1f}%", gpu_color)
                    visible_gpus.append(text)
                    gpu_colors.append(color)

            if visible_gpus:
                if gpu_colors and gpu_colors[0] is None:
                    self.gpu_label.setTextFormat(Qt.RichText)
                    self.gpu_label.setText("<br>".join(visible_gpus))
                else:
                    self.gpu_label.setTextFormat(Qt.PlainText)
                    self.gpu_label.setText("\n".join(visible_gpus))
                    if gpu_colors:
                        self.gpu_label.setStyleSheet(f"color: {gpu_colors[0]};")
                self.gpu_label.setVisible(True)
            else:
                self.gpu_label.setVisible(False)
        else:
            self.gpu_label.setVisible(False)

        if self.config.get("show_gpu_temp", False):
            gpu_temps = self.monitor.get_gpu_temperature()
            if gpu_temps:
                temp_texts = []
                temp_colors = []
                for t in gpu_temps:
                    temp_color = self._get_color_for_temp(t)
                    text, color = self._format_with_color(self.trans.get('gpu_temp', 'GPU Temp'), f"{t:.1f}°C", temp_color)
                    temp_texts.append(text)
                    temp_colors.append(color)
                if temp_colors and temp_colors[0] is None:
                    self.gpu_temp_label.setTextFormat(Qt.RichText)
                    self.gpu_temp_label.setText("<br>".join(temp_texts))
                else:
                    self.gpu_temp_label.setTextFormat(Qt.PlainText)
                    self.gpu_temp_label.setText("\n".join(temp_texts))
                    if temp_colors:
                        self.gpu_temp_label.setStyleSheet(f"color: {temp_colors[0]};")
                self.gpu_temp_label.setVisible(True)
            else:
                self.gpu_temp_label.setVisible(False)
        else:
            self.gpu_temp_label.setVisible(False)

        self.adjustSize()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            preset = self.config.get("position_preset", "custom")
            locked = self.config.get("position_locked", False)
            if preset == "custom" and not locked:
                self.dragging = True
                self.drag_position = event.position().toPoint()
                event.accept()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'dragging') and self.dragging:
            if event.buttons() & Qt.LeftButton:
                new_pos = event.globalPosition().toPoint() - self.drag_position
                self.move(new_pos)
                self.positionChanged.emit(new_pos.x(), new_pos.y())
                event.accept()

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'dragging') and self.dragging:
            self.dragging = False
            new_pos = self.pos()
            self.config_manager.set("position_x", new_pos.x())
            self.config_manager.set("position_y", new_pos.y())
            self.config_manager.save_config()
            self.positionChanged.emit(new_pos.x(), new_pos.y())
            event.accept()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
