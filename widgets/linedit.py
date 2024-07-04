from PyQt5 import QtGui
from PyQt5.QtWidgets import QLineEdit, QWidget
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp


class InputLine(QLineEdit):
    """
    Widget that allows users to input text of a certain
    length 
    """
    
    def __init__(self, cwidget: QWidget, position: tuple, 
                 regex: str = None, max_char: int = None):
        super().__init__(cwidget)
        self.position = position
        self.regex = regex
        self.max_char = max_char
        self._setUp()
    
    def _setUp(self):
        """
        Set the maximum amount of characters and the font-size
        into the widget.
        """
        self.setGeometry(*self.position, 190, 41)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)
        if self.regex == None:
            self.setMaxLength(self.max_char)
        else:
            validator = QRegExpValidator(QRegExp(self.regex), self)
            self.setValidator(validator)