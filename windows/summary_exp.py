from database import DB_conn
from PyQt5 import QtCore, QtGui, QtWidgets
from widgets import Button, ComboBox, Field
import sys

class SummaryExp(object):
    """
    It divides the expenses I have made during a particular
    season into categories and shows them in tabular form. 
    """

    def setupUi(self, MainWindow):
        MainWindow.setGeometry(300, 200, 1400, 620)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # It tells you what you are seeing in this window
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(10, 5, 460, 28))
        self.title.setFont(font)
        self.title.setText("See how much you spend over the period")
        # Back button to the menu
        self.back_button = Button(cwidget=self.centralwidget, 
                             position=(10, 60),
                             dimensions=(50, 50),
                             mssg="⟵")
        # To choose the season
        self.season_f = Field(cwidget=self.centralwidget,
                            position=(10, 140),
                            texto="Season")
        self._set_seasons()
        self.table = QtWidgets.QTableView(MainWindow)
        self.table.setGeometry(50, 250, 1295, 325)
        MainWindow.setCentralWidget(self.centralwidget)

    def _set_seasons(self):
        """
        Get all the seasons and save them into a combobox 
        """
        self.seasons_cb = ComboBox(cwidget=self.centralwidget,
                                 position=(10, 180))
        db_conn = DB_conn(dbname="budgetplanner")
        # Start a db connection
        _, cursor = db_conn.start()
        cursor.execute("SELECT sid FROM seasons")
        seasons = [str(s[0]) for s in cursor.fetchall()]
        db_conn.end()
        # Store the value into the combobox
        self.seasons_cb.addItems(seasons)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = SummaryExp()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())