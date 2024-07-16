from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5 import QtGui

class Button(QPushButton):
    """
    It represent an action that can be performed in the app 
    """
    def __init__(self, cwidget: QWidget, position: tuple, 
                 dimensions: tuple, pointsize: int = 15, mssg: str = "", ):
        super().__init__(cwidget)
        self.position = position
        self.dimensions = dimensions
        self.pointsize = pointsize
        self.mssg = mssg
        self._setUp()

    def _setUp(self):
        """
        Set the main features of a button
        """
        font = QtGui.QFont()
        font.setPointSize(self.pointsize)
        self.setGeometry(*self.position, *self.dimensions)
        self.setFont(font)
        self.setText(self.mssg)