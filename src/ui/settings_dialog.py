from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                               QSpinBox, QPushButton, QColorDialog, QSlider,
                               QHBoxLayout, QLabel, QCheckBox, QGroupBox, 
                               QScrollArea, QWidget, QLineEdit, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase, QDesktopServices
from PySide6.QtCore import QUrl
from src.utils.translations import TRANSLATIONS
from src.core.system_monitor import SystemMonitor
from src.core.autostart_manager import AutostartManager
from src.core.update_checker import UpdateChecker
from src.core.config_manager import APP_VERSION

class SettingsDialog(QDialog):
    def __init__(self, config_manager, on_apply_callback=None, parent=None, overlay_window=None, hotkey_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.on_apply_callback = on_apply_callback
        self.overlay_window = overlay_window
        self.hotkey_manager = hotkey_manager
        self.current_lang = self.config_manager.get("language", "es")
        self.initialized = False
        self.autostart_manager = AutostartManager()
        self.update_checker = UpdateChecker("IPeralta-GLSL", "Overlay", APP_VERSION)
        self.update_checker.update_available.connect(self.on_update_available)
        self.update_checker.check_complete.connect(self.on_check_complete)
        self.apply_stylesheet()
        self.init_ui()
        self.retranslate_ui()
        self.initialized = True

        if self.overlay_window:
            self.overlay_window.positionChanged.connect(self.update_position_display)

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
            QComboBox, QSpinBox, QFontComboBox, QLineEdit {
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
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                color: #4CAF50;
                font-weight: bold;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2b2b2b;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4CAF50;
            }
            QScrollBar::add-line:vertical {
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                height: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def init_ui(self):
        main_layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        self.group_general = QGroupBox()
        general_layout = QFormLayout()

        self.lang_label = QLabel()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["en", "es"])
        self.lang_combo.setCurrentText(self.current_lang)
        self.lang_combo.currentTextChanged.connect(self.on_language_change)
        general_layout.addRow(self.lang_label, self.lang_combo)

        self.group_general.setLayout(general_layout)
        scroll_layout.addWidget(self.group_general)

        self.group_appearance = QGroupBox()
        appearance_layout = QFormLayout()

        self.font_family_label = QLabel()
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(QFontDatabase.families())
        self.font_family_combo.setCurrentText(self.config_manager.get("font_family", "Arial"))
        appearance_layout.addRow(self.font_family_label, self.font_family_combo)

        self.font_size_label = QLabel()
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(self.config_manager.get("font_size", 14))
        appearance_layout.addRow(self.font_size_label, self.font_size_spin)

        self.text_color_label = QLabel()
        self.text_color_btn = QPushButton()
        self.text_color = self.config_manager.get("text_color", "#FFFFFF")
        self.text_color_btn.setStyleSheet(f"background-color: {self.text_color}")
        self.text_color_btn.clicked.connect(lambda: self.pick_color("text"))
        appearance_layout.addRow(self.text_color_label, self.text_color_btn)

        self.bg_color_label = QLabel()
        self.bg_color_btn = QPushButton()
        self.bg_color = self.config_manager.get("background_color", "#000000")
        self.bg_color_btn.setStyleSheet(f"background-color: {self.bg_color}")
        self.bg_color_btn.clicked.connect(lambda: self.pick_color("bg"))
        appearance_layout.addRow(self.bg_color_label, self.bg_color_btn)

        self.opacity_label = QLabel()
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(int(self.config_manager.get("background_opacity", 0.5) * 100))
        appearance_layout.addRow(self.opacity_label, self.opacity_slider)

        self.group_appearance.setLayout(appearance_layout)
        scroll_layout.addWidget(self.group_appearance)

        self.group_position = QGroupBox()
        position_layout = QFormLayout()

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
        position_layout.addRow(self.preset_label, self.preset_combo)

        self.lock_pos_check = QCheckBox()
        self.lock_pos_check.setChecked(self.config_manager.get("position_locked", False))
        self.lock_pos_check.toggled.connect(lambda: self.save_settings())
        position_layout.addRow("", self.lock_pos_check)

        self.custom_pos_layout = QHBoxLayout()

        self.pos_label = QLabel()
        self.pos_x_label = QLabel()
        self.pos_x_spin = QSpinBox()
        self.pos_x_spin.setRange(0, 3000)
        self.pos_x_spin.setValue(self.config_manager.get("position_x", 10))

        self.pos_y_label = QLabel()
        self.pos_y_spin = QSpinBox()
        self.pos_y_spin.setRange(0, 2000)
        self.pos_y_spin.setValue(self.config_manager.get("position_y", 10))

        self.custom_pos_layout.addWidget(self.pos_label)
        self.custom_pos_layout.addWidget(self.pos_x_label)
        self.custom_pos_layout.addWidget(self.pos_x_spin)
        self.custom_pos_layout.addWidget(self.pos_y_label)
        self.custom_pos_layout.addWidget(self.pos_y_spin)
        self.custom_pos_layout.addStretch()

        position_layout.addRow(self.custom_pos_layout)

        self.group_position.setLayout(position_layout)
        scroll_layout.addWidget(self.group_position)

        self.group_content = QGroupBox()
        content_layout = QVBoxLayout()

        self.group_components = QGroupBox()
        components_layout = QFormLayout()

        self.show_time_check = QCheckBox()
        self.show_time_check.setChecked(self.config_manager.get("show_time", True))
        components_layout.addRow("", self.show_time_check)

        self.show_cpu_check = QCheckBox()
        self.show_cpu_check.setChecked(self.config_manager.get("show_cpu", True))
        components_layout.addRow("", self.show_cpu_check)

        self.show_ram_check = QCheckBox()
        self.show_ram_check.setChecked(self.config_manager.get("show_ram", True))
        components_layout.addRow("", self.show_ram_check)

        self.show_gpu_check = QCheckBox()
        self.show_gpu_check.setChecked(self.config_manager.get("show_gpu", True))
        components_layout.addRow("", self.show_gpu_check)

        self.group_components.setLayout(components_layout)
        content_layout.addWidget(self.group_components)

        self.group_details = QGroupBox()
        details_layout = QFormLayout()

        self.show_cpu_name_check = QCheckBox()
        self.show_cpu_name_check.setChecked(self.config_manager.get("show_cpu_name", False))
        details_layout.addRow("", self.show_cpu_name_check)

        self.show_cpu_manufacturer_check = QCheckBox()
        self.show_cpu_manufacturer_check.setChecked(self.config_manager.get("show_cpu_manufacturer", False))
        details_layout.addRow("", self.show_cpu_manufacturer_check)

        self.show_gpu_name_check = QCheckBox()
        self.show_gpu_name_check.setChecked(self.config_manager.get("show_gpu_name", False))
        details_layout.addRow("", self.show_gpu_name_check)

        self.show_gpu_manufacturer_check = QCheckBox()
        self.show_gpu_manufacturer_check.setChecked(self.config_manager.get("show_gpu_manufacturer", False))
        details_layout.addRow("", self.show_gpu_manufacturer_check)

        self.group_details.setLayout(details_layout)
        content_layout.addWidget(self.group_details)

        self.group_temps = QGroupBox()
        temps_layout = QFormLayout()

        self.show_cpu_temp_check = QCheckBox()
        self.show_cpu_temp_check.setChecked(self.config_manager.get("show_cpu_temp", False))
        temps_layout.addRow("", self.show_cpu_temp_check)

        self.show_gpu_temp_check = QCheckBox()
        self.show_gpu_temp_check.setChecked(self.config_manager.get("show_gpu_temp", False))
        temps_layout.addRow("", self.show_gpu_temp_check)

        self.group_temps.setLayout(temps_layout)
        content_layout.addWidget(self.group_temps)

        self.monitor = SystemMonitor()
        gpu_info = self.monitor.get_gpu_info()
        self.gpu_checks = {}

        gpu_visibility = self.config_manager.get("gpu_visibility", {})

        if gpu_info:
            gpu_group = QGroupBox("GPUs")
            gpu_layout = QFormLayout()
            for name, _ in gpu_info:
                check = QCheckBox(name)
                is_visible = gpu_visibility.get(name, True)
                check.setChecked(is_visible)
                gpu_layout.addRow("", check)
                self.gpu_checks[name] = check
                check.toggled.connect(lambda: self.save_settings())
            gpu_group.setLayout(gpu_layout)
            content_layout.addWidget(gpu_group)

        self.group_content.setLayout(content_layout)
        scroll_layout.addWidget(self.group_content)

        self.group_advanced = QGroupBox()
        advanced_layout = QFormLayout()

        self.update_interval_label = QLabel()
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(100, 10000)
        self.update_interval_spin.setSingleStep(100)
        self.update_interval_spin.setValue(self.config_manager.get("update_interval_ms", 1000))
        advanced_layout.addRow(self.update_interval_label, self.update_interval_spin)

        self.hotkey_enabled_check = QCheckBox()
        self.hotkey_enabled_check.setChecked(self.config_manager.get("hotkey_enabled", True))
        advanced_layout.addRow("", self.hotkey_enabled_check)

        self.hotkey_label = QLabel()
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setText(self.config_manager.get("hotkey_toggle", "ctrl+shift+o"))
        advanced_layout.addRow(self.hotkey_label, self.hotkey_edit)

        self.autostart_check = QCheckBox()
        self.autostart_check.setChecked(self.autostart_manager.is_enabled())
        advanced_layout.addRow("", self.autostart_check)

        self.check_updates_check = QCheckBox()
        self.check_updates_check.setChecked(self.config_manager.get("check_updates", True))
        advanced_layout.addRow("", self.check_updates_check)

        self.check_updates_btn = QPushButton()
        self.check_updates_btn.clicked.connect(self.check_for_updates)
        advanced_layout.addRow("", self.check_updates_btn)

        self.group_advanced.setLayout(advanced_layout)
        scroll_layout.addWidget(self.group_advanced)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        self.font_family_combo.currentTextChanged.connect(lambda: self.save_settings())
        self.font_size_spin.valueChanged.connect(lambda: self.save_settings())
        self.pos_x_spin.valueChanged.connect(lambda: self.save_settings())
        self.pos_y_spin.valueChanged.connect(lambda: self.save_settings())
        self.opacity_slider.valueChanged.connect(lambda: self.save_settings())
        self.show_time_check.toggled.connect(lambda: self.save_settings())
        self.show_cpu_check.toggled.connect(lambda: self.save_settings())
        self.show_ram_check.toggled.connect(lambda: self.save_settings())
        self.show_gpu_check.toggled.connect(lambda: self.save_settings())
        self.show_cpu_name_check.toggled.connect(lambda: self.save_settings())
        self.show_cpu_manufacturer_check.toggled.connect(lambda: self.save_settings())
        self.show_ram_check.toggled.connect(lambda: self.save_settings())
        self.show_gpu_name_check.toggled.connect(lambda: self.save_settings())
        self.show_gpu_manufacturer_check.toggled.connect(lambda: self.save_settings())
        self.show_cpu_temp_check.toggled.connect(lambda: self.save_settings())
        self.show_gpu_temp_check.toggled.connect(lambda: self.save_settings())
        self.update_interval_spin.valueChanged.connect(lambda: self.save_settings())
        self.hotkey_enabled_check.toggled.connect(lambda: self.save_settings())
        self.hotkey_edit.editingFinished.connect(lambda: self.save_settings())
        self.autostart_check.toggled.connect(self.on_autostart_changed)
        self.check_updates_check.toggled.connect(lambda: self.save_settings())

    def retranslate_ui(self):
        trans = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
        self.setWindowTitle(trans["settings"])

        self.group_general.setTitle(trans["tab_general"])
        self.group_appearance.setTitle(trans["tab_appearance"])
        self.group_position.setTitle(trans["tab_position"])
        self.group_content.setTitle(trans["tab_content"])
        self.group_advanced.setTitle(trans["tab_advanced"])

        self.lang_label.setText(trans["language"])
        self.preset_label.setText(trans["position_preset"])
        self.preset_combo.setItemText(0, trans["preset_custom"])
        self.preset_combo.setItemText(1, trans["preset_top_left"])
        self.preset_combo.setItemText(2, trans["preset_top_center"])
        self.preset_combo.setItemText(3, trans["preset_top_right"])
        self.preset_combo.setItemText(4, trans["preset_bottom_left"])
        self.preset_combo.setItemText(5, trans["preset_bottom_center"])
        self.preset_combo.setItemText(6, trans["preset_bottom_right"])
        self.lock_pos_check.setText(trans.get("lock_position", "Lock Position"))
        self.pos_label.setText(trans["position_label"])
        self.pos_x_label.setText(trans["axis_x"])
        self.pos_y_label.setText(trans["axis_y"])
        self.font_family_label.setText(trans["font_family"])
        self.font_size_label.setText(trans["font_size"])
        self.text_color_label.setText(trans["text_color"])
        self.text_color_btn.setText(trans["pick_color"])
        self.bg_color_label.setText(trans["bg_color"])
        self.bg_color_btn.setText(trans["pick_color"])
        self.opacity_label.setText(trans["opacity"])
        self.show_time_check.setText(trans["show_time"])
        self.show_cpu_check.setText(trans["show_cpu"])
        self.show_ram_check.setText(trans["show_ram"])
        self.show_gpu_check.setText(trans["show_gpu"])
        self.show_cpu_name_check.setText(trans["show_cpu_name"])
        self.show_cpu_manufacturer_check.setText(trans["show_cpu_manufacturer"])
        self.show_ram_check.setText(trans["show_ram"])
        self.show_gpu_name_check.setText(trans["show_gpu_name"])
        self.show_gpu_manufacturer_check.setText(trans["show_gpu_manufacturer"])
        self.show_cpu_temp_check.setText(trans["show_cpu_temp"])
        self.show_gpu_temp_check.setText(trans["show_gpu_temp"])

        self.group_components.setTitle(trans["cat_components"])
        self.group_details.setTitle(trans["cat_details"])
        self.group_temps.setTitle(trans["cat_temperatures"])

        self.update_interval_label.setText(trans["update_interval"])
        self.hotkey_label.setText(trans["hotkey_toggle"])
        self.hotkey_enabled_check.setText(trans["hotkey_enabled"])
        self.autostart_check.setText(trans["autostart"])
        self.check_updates_check.setText(trans["check_updates"])
        self.check_updates_btn.setText(trans["check_now"])

    def on_preset_change(self, index):
        key = self.preset_combo.itemData(index)
        is_custom = (key == "custom")
        self.pos_x_spin.setEnabled(is_custom)
        self.pos_y_spin.setEnabled(is_custom)
        self.save_settings()

    def update_position_display(self, x, y):
        self.pos_x_spin.blockSignals(True)
        self.pos_y_spin.blockSignals(True)
        self.pos_x_spin.setValue(x)
        self.pos_y_spin.setValue(y)
        self.pos_x_spin.blockSignals(False)
        self.pos_y_spin.blockSignals(False)

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
            self.save_settings()

    def on_language_change(self, text):
        self.current_lang = text
        self.retranslate_ui()
        self.save_settings()

    def on_autostart_changed(self, checked):
        if checked:
            self.autostart_manager.enable()
        else:
            self.autostart_manager.disable()
        self.save_settings()

    def check_for_updates(self):
        self.check_updates_btn.setEnabled(False)
        self.update_checker.check_for_updates()

    def on_update_available(self, version, notes):
        trans = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
        msg = QMessageBox(self)
        msg.setWindowTitle(trans["update_available"])
        msg.setText(trans["update_message"].format(version=version))
        msg.setInformativeText(notes[:500] if notes else "")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText(trans["download"])
        msg.button(QMessageBox.No).setText(trans["later"])
        if msg.exec() == QMessageBox.Yes:
            QDesktopServices.openUrl(QUrl(self.update_checker.get_download_url()))

    def on_check_complete(self, has_update):
        self.check_updates_btn.setEnabled(True)
        if not has_update:
            trans = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
            QMessageBox.information(self, trans["no_updates"], trans["up_to_date"])

    def save_settings(self):
        if not hasattr(self, 'initialized') or not self.initialized:
            return

        self.config_manager.set("language", self.lang_combo.currentText())
        self.config_manager.set("position_preset", self.preset_combo.currentData())
        self.config_manager.set("position_locked", self.lock_pos_check.isChecked())
        self.config_manager.set("font_family", self.font_family_combo.currentText())
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
        self.config_manager.set("show_cpu_name", self.show_cpu_name_check.isChecked())
        self.config_manager.set("show_cpu_manufacturer", self.show_cpu_manufacturer_check.isChecked())
        self.config_manager.set("show_ram", self.show_ram_check.isChecked())
        self.config_manager.set("show_gpu_name", self.show_gpu_name_check.isChecked())
        self.config_manager.set("show_gpu_manufacturer", self.show_gpu_manufacturer_check.isChecked())
        self.config_manager.set("show_cpu_temp", self.show_cpu_temp_check.isChecked())
        self.config_manager.set("show_gpu_temp", self.show_gpu_temp_check.isChecked())
        self.config_manager.set("update_interval_ms", self.update_interval_spin.value())
        self.config_manager.set("hotkey_enabled", self.hotkey_enabled_check.isChecked())
        self.config_manager.set("hotkey_toggle", self.hotkey_edit.text())
        self.config_manager.set("autostart", self.autostart_check.isChecked())
        self.config_manager.set("check_updates", self.check_updates_check.isChecked())

        gpu_visibility = {}
        for name, check in self.gpu_checks.items():
            gpu_visibility[name] = check.isChecked()
        self.config_manager.set("gpu_visibility", gpu_visibility)

        self.config_manager.save_config()

        if self.hotkey_manager and self.hotkey_enabled_check.isChecked():
            self.hotkey_manager.register_hotkey(self.hotkey_edit.text())
        elif self.hotkey_manager:
            self.hotkey_manager.unregister_hotkey()

        if self.on_apply_callback:
            self.on_apply_callback()
