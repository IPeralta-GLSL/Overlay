import json
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox, 
                               QSpinBox, QPushButton, QColorDialog, QSlider, 
                               QHBoxLayout, QLabel)
from PySide6.QtCore import Qt
from translations import TRANSLATIONS

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.current_lang = self.config.get("language", "es")
        self.trans = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
        self.setWindowTitle(self.trans["settings"])
        self.apply_stylesheet()
        self.init_ui()

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
            QComboBox, QSpinBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #ffffff;
                selection-background-color: #4CAF50;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #3c3c3c;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #4CAF50;
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Language
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["en", "es"])
        self.lang_combo.setCurrentText(self.current_lang)
        self.lang_combo.currentTextChanged.connect(self.on_language_change)
        form_layout.addRow(self.trans["language"], self.lang_combo)

        # Font Size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(self.config.get("font_size", 14))
        form_layout.addRow(self.trans["font_size"], self.font_size_spin)

        # Text Color
        self.text_color_btn = QPushButton(self.trans["pick_color"])
        self.text_color = self.config.get("text_color", "#FFFFFF")
        self.text_color_btn.setStyleSheet(f"background-color: {self.text_color}")
        self.text_color_btn.clicked.connect(lambda: self.pick_color("text"))
        form_layout.addRow(self.trans["text_color"], self.text_color_btn)

        # Background Color
        self.bg_color_btn = QPushButton(self.trans["pick_color"])
        self.bg_color = self.config.get("background_color", "#000000")
        self.bg_color_btn.setStyleSheet(f"background-color: {self.bg_color}")
        self.bg_color_btn.clicked.connect(lambda: self.pick_color("bg"))
        form_layout.addRow(self.trans["bg_color"], self.bg_color_btn)

        # Opacity
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(int(self.config.get("background_opacity", 0.5) * 100))
        form_layout.addRow(self.trans["opacity"], self.opacity_slider)

        layout.addLayout(form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton(self.trans["save"])
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton(self.trans["cancel"])
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def pick_color(self, target):
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            if target == "text":
                self.text_color = hex_color
                self.text_color_btn.setStyleSheet(f"background-color: {hex_color}")
            else:
                self.bg_color = hex_color
                self.bg_color_btn.setStyleSheet(f"background-color: {hex_color}")

    def on_language_change(self, text):
        # Ideally reload UI text immediately, but for simplicity require restart or save
        pass

    def save_settings(self):
        self.config["language"] = self.lang_combo.currentText()
        self.config["font_size"] = self.font_size_spin.value()
        self.config["text_color"] = self.text_color
        self.config["background_color"] = self.bg_color
        self.config["background_opacity"] = self.opacity_slider.value() / 100.0
        
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=4)
        
        self.accept()
