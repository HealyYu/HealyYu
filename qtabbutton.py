from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal 
# 自定义QPushLabel
class QTabButton(QWidget):
    
    clicked = pyqtSignal()
    def __init__(self, parent=None):
        super(QTabButton, self).__init__(parent)
    def mousePressEvent(self, event):
        self.clicked.emit()