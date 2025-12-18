import platform
import os
import sys

class AutostartManager:
    def __init__(self, app_name="SystemOverlay"):
        self._app_name = app_name
        self._system = platform.system()

    def is_enabled(self):
        if self._system == "Windows":
            return self._is_enabled_windows()
        elif self._system == "Linux":
            return self._is_enabled_linux()
        return False

    def enable(self):
        if self._system == "Windows":
            return self._enable_windows()
        elif self._system == "Linux":
            return self._enable_linux()
        return False

    def disable(self):
        if self._system == "Windows":
            return self._disable_windows()
        elif self._system == "Linux":
            return self._disable_linux()
        return False

    def _get_executable_path(self):
        if getattr(sys, 'frozen', False):
            return sys.executable
        return f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'

    def _is_enabled_windows(self):
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )
            try:
                winreg.QueryValueEx(key, self._app_name)
                winreg.CloseKey(key)
                return True
            except WindowsError:
                winreg.CloseKey(key)
                return False
        except:
            return False

    def _enable_windows(self):
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, self._app_name, 0, winreg.REG_SZ, self._get_executable_path())
            winreg.CloseKey(key)
            return True
        except:
            return False

    def _disable_windows(self):
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            try:
                winreg.DeleteValue(key, self._app_name)
            except WindowsError:
                pass
            winreg.CloseKey(key)
            return True
        except:
            return False

    def _get_autostart_dir_linux(self):
        return os.path.expanduser("~/.config/autostart")

    def _get_desktop_file_path(self):
        return os.path.join(self._get_autostart_dir_linux(), f"{self._app_name}.desktop")

    def _is_enabled_linux(self):
        return os.path.exists(self._get_desktop_file_path())

    def _enable_linux(self):
        try:
            autostart_dir = self._get_autostart_dir_linux()
            if not os.path.exists(autostart_dir):
                os.makedirs(autostart_dir)
            
            desktop_content = f"""[Desktop Entry]
Type=Application
Name={self._app_name}
Exec={self._get_executable_path()}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
Terminal=false
"""
            with open(self._get_desktop_file_path(), 'w') as f:
                f.write(desktop_content)
            return True
        except:
            return False

    def _disable_linux(self):
        try:
            path = self._get_desktop_file_path()
            if os.path.exists(path):
                os.remove(path)
            return True
        except:
            return False
