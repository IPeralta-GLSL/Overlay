from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication
import sys
import os

app = QApplication(sys.argv)

if os.path.exists("overlay.svg"):
    pixmap = QPixmap("overlay.svg")
    if not pixmap.isNull():
        pixmap.save("overlay.ico", "ICO")
        print("Successfully converted overlay.svg to overlay.ico")
    else:
        print("Failed to load overlay.svg")
else:
    print("overlay.svg not found")
