from database import DB_conn
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QStyle, QWidget
import sys
from widgets import ComboBox, Field, InputLine, Button


class EnterExpense(object):
    """
    """
    

    def setupUi(self, MainWindow: QMainWindow):
        MainWindow.setGeometry(500, 200, 750, 700)
        self.centralwidget = QWidget(MainWindow)
        # It tells you what you can do on this window
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.indication = QLabel(self.centralwidget)
        self.indication.setGeometry(QtCore.QRect(10, 5, 421, 32))
        self.indication.setFont(font)
        self.indication.setText("Fill in the fields of the movement")
        # Back button to the menu
        self.back_button = Button(cwidget=self.centralwidget, 
                             position=(10, 60),
                             dimensions=(50, 50),
                             mssg="⟵")
        # To select the movement type
        self.mov_type = Field(cwidget=self.centralwidget, 
                              position=(10, 140),
                              texto="Type")
        # Combo box
        self.options_mtype = ComboBox(cwidget=self.centralwidget, 
                                      options=("Income", "Expense"),
                                      position=(10, 180))
        self.options_mtype.currentIndexChanged.connect(self._update_categories)

        # It shows the categories of incomes and expenses that there are.
        self.cat_mov = Field(cwidget=self.centralwidget, 
                              position=(10, 260),
                              texto="Category")
        # Combo box
        self.categories = ComboBox(cwidget=self.centralwidget,
                                   position=(10, 300))
        
        # The movement description
        self.mov_des = Field(cwidget=self.centralwidget, 
                              position=(10, 380),
                              texto="Description")
        # Space to specify a brief description of the movement
        self.description = InputLine(cwidget=self.centralwidget,
                                     position=(10, 420),
                                     max_char=25)

        # Set the amount
        self.amount_mov = Field(cwidget=self.centralwidget, 
                              position=(10, 500),
                              texto="Amount (€)")
        # The amount of the movement
        self.amount = InputLine(cwidget=self.centralwidget,
                                position=(10, 540),
                                # Regular expression: It starts with a number of 1-4 digits 
                                # and followed by decimal part of 1-2 digits.
                                regex=r'^\d{1,4}(\.\d{0,2})?$')

        # Send the movement to the database
        self.send_mv = Button(cwidget=self.centralwidget,
                              position=(10, 615),
                              dimensions=(200, 41),
                              mssg="Enviar")
        self.send_mv.clicked.connect(self._input_movement)
        
        MainWindow.setCentralWidget(self.centralwidget)


    def _update_categories(self):
        """
        Update the categories according to the 
        movement type selected
        """
        current_type = self.options_mtype.currentText()
        self.categories.clear()
        if current_type == "Expense":
            self.categories.addItems(["Alojamiento", "Servicios", "Comida", 
                                      "Telefonia", "Transporte", "Universidad",
                                      "Ocio", "Gym", "Otros"])
        elif current_type == "Income":
            self.categories.addItems(["Salario", "Transferencia"])


    def _input_movement(self) -> tuple:
        """
        Register a movement into the table Movements
        """
        db_conn = DB_conn(dbname="budgetplanner")
        conn, cursor = db_conn.start()
        record = (
            datetime.now().date().strftime("%Y-%m-%d"),
            self.options_mtype.currentText(),
            self.categories.currentText(),
            self.description.text(),
            float(self.amount.text())
        )
        query = "INSERT INTO movements (date, type, category, description, amount) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, record)
        conn.commit()
        db_conn.end()
        # Remove the content of the fields
        self.description.clear()
        self.amount.clear()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = EnterExpense()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())