from database import DB_conn
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from widgets import Button, ComboBox, Field, InputLine
import sys


class MoneyDistribution(object):
    """
    A window where you can see how much money you have save
    in cash and in cards.
    """

    def setupUi(self, MainWindow):
        MainWindow.setGeometry(500, 200, 750, 700)
        self.centralwidget = QWidget(MainWindow)
        # Get the htypes that were added to the financial holding table
        # It tells you what you are seeing in this window
        self.indication = Field(cwidget=self.centralwidget, position=(10, 20),
                                texto="Have a look at how much money you have", 
                                dimensions=(590, 32), pointsize=20, 
                                bold=True, weight=75)
        # To return to the menu
        self.back_button = Button(cwidget=self.centralwidget, 
                             position=(10, 65),
                             dimensions=(50, 50),
                             mssg="⟵")
        # To add and remove and holding type
        bsize = (175, 50) # Button's size
        self.add_htype = Button(cwidget=self.centralwidget,
                                position=(10, 140),
                                dimensions=bsize,
                                pointsize=12,
                                mssg="Add Holding")
        self.rm_htype = Button(cwidget=self.centralwidget,
                               position=(200, 140),
                               dimensions=bsize,
                               pointsize=12,
                               mssg="Remove Holding")
        self.update_htypes()
        MainWindow.setCentralWidget(self.centralwidget)
    
    def update_htypes(self):
        """
        It checks if there are htypes that have been added in order
        to show them in this window
        """
        self.add_htype.move(10, 140), self.rm_htype.move(200, 140)
        db_conn = DB_conn(dbname="budgetplanner")
        _, cursor = db_conn.start()
        cursor.execute("""
                    SELECT holding_type, institution, amount
                    FROM financial_holdings
                       """)
        records = [htype for htype in cursor.fetchall()]
        db_conn.end()
        # Display
        ycoord = self.add_htype.y() 
        for htype, inst, amount in records:
            if htype == "Card":
                texto = f"{inst} ({htype})"
            elif htype == "Cash":
                texto = htype
            self.label = Field(cwidget=self.centralwidget,
                               position=(10, ycoord),
                               dimensions=(300, 50),
                               texto=f"{texto} --> {float(amount)} €")
            ycoord += 80
        self.add_htype.move(10, ycoord), self.rm_htype.move(200, ycoord)                
        


class HoldingType(object):
    """
    Special window to register a new holding type
    """

    def setupUi(self, MainWindow: QMainWindow):
        MainWindow.setGeometry(600, 200, 500, 450)
        self.centralwidget = QWidget(MainWindow)
        # It tells you what you are seeing in this window
        self.indication = Field(cwidget=self.centralwidget, position=(10, 10),
                                texto="Fill in the field of the new holding type",
                                dimensions=(400, 32),bold=True, weight=75)
        # Set a htype: cash, card, investment, etc
        self.htype = Field(cwidget=self.centralwidget, position=(10, 60),
                           texto="Holding Type", dimensions=(200, 30))
        self.htype_cb = ComboBox(cwidget=self.centralwidget, position=(10, 100),
                                 options=("Cash", "Card"))
        # The rest of the fields
        self.institution = Field(cwidget=self.centralwidget, position=(10, 160),
                                     texto="Institution", dimensions=(200, 30))
        self.input_inst = InputLine(cwidget=self.centralwidget, position=(10, 200), 
                                     max_char=9)
        self.amount = Field(cwidget=self.centralwidget, position=(10, 260),
                            texto="Amount", dimensions=(200, 30))
        self.input_amount = InputLine(cwidget=self.centralwidget, position=(10, 300),
                                      regex=r'^\d{1,4}(\.\d{0,2})?$')
        # Save a new holding type
        self.save_htype = Button(cwidget=self.centralwidget,
                                 position=(10, 380),
                                 dimensions=(100, 40),
                                 mssg="Save")
        self.save_htype.clicked.connect(self._save_new_htype)
        # Hide them
        self._toggle_visibility(self.institution, self.input_inst, 
                                self.amount, self.input_amount, 
                                self.save_htype, hide =True)
        # Show the corresponding fields
        self.htype_cb.currentIndexChanged.connect(self._show_more_fields)
        MainWindow.setCentralWidget(self.centralwidget)

    def _show_more_fields(self):
        """
        According to the holding type selected, it will display
        all the rest of the widgets or only some of them.
        """
        option = self.htype_cb.currentText()
        if option == "Card":
            # Rearrange the widgets
            self.amount.move(10, self.institution.y() + 100)
            self.input_amount.move(10, self.input_inst.y() + 100)
            self._toggle_visibility(self.institution, self.input_inst, 
                                    self.amount, self.input_amount, self.save_htype)
        elif option == "Cash":
            # Rearrange the widgets
            self.amount.move(10, self.institution.y())
            self.input_amount.move(10, self.input_inst.y())
            self._toggle_visibility(self.institution, self.input_inst, hide=True)
            self._toggle_visibility(self.amount, self.input_amount, self.save_htype)
        self.save_htype.move(10, self.input_amount.y() + 80)

    def _toggle_visibility(self, *args, hide = False):
        """
        To hide or display the sent widgets.
        """
        if hide:
            for field in args:
                field.hide()
        else:
            for field in args:
                field.show()
    
    def _save_new_htype(self):
        """
        Once a button is clicked, the new htype is stored in the
        financial holding table
        """
        db_conn = DB_conn(dbname="budgetplanner")
        conn, cursor = db_conn.start()
        record = (
            self.htype_cb.currentText(),
            self.input_inst.text() if len(self.input_inst.text()) != 0 else None,
            self.input_amount.text(),
            datetime.now().date().strftime("%Y-%m-%d")
                  )
        query = "INSERT INTO financial_holdings (holding_type, institution, amount, last_updated) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, record)
        conn.commit()
        db_conn.end()
        # Clean the fields
        self.input_inst.clear()
        self.input_amount.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = MoneyDistribution()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
