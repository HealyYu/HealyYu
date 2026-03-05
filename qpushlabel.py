from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal 
# 自定义QPushLabel
class QPushLabel(QLabel):
    
    clicked = pyqtSignal()
    def __init__(self, parent=None):
        super(QPushLabel, self).__init__(parent)
    # def clicked(self):
    #     self.button_clicked_signal.emit()
    def mousePressEvent(self, event):
        self.clicked.emit()
    # def connect_customized_slot(self, func):
    #     self.button_clicked_signal.connect(func)