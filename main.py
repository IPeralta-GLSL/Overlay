import sys 
import shutil 
import types 
import setuptools 
import json 
import os

try :
    from distutils import spawn 
except ImportError :
    distutils =types .ModuleType ("distutils")
    spawn =types .ModuleType ("distutils.spawn")

    def find_executable (executable ,path =None ):
        return shutil .which (executable ,path =path )

    spawn .find_executable =find_executable 
    distutils .spawn =spawn 
    sys .modules ["distutils"]=distutils 
    sys .modules ["distutils.spawn"]=spawn 

from PySide6 .QtWidgets import QApplication ,QSystemTrayIcon ,QMenu 
from PySide6 .QtGui import QIcon ,QAction ,QPixmap ,QColor 
from src .ui .overlay_window import OverlayWindow 
from src .ui .settings_dialog import SettingsDialog 
from src .core .config_manager import ConfigManager 
from src .utils .translations import TRANSLATIONS 

def create_tray_icon (app ,window ,config_manager ):
    tray_icon =QSystemTrayIcon (app )

    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        if os.path.exists(os.path.join(base_path, "_internal")):
            base_path = os.path.join(base_path, "_internal")
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(base_path, "overlay.svg")
    icon = QIcon(icon_path)
    tray_icon .setIcon (icon )
    app.setWindowIcon(icon)

    lang =config_manager .get ("language","es")
    trans =TRANSLATIONS .get (lang ,TRANSLATIONS ["en"])

    menu =QMenu ()

    settings_action =QAction (trans ["settings"],app )
    settings_action .triggered .connect (lambda :open_settings (window ,config_manager ))
    menu .addAction (settings_action )

    exit_action =QAction (trans ["exit"],app )
    exit_action .triggered .connect (app .quit )
    menu .addAction (exit_action )

    tray_icon .setContextMenu (menu )


    tray_icon .activated .connect (lambda reason :open_settings (window ,config_manager )if reason ==QSystemTrayIcon .Trigger else None )

    tray_icon .show ()
    return tray_icon 

_settings_dialog = None

def _reset_settings_dialog():
    global _settings_dialog
    _settings_dialog = None

def open_settings(window, config_manager):
    global _settings_dialog
    if _settings_dialog is None:
        _settings_dialog = SettingsDialog(config_manager, on_apply_callback=window.reload_settings, overlay_window=window)
        _settings_dialog.finished.connect(_reset_settings_dialog)
        _settings_dialog.show()
    else:
        _settings_dialog.show()
        _settings_dialog.raise_()
        _settings_dialog.activateWindow()

if __name__ =="__main__":
    app =QApplication (sys .argv )
    app .setQuitOnLastWindowClosed (False )

    config_manager =ConfigManager ()
    window =OverlayWindow (config_manager )
    window .show ()

    tray_icon =create_tray_icon (app ,window ,config_manager )


    open_settings (window ,config_manager )

    sys .exit (app .exec ())
