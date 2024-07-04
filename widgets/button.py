from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5 import QtGui

class Button(QPushButton):
    """
    It represent an action that can be performed in the app 
    """
    def __init__(self, cwidget: QWidget, position: tuple, dimensions: tuple, mssg: str):
        super().__init__(cwidget)
        self.position = position
        self.dimensions = dimensions
        self.mssg = mssg
        self._setUp()

    def _setUp(self):
        """
        Set the main features of a button
        """
        font = QtGui.QFont()
        font.setPointSize(15)
        self.setGeometry(*self.position, *self.dimensions)
        self.setFont(font)
        self.setText(self.mssg)