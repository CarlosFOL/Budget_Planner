from database import DB_conn
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from .secondary_wind import SecondaryWindow
import sys
from widgets import Button, ComboBox, Field, InputLine, Message_Box


class EnterExpense(SecondaryWindow):
    """
    Window that displays the fields that you have to fill in in order
    to register a new movement, either an income or expense. 
    """
    

    def setupUi(self):
        # Set the database connection
        self.db_conn = DB_conn(dbname="budget_planner")

        self.main_window.setGeometry(500, 200, 750, 700)
        self.centralwidget = QWidget(self.main_window)
        # It tells you what you can do on this window
        self.indication = Field(cwidget=self.centralwidget, position=(10, 5),
                                texto="Fill in the fields of the movement",
                                dimensions=(421, 32), pointsize=20,
                                bold=True, weight=75)
        # Back button to the menu
        self.back_button = Button(cwidget=self.centralwidget, 
                             position=(10, 60),                
                             dimensions=(50, 50),
                             mssg="⟵")
        self.back_button.clicked.connect(self._back_menu)
        # To select the movement type
        self.mov_type = Field(cwidget=self.centralwidget, 
                              position=(10, 140),
                              dimensions=(145, 23),
                              texto="Type")
        self.options_mtype = ComboBox(cwidget=self.centralwidget, 
                                      options=("Income", "Expense"),
                                      position=(10, 180))
        self.options_mtype.currentIndexChanged.connect(self._update_categories)

        # It shows the categories either of incomes or expenses that are available.
        self.cat_mov = Field(cwidget=self.centralwidget, 
                              position=(10, 260),
                              dimensions=(145, 23),
                              texto="Category")
        self.categories = ComboBox(cwidget=self.centralwidget,
                                   position=(10, 300))
        
        # The movement description
        self.mov_des = Field(cwidget=self.centralwidget, 
                              position=(10, 380),
                              dimensions=(145, 23),
                              texto="Description")
        # Space to specify a brief description of the movement
        self.description = InputLine(cwidget=self.centralwidget,
                                     position=(10, 420),
                                     max_char=25)

        # Set the amount
        self.amount_mov = Field(cwidget=self.centralwidget, 
                              position=(10, 500),
                              dimensions=(145, 23),
                              texto="Amount (€)")
        # The amount of the movement
        self.amount = InputLine(cwidget=self.centralwidget,
                                position=(10, 540),
                                # Regular expression: It starts with a number of 1-4 digits 
                                # and followed by decimal part of 1-2 digits.
                                regex=r'^\d{1,4}(\.\d{0,2})?$')
        self._display_htypes_cb()

        # Send the movement to the database
        self.send_mv = Button(cwidget=self.centralwidget,
                              position=(10, 615),
                              dimensions=(200, 41),
                              mssg="Enviar")
        self.send_mv.clicked.connect(self._insert_movement)
        
        self.main_window.setCentralWidget(self.centralwidget)


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


    def _display_htypes_cb(self):
        """
        Display a combobox with the registered holding types in
        the financial holding table.
        """
        outcome = self.db_conn.execute("SELECT holding_type, institution \
                                        FROM financial_holdings")
        self.htype_cb = ComboBox(cwidget=self.centralwidget, 
                                 position=(240, 540),
                                # Set comprehension to avoid duplicates
                                 options={record[0] for record in outcome})
        self.inst_cb = ComboBox(cwidget=self.centralwidget, 
                                position=(420, 540),
                                options=[inst for htype, inst in outcome if htype == "Card"])
        self.inst_cb.hide()
        self.htype_cb.currentIndexChanged.connect(self._extra_field)


    def _extra_field(self):
        """
        In case of the movement has been performed with card, 
        it will display a new combobox with the registered
        insitution names. 
        """
        if self.htype_cb.currentText() == "Card":
            self.inst_cb.show()
        elif self.htype_cb.currentText() == "Cash" and self.inst_cb.isVisible():
            self.inst_cb.hide()


    def _insert_movement(self) -> tuple:
        """
        Register a movement into the table Movements,
        """
        inputs = (datetime.now().date().strftime("%Y-%m-%d"),
                  self.options_mtype.currentText(),
                  self.categories.currentText(), 
                  self.description.text(), 
                  self.amount.text())
        query = "INSERT INTO movements (date, type, category, description, amount)\
                 VALUES ('%s', '%s', '%s', '%s', %s)"
        if not self._empty_fields(inputs):
            query = query%inputs # Add the values into the query
            status = self.db_conn.execute(commands=[query, self._upd_balance()])
            if status == "Ok":
                Message_Box(title="Operation successfully completed",
                            text="The transaction has been done.",
                            icon="Information")
            self.refresh()
        else:
            Message_Box(title="Incomplete", 
                        text="Please, complete all the movement's fields",
                        icon="Critical")


    def _empty_fields(self, record: tuple) -> bool:
        """
        It checks if all the movement's fields have been filled in.
        In this way, we avoid to store an incomplete record. 
        """
        for element in record:
            if element == "":
                return True
        return False


    def _upd_balance(self):
        """
        Get the hold type used and institution (only if appropiate) 
        for that movement and reduce its balance
        """
        operator = {"Income": "+", "Expense": "-"}
        htype = self.htype_cb.currentText()
        query = f"UPDATE financial_holdings\
                  SET\
                    amount = amount {operator[self.options_mtype.currentText()]} {self.amount.text()}\
                    , last_updated = '{datetime.now().date().strftime("%Y-%m-%d")}'\
                WHERE holding_type = '{htype}'"
        if htype == "Card":
            query += f" AND institution = '{self.inst_cb.currentText()}'"
        return query
    

    def refresh(self):
        """
        Clear all the fields once a movement is stored or
        if the EnterExpense window is reopened.
        """
        self.options_mtype.setCurrentIndex(-1)
        self.description.clear()
        self.amount.clear()
        self.htype_cb.setCurrentIndex(-1)
        self.inst_cb.hide()

        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = EnterExpense()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
