from PySide6.QtCore import QObject, Signal, QThread
import urllib.request
import json
import re

class UpdateChecker(QObject):
    update_available = Signal(str, str)
    check_complete = Signal(bool)
    error_occurred = Signal(str)

    def __init__(self, owner, repo, current_version, parent=None):
        super().__init__(parent)
        self._owner = owner
        self._repo = repo
        self._current_version = current_version
        self._thread = None

    def check_for_updates(self):
        self._thread = UpdateCheckThread(self._owner, self._repo, self._current_version)
        self._thread.update_available.connect(self.update_available.emit)
        self._thread.check_complete.connect(self.check_complete.emit)
        self._thread.error_occurred.connect(self.error_occurred.emit)
        self._thread.start()

    def get_download_url(self):
        return f"https://github.com/{self._owner}/{self._repo}/releases/latest"


class UpdateCheckThread(QThread):
    update_available = Signal(str, str)
    check_complete = Signal(bool)
    error_occurred = Signal(str)

    def __init__(self, owner, repo, current_version):
        super().__init__()
        self._owner = owner
        self._repo = repo
        self._current_version = current_version

    def run(self):
        try:
            url = f"https://api.github.com/repos/{self._owner}/{self._repo}/releases/latest"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "SystemOverlay-UpdateChecker")
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "").lstrip("v")
                release_notes = data.get("body", "")
                if self._compare_versions(latest_version, self._current_version) > 0:
                    self.update_available.emit(latest_version, release_notes)
                    self.check_complete.emit(True)
                else:
                    self.check_complete.emit(False)
        except Exception as e:
            self.error_occurred.emit(str(e))
            self.check_complete.emit(False)

    def _compare_versions(self, v1, v2):
        def parse(v):
            return [int(x) for x in re.sub(r'[^0-9.]', '', v).split('.') if x]
        
        v1_parts = parse(v1)
        v2_parts = parse(v2)
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            p1 = v1_parts[i] if i < len(v1_parts) else 0
            p2 = v2_parts[i] if i < len(v2_parts) else 0
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
        return 0
