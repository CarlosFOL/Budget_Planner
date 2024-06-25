from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QPushButton, QWidget
import sys

class Button(QPushButton):
    """
    It represent an action that can be performed in the app 
    """
    def __init__(self, cwidget: QWidget, coord: tuple, mssg: str):
        super().__init__(cwidget)
        self.x, self.y = coord
        self.mssg = mssg
        self._set_features()

    def _set_features(self):
        """
        Set the main features of a button
        """
        font = QtGui.QFont()
        font.setPointSize(15)
        self.setGeometry(QtCore.QRect(self.x, self.y, 231, 81))
        self.setFont(font)
        self.setText(self.mssg)


class MenuBP(object):
    """
    The menu for the Budget Planner Application.
    """
    def setupUi(self, MainWindow):
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # Welcome message
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.w_mssg = QtWidgets.QLabel(self.centralwidget)
        self.w_mssg.setGeometry(QtCore.QRect(20, 20, 545, 38))
        self.w_mssg.setFont(font)
        self.w_mssg.setText("Welcome to your Expense Manager")
        # Buttons for the actions that can be one through the budget planner
        self.movement = Button(cwidget=self.centralwidget, 
                               coord=(20, 90),
                               mssg="ENTER A MOVEMENT")
        self.money_dist = Button(cwidget=self.centralwidget,
                                 coord=(20, 200),
                                 mssg="MONEY DISTRIBUTION")
        self.exp_summary = Button(cwidget=self.centralwidget,
                                  coord=(20, 310),
                                  mssg="EXPENSE SUMMARY")
        MainWindow.setCentralWidget(self.centralwidget)

   
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MenuBP()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())