import sys
import shutil
import types
import setuptools
import json

# Patch distutils for GPUtil on Python 3.12+
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
from PySide6.QtGui import QIcon, QAction, QPixmap, QColor
from overlay_window import OverlayWindow
from settings_dialog import SettingsDialog
from translations import TRANSLATIONS

def create_tray_icon(app, window):
    tray_icon = QSystemTrayIcon(app)
    
    # Create a simple icon programmatically
    pixmap = QPixmap(16, 16)
    pixmap.fill(QColor("green"))
    icon = QIcon(pixmap)
    tray_icon.setIcon(icon)
    
    # Load config for language
    with open('config.json', 'r') as f:
        config = json.load(f)
    lang = config.get("language", "es")
    trans = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    menu = QMenu()
    
    settings_action = QAction(trans["settings"], app)
    settings_action.triggered.connect(lambda: open_settings(window))
    menu.addAction(settings_action)

    exit_action = QAction(trans["exit"], app)
    exit_action.triggered.connect(app.quit)
    menu.addAction(exit_action)

    tray_icon.setContextMenu(menu)
    tray_icon.show()
    return tray_icon

def open_settings(window):
    dialog = SettingsDialog(window.config)
    if dialog.exec():
        window.reload_settings()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    window = OverlayWindow()
    window.show()
    
    tray_icon = create_tray_icon(app, window)
    
    sys.exit(app.exec())
