import sys
import shutil
import types
import setuptools
import json
import os
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if sys.platform == 'win32' and not is_admin():
        script = os.path.abspath(sys.argv[0])
        python_exe = sys.executable
        pythonw_exe = python_exe.replace('python.exe', 'pythonw.exe')
        if os.path.exists(pythonw_exe):
            python_exe = pythonw_exe
        working_dir = os.path.dirname(script)
        args = f'"{script}"'
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", python_exe, args, working_dir, 1
        )
        sys.exit(0)

run_as_admin()

try:
    from distutils import spawn
except ImportError:
    distutils = types.ModuleType("distutils")
    spawn = types.ModuleType("distutils.spawn")

    def find_executable(executable, path=None):
        return shutil.which(executable, path=path)

    spawn.find_executable = find_executable
    distutils.spawn = spawn
    sys.modules["distutils"] = distutils
    sys.modules["distutils.spawn"] = spawn

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from src.ui.overlay_window import OverlayWindow
from src.ui.settings_dialog import SettingsDialog
from src.core.config_manager import ConfigManager
from src.core.hotkey_manager import HotkeyManager
from src.core.update_checker import UpdateChecker
from src.core.config_manager import APP_VERSION
from src.utils.translations import TRANSLATIONS

def create_tray_icon(app, window, config_manager, hotkey_manager):
    tray_icon = QSystemTrayIcon(app)

    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(base_path, "overlay.svg")
    icon = QIcon(icon_path)
    tray_icon.setIcon(icon)
    app.setWindowIcon(icon)

    lang = config_manager.get("language", "es")
    trans = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    menu = QMenu()

    settings_action = QAction(trans["settings"], app)
    settings_action.triggered.connect(lambda: open_settings(window, config_manager, hotkey_manager))
    menu.addAction(settings_action)

    exit_action = QAction(trans["exit"], app)
    exit_action.triggered.connect(app.quit)
    menu.addAction(exit_action)

    tray_icon.setContextMenu(menu)

    tray_icon.activated.connect(lambda reason: open_settings(window, config_manager, hotkey_manager) if reason == QSystemTrayIcon.Trigger else None)

    tray_icon.show()
    return tray_icon

_settings_dialog = None

def _reset_settings_dialog():
    global _settings_dialog
    _settings_dialog = None

def open_settings(window, config_manager, hotkey_manager):
    global _settings_dialog
    if _settings_dialog is None:
        _settings_dialog = SettingsDialog(
            config_manager,
            on_apply_callback=window.reload_settings,
            overlay_window=window,
            hotkey_manager=hotkey_manager
        )
        _settings_dialog.finished.connect(_reset_settings_dialog)
        _settings_dialog.show()
    else:
        _settings_dialog.show()
        _settings_dialog.raise_()
        _settings_dialog.activateWindow()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config_manager = ConfigManager()
    window = OverlayWindow(config_manager)
    
    hotkey_manager = HotkeyManager()
    hotkey_manager.toggle_overlay.connect(window.toggle_visibility)
    
    if config_manager.get("hotkey_enabled", True):
        hotkey_manager.register_hotkey(config_manager.get("hotkey_toggle", "ctrl+shift+o"))
    
    window.show()

    tray_icon = create_tray_icon(app, window, config_manager, hotkey_manager)

    if config_manager.get("check_updates", True):
        update_checker = UpdateChecker("IPeralta-GLSL", "Overlay", APP_VERSION)
        update_checker.check_for_updates()

    open_settings(window, config_manager, hotkey_manager)

    sys.exit(app.exec())
