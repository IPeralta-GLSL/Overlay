from PySide6.QtCore import QObject, Signal, Slot, QThread
import platform

class KeyboardListenerThread(QThread):
    hotkey_pressed = Signal()

    def __init__(self, hotkey_str, parent=None):
        super().__init__(parent)
        self._hotkey_str = hotkey_str
        self._running = True
        self._current_keys = set()
        self._target_keys = set()
        self._hotkey_triggered = False

    def _normalize_key(self, key):
        from pynput import keyboard
        if hasattr(key, 'char') and key.char:
            return key.char.lower()
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            return 'ctrl'
        if key in (keyboard.Key.shift_l, keyboard.Key.shift_r):
            return 'shift'
        if key in (keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
            return 'alt'
        if key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
            return 'cmd'
        return key

    def _parse_hotkey(self):
        from pynput import keyboard
        keys = set()
        parts = self._hotkey_str.lower().replace(" ", "").split("+")
        for part in parts:
            if part in ["ctrl", "control"]:
                keys.add('ctrl')
            elif part == "shift":
                keys.add('shift')
            elif part in ["alt", "option"]:
                keys.add('alt')
            elif part in ["cmd", "command", "win", "super"]:
                keys.add('cmd')
            elif len(part) == 1:
                keys.add(part)
            elif part.startswith("f") and part[1:].isdigit():
                fkey = getattr(keyboard.Key, part, None)
                if fkey:
                    keys.add(fkey)
        return keys

    def _check_hotkey(self):
        for key in self._target_keys:
            if key not in self._current_keys:
                return False
        return True

    def run(self):
        from pynput import keyboard
        self._target_keys = self._parse_hotkey()
        if not self._target_keys:
            return

        def on_press(key):
            if not self._running:
                return False
            try:
                normalized = self._normalize_key(key)
                if normalized is not None:
                    self._current_keys.add(normalized)
                if not self._hotkey_triggered and self._check_hotkey():
                    self._hotkey_triggered = True
                    self.hotkey_pressed.emit()
            except:
                pass

        def on_release(key):
            if not self._running:
                return False
            try:
                normalized = self._normalize_key(key)
                if normalized is not None:
                    self._current_keys.discard(normalized)
                self._hotkey_triggered = False
            except:
                pass

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            while self._running:
                listener.join(0.1)

    def stop(self):
        self._running = False
        self.wait(500)


class HotkeyManager(QObject):
    toggle_overlay = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._listener_thread = None
        self._registered = False

    def register_hotkey(self, hotkey_str):
        self.unregister_hotkey()
        try:
            self._listener_thread = KeyboardListenerThread(hotkey_str, self)
            self._listener_thread.hotkey_pressed.connect(self.toggle_overlay)
            self._listener_thread.start()
            self._registered = True
            return True
        except:
            return False

    def unregister_hotkey(self):
        if self._listener_thread:
            self._listener_thread.stop()
            self._listener_thread = None
        self._registered = False

    def is_registered(self):
        return self._registered
