from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
import sys
from widgets import Button, Field


class MenuBP(object):
    """
    The menu for the Budget Planner Application.
    """

    def setupUi(self, MainWindow: QMainWindow):
        MainWindow.setGeometry(500, 200, 800, 500)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # Welcome message
        self.w_mssg = Field(cwidget=self.centralwidget, position=(20, 20),
                            texto="Welcome to your Expense Manager",
                            dimensions=(545, 38), pointsize=25,
                            bold=True, weight=75)
        # Buttons for the actions that can be one through the budget planner
        size = (231, 81)
        self.movement = Button(cwidget=self.centralwidget, 
                               position=(20, 120),
                               dimensions=size,
                               pointsize=14,
                               mssg="ENTER A MOVEMENT")
        self.money_dist = Button(cwidget=self.centralwidget,
                                 position=(20, 230),
                                 dimensions=size,
                                 pointsize=14,
                                 mssg="MONEY DISTRIBUTION")
        self.exp_summary = Button(cwidget=self.centralwidget,
                                  position=(20, 340),
                                  dimensions=size,
                                  pointsize=14,
                                  mssg="EXPENSE SUMMARY")
        MainWindow.setCentralWidget(self.centralwidget)

   

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MenuBP()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())