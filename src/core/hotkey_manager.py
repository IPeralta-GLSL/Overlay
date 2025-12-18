from PySide6.QtCore import QObject, Signal
import platform

class HotkeyManager(QObject):
    toggle_overlay = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._listener = None
        self._registered = False

    def register_hotkey(self, hotkey_str):
        self.unregister_hotkey()
        try:
            from pynput import keyboard
            keys = self._parse_hotkey(hotkey_str)
            if not keys:
                return False

            self._current_keys = set()
            self._target_keys = keys

            def on_press(key):
                try:
                    if hasattr(key, 'char'):
                        self._current_keys.add(key.char.lower() if key.char else None)
                    else:
                        self._current_keys.add(key)
                    if self._check_hotkey():
                        self.toggle_overlay.emit()
                except:
                    pass

            def on_release(key):
                try:
                    if hasattr(key, 'char'):
                        self._current_keys.discard(key.char.lower() if key.char else None)
                    else:
                        self._current_keys.discard(key)
                except:
                    pass

            self._listener = keyboard.Listener(on_press=on_press, on_release=on_release)
            self._listener.start()
            self._registered = True
            return True
        except ImportError:
            return False
        except:
            return False

    def _parse_hotkey(self, hotkey_str):
        from pynput import keyboard
        keys = set()
        parts = hotkey_str.lower().replace(" ", "").split("+")
        for part in parts:
            if part in ["ctrl", "control"]:
                keys.add(keyboard.Key.ctrl_l)
            elif part == "shift":
                keys.add(keyboard.Key.shift_l)
            elif part in ["alt", "option"]:
                keys.add(keyboard.Key.alt_l)
            elif part in ["cmd", "command", "win", "super"]:
                keys.add(keyboard.Key.cmd)
            elif len(part) == 1:
                keys.add(part)
            elif part.startswith("f") and part[1:].isdigit():
                fkey = getattr(keyboard.Key, part, None)
                if fkey:
                    keys.add(fkey)
        return keys

    def _check_hotkey(self):
        from pynput import keyboard
        for key in self._target_keys:
            if key in self._current_keys:
                continue
            if key == keyboard.Key.ctrl_l and keyboard.Key.ctrl_r in self._current_keys:
                continue
            if key == keyboard.Key.shift_l and keyboard.Key.shift_r in self._current_keys:
                continue
            if key == keyboard.Key.alt_l and keyboard.Key.alt_r in self._current_keys:
                continue
            return False
        return True

    def unregister_hotkey(self):
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._registered = False

    def is_registered(self):
        return self._registered
