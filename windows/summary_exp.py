from PyQt5 import QtCore, QtGui, QtWidgets
from widgets import ComboBox, Field
import sys

class SummaryExp(object):
    """
    """

    def setupUi(self, MainWindow):
        MainWindow.setGeometry(500, 200, 800, 500)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # It tells you what you are seeing in this window
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(10, 20, 460, 28))
        self.title.setFont(font)
        self.title.setText("See how much you spend over the period")
        # To choose the season
        self.seasons_cb = ComboBox(cwidget=self.centralwidget,
                                 position=(10, 100))
        self.season_f = Field(cwidget=self.centralwidget,
                            position=(10, 70),
                            texto="Season`")
        MainWindow.setCentralWidget(self.centralwidget)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = SummaryExp()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
