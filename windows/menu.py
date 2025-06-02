from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
import sys
from widgets import Button, Field


class MenuBP(object):
    """
    The menu for the Budget Planner Application.
    """

    def setupUi(self, MainWindow: QMainWindow):
        # Set window properties
        MainWindow.setGeometry(500, 200, 900, 600)
        MainWindow.setWindowTitle("Budget Planner")
        MainWindow.setStyleSheet("background-color: #f5f5f7;")
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # Welcome message
        self.w_mssg = Field(cwidget=self.centralwidget, position=(20, 20),
                            texto="Welcome to your Expense Manager",
                            dimensions=(860, 80), pointsize=28,
                            bold=True, weight=75)
        self.w_mssg.setStyleSheet("color: #2c3e50; padding: 10px;")
        
        # Buttons for the actions
        size = (280, 90)
        button_style = """QPushButton {
                            background-color: #2e7d32;  /* Dark green */
                            color: white;
                            border-radius: 10px;
                            font-size: 16px;
                            font-weight: bold;
                            padding: 10px;
                        }
                        QPushButton:hover {
                            background-color: #4caf50;  /* Medium green */
                        }"""
        
        # Left side buttons
        self.movement = Button(cwidget=self.centralwidget, 
                               position=(50, 120),
                               dimensions=size,
                               pointsize=14,
                               mssg="ENTER A MOVEMENT")
        self.movement.setStyleSheet(button_style)
        
        self.money_dist = Button(cwidget=self.centralwidget,
                                 position=(50, 240),
                                 dimensions=size,
                                 pointsize=14,
                                 mssg="MONEY DISTRIBUTION")
        self.money_dist.setStyleSheet(button_style)
        
        self.exp_summary = Button(cwidget=self.centralwidget,
                                  position=(50, 360),
                                  dimensions=size,
                                  pointsize=14,
                                  mssg="EXPENSE SUMMARY")
        self.exp_summary.setStyleSheet(button_style)
        
        # Right side - Add search button
        self.search_btn = Button(cwidget=self.centralwidget,
                                position=(50, 480),
                                dimensions=size,
                                pointsize=14,
                                mssg="SEARCH MOVEMENTS")
        self.search_btn.setStyleSheet(button_style)
        
        # App description
        description = "Manage your finances with ease and security"
        self.app_desc = Field(cwidget=self.centralwidget, 
                             position=(400, 120),
                             dimensions=(450, 350),
                             texto=description,
                             pointsize=14)
        self.app_desc.setStyleSheet("color: #7f8c8d; padding: 20px;")
        
        MainWindow.setCentralWidget(self.centralwidget)

   

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MenuBP()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
