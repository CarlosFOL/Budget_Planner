from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QWidget

class Field(QLabel):
    """
    Field that has to be fill in for the user when
    recording a movement
    """

    def __init__(self, cwidget: QWidget, position: tuple, texto: str):
        super().__init__(cwidget)
        self.position = position
        self.texto = texto
        self._setUp()
    
    def _setUp(self):
        """
        Set the main features of the field
        """
        self.setGeometry(*self.position, 145, 23)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.setFont(font)
        self.setText(self.texto)