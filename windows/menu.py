from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
import sys
from widgets import Button


class MenuBP(object):
    """
    The menu for the Budget Planner Application.
    """

    def setupUi(self, MainWindow: QMainWindow):
        MainWindow.setGeometry(500, 200, 800, 500)
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
        size = (231, 81)
        self.movement = Button(cwidget=self.centralwidget, 
                               position=(20, 90),
                               dimensions=size,
                               mssg="ENTER A MOVEMENT")
        self.money_dist = Button(cwidget=self.centralwidget,
                                 position=(20, 200),
                                 dimensions=size,
                                 mssg="MONEY DISTRIBUTION")
        self.exp_summary = Button(cwidget=self.centralwidget,
                                  position=(20, 310),
                                  dimensions=size,
                                  mssg="EXPENSE SUMMARY")
        MainWindow.setCentralWidget(self.centralwidget)

   

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MenuBP()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())