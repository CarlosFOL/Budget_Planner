import pandas as pd
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import QAbstractTableModel, Qt


class Table(QAbstractTableModel):
    """
    It represents a table widget created by using 
    a pandas dataframe
    """

    def __init__(self, data):
        super().__init__()
        self.data = data

    def rowCount(self, parent = None):
        return self.data.shape[0]
    
    def columnCount(self, parent = None):
        return self.data.shape[1]
    
    def data(self, index, role = Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self.data.iloc[index.row(), index.column()])
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return str(self.data.columns[section])
        elif role == Qt.DisplayRole and orientation == Qt.Vertical:
            return str(self.data.index[section])
