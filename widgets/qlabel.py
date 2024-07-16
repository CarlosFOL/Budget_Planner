from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QWidget

class Field(QLabel):
    """
    Field that has to be fill in for the user when
    recording a movement
    """

    def __init__(self, cwidget: QWidget, position: tuple, texto: str, 
                 dimensions: tuple, pointsize: int = 15, 
                 bold: bool = False, weight: int = 20):
        super().__init__(cwidget)
        self.position = position
        self.texto = texto
        self.dimensions = dimensions
        self.pointsize = pointsize
        self.bold = bold
        self.weight = weight
        self._setUp()
    
    def _setUp(self):
        """
        Set the main features of the field
        """
        self.setGeometry(*self.position, *self.dimensions)
        font = QtGui.QFont()
        font.setPointSize(self.pointsize)
        font.setBold(self.bold)
        font.setWeight(self.weight)
        self.setFont(font)
        self.setText(self.texto)