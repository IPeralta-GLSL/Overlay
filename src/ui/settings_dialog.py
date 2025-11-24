from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox, 
                               QSpinBox, QPushButton, QColorDialog, QSlider, 
                               QHBoxLayout, QLabel, QFontComboBox, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from src.utils.translations import TRANSLATIONS

class SettingsDialog(QDialog):
    def __init__(self, config_manager, on_apply_callback=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.on_apply_callback = on_apply_callback
        self.current_lang = self.config_manager.get("language", "es")
        self.apply_stylesheet()
        self.init_ui()
        self.retranslate_ui()
        
        # Trigger initial state for preset
        self.on_preset_change(self.preset_combo.currentIndex())

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
            QComboBox, QSpinBox, QFontComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 4px;
            }
            QComboBox::drop-down, QFontComboBox::drop-down {
                border: 0px;
            }
            QComboBox QAbstractItemView, QFontComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #ffffff;
                selection-background-color: #4CAF50;
            }
            QCheckBox {
                color: #ffffff;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 1px solid #4CAF50;
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
        self.form_layout = QFormLayout()

        # Language
        self.lang_label = QLabel()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["en", "es"])
        self.lang_combo.setCurrentText(self.current_lang)
        self.lang_combo.currentTextChanged.connect(self.on_language_change)
        self.form_layout.addRow(self.lang_label, self.lang_combo)

        # Position Preset
        self.preset_label = QLabel()
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("custom", "custom")
        self.preset_combo.addItem("top-left", "top-left")
        self.preset_combo.addItem("top-center", "top-center")
        self.preset_combo.addItem("top-right", "top-right")
        self.preset_combo.addItem("bottom-left", "bottom-left")
        self.preset_combo.addItem("bottom-center", "bottom-center")
        self.preset_combo.addItem("bottom-right", "bottom-right")
        
        current_preset = self.config_manager.get("position_preset", "custom")
        index = self.preset_combo.findData(current_preset)
        if index >= 0:
            self.preset_combo.setCurrentIndex(index)
            
        self.preset_combo.currentIndexChanged.connect(self.on_preset_change)
        self.form_layout.addRow(self.preset_label, self.preset_combo)

        # Custom Position (X, Y)
        self.custom_pos_layout = QHBoxLayout()
        
        self.pos_x_label = QLabel()
        self.pos_x_spin = QSpinBox()
        self.pos_x_spin.setRange(0, 3000)
        self.pos_x_spin.setValue(self.config_manager.get("position_x", 10))
        
        self.pos_y_label = QLabel()
        self.pos_y_spin = QSpinBox()
        self.pos_y_spin.setRange(0, 2000)
        self.pos_y_spin.setValue(self.config_manager.get("position_y", 10))

        self.custom_pos_layout.addWidget(self.pos_x_label)
        self.custom_pos_layout.addWidget(self.pos_x_spin)
        self.custom_pos_layout.addWidget(self.pos_y_label)
        self.custom_pos_layout.addWidget(self.pos_y_spin)
        
        self.form_layout.addRow(self.custom_pos_layout)

        # Font Family
        self.font_family_label = QLabel()
        self.font_family_combo = QFontComboBox()
        self.font_family_combo.setCurrentFont(QFont(self.config_manager.get("font_family", "Arial")))
        self.form_layout.addRow(self.font_family_label, self.font_family_combo)

        # Font Size
        self.font_size_label = QLabel()
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(self.config_manager.get("font_size", 14))
        self.form_layout.addRow(self.font_size_label, self.font_size_spin)

        # Text Color
        self.text_color_label = QLabel()
        self.text_color_btn = QPushButton()
        self.text_color = self.config_manager.get("text_color", "#FFFFFF")
        self.text_color_btn.setStyleSheet(f"background-color: {self.text_color}")
        self.text_color_btn.clicked.connect(lambda: self.pick_color("text"))
        self.form_layout.addRow(self.text_color_label, self.text_color_btn)

        # Background Color
        self.bg_color_label = QLabel()
        self.bg_color_btn = QPushButton()
        self.bg_color = self.config_manager.get("background_color", "#000000")
        self.bg_color_btn.setStyleSheet(f"background-color: {self.bg_color}")
        self.bg_color_btn.clicked.connect(lambda: self.pick_color("bg"))
        self.form_layout.addRow(self.bg_color_label, self.bg_color_btn)

        # Opacity
        self.opacity_label = QLabel()
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(int(self.config_manager.get("background_opacity", 0.5) * 100))
        self.form_layout.addRow(self.opacity_label, self.opacity_slider)

        # Visibility Toggles
        self.show_time_check = QCheckBox()
        self.show_time_check.setChecked(self.config_manager.get("show_time", True))
        self.form_layout.addRow("", self.show_time_check)

        self.show_cpu_check = QCheckBox()
        self.show_cpu_check.setChecked(self.config_manager.get("show_cpu", True))
        self.form_layout.addRow("", self.show_cpu_check)

        self.show_ram_check = QCheckBox()
        self.show_ram_check.setChecked(self.config_manager.get("show_ram", True))
        self.form_layout.addRow("", self.show_ram_check)

        self.show_gpu_check = QCheckBox()
        self.show_gpu_check.setChecked(self.config_manager.get("show_gpu", True))
        self.form_layout.addRow("", self.show_gpu_check)

        layout.addLayout(self.form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton()
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def retranslate_ui(self):
        trans = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
        self.setWindowTitle(trans["settings"])
        self.lang_label.setText(trans["language"])
        self.preset_label.setText(trans["position_preset"])
        self.preset_combo.setItemText(0, trans["preset_custom"])
        self.preset_combo.setItemText(1, trans["preset_top_left"])
        self.preset_combo.setItemText(2, trans["preset_top_center"])
        self.preset_combo.setItemText(3, trans["preset_top_right"])
        self.preset_combo.setItemText(4, trans["preset_bottom_left"])
        self.preset_combo.setItemText(5, trans["preset_bottom_center"])
        self.preset_combo.setItemText(6, trans["preset_bottom_right"])
        self.font_family_label.setText(trans["font_family"])
        self.font_size_label.setText(trans["font_size"])
        self.pos_x_label.setText(trans["position_x"])
        self.pos_y_label.setText(trans["position_y"])
        self.text_color_label.setText(trans["text_color"])
        self.text_color_btn.setText(trans["pick_color"])
        self.bg_color_label.setText(trans["bg_color"])
        self.bg_color_btn.setText(trans["pick_color"])
        self.opacity_label.setText(trans["opacity"])
        self.show_time_check.setText(trans["show_time"])
        self.show_cpu_check.setText(trans["show_cpu"])
        self.show_ram_check.setText(trans["show_ram"])
        self.show_gpu_check.setText(trans["show_gpu"])
        self.save_btn.setText(trans["save"])
        self.cancel_btn.setText(trans["cancel"])

    def on_preset_change(self, index):
        key = self.preset_combo.itemData(index)
        is_custom = (key == "custom")
        self.pos_x_spin.setEnabled(is_custom)
        self.pos_y_spin.setEnabled(is_custom)

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
        self.current_lang = text
        self.retranslate_ui()

    def save_settings(self):
        self.config_manager.set("language", self.lang_combo.currentText())
        self.config_manager.set("position_preset", self.preset_combo.currentData())
        self.config_manager.set("font_family", self.font_family_combo.currentFont().family())
        self.config_manager.set("font_size", self.font_size_spin.value())
        self.config_manager.set("position_x", self.pos_x_spin.value())
        self.config_manager.set("position_y", self.pos_y_spin.value())
        self.config_manager.set("text_color", self.text_color)
        self.config_manager.set("background_color", self.bg_color)
        self.config_manager.set("background_opacity", self.opacity_slider.value() / 100.0)
        self.config_manager.set("show_time", self.show_time_check.isChecked())
        self.config_manager.set("show_cpu", self.show_cpu_check.isChecked())
        self.config_manager.set("show_ram", self.show_ram_check.isChecked())
        self.config_manager.set("show_gpu", self.show_gpu_check.isChecked())
        self.config_manager.save_config()
        
        if self.on_apply_callback:
            self.on_apply_callback()
        # self.accept() # Do not close on apply
