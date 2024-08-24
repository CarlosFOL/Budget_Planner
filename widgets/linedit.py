from PyQt5 import QtGui
from PyQt5.QtWidgets import QLineEdit, QWidget
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp


class InputLine(QLineEdit):
    """
    Widget that allows users to input text of a certain
    length 
    """
    
    def __init__(self, cwidget: QWidget, position: tuple, dimensions: tuple = (190, 41), 
                 texto: str = '', regex: str = None, max_char: int = None, readonly: bool = False):
        super().__init__(cwidget)
        self.position = position
        self.dimensions = dimensions
        self.texto = texto
        self.regex = regex
        self.max_char = max_char
        self.readonly = readonly
        self._setUp()
    
    def _setUp(self):
        """
        Set the maximum amount of characters and the font-size
        into the widget.
        """
        self.setGeometry(*self.position, *self.dimensions)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)
        self.setText(self.texto)
        if self.max_char is not None:
            self.setMaxLength(self.max_char)
        elif self.regex is not None:
            validator = QRegExpValidator(QRegExp(self.regex), self)
            self.setValidator(validator)
        # Set if it's possible to edit the content of the widget.
        self.setReadOnly(self.readonly)