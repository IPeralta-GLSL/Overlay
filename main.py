print("Starting...")
import sys
from PySide6.QtWidgets import QApplication
from overlay_window import OverlayWindow

if __name__ == "__main__":
    print("Initializing App...")
    app = QApplication(sys.argv)
    window = OverlayWindow()
    window.show()
    print("Window shown")
    sys.exit(app.exec())
