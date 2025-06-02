from PyQt5 import QtGui
from PyQt5.QtWidgets import QComboBox, QWidget

class ComboBox(QComboBox):
    """
    It stores the different options that the user can select 
    in a certain field.
    """

    def __init__(self, cwidget: QWidget, position: tuple, options: tuple = None, dimensions: tuple = None):
        super().__init__(cwidget)
        self.options = options
        self.position = position
        self.dimensions = dimensions if dimensions else (141, 41)  # Default dimensions if not provided
        self._setUp()
        # To ensure that there is no option selected in the combobox
        self.setCurrentIndex(-1)
    
    def _setUp(self):
        """
        Configure the main features for the combo box object
        """
        self.setGeometry(*self.position, *self.dimensions)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.setFont(font)   
        if self.options is None:
            self.addItem("")     
        else:
            self.addItems(self.options)