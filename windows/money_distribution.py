from database import DB_conn
from datetime import datetime
from functools import reduce
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from widgets import Button, ComboBox, Field, InputLine
import sys



class MoneyDistribution(object):
    """
    A window where you can see how much money you have save
    in cash and in cards.
    """


    def setupUi(self, MainWindow):
        # Set the database connection
        self.db_conn = DB_conn(dbname="budgetplanner")

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
        self._update_htypes()
        MainWindow.setCentralWidget(self.centralwidget)
    

    def _update_htypes(self):
        """
        It checks if there are htypes that have been added in order
        to show them in this window
        """
        self.add_htype.move(10, 140), self.rm_htype.move(200, 140)
        _, records = self.db_conn.execute(sql_command="SELECT holding_type, institution, amount\
                                                       FROM financial_holdings")
        # Create a section for each holding type.
        ycoord = self.add_htype.y()
        for htype in ["Card", "Cash"]:
            match_records = [r for r in records if r[0] == htype]
            if len(match_records) > 0:
                ycoord = self._create_section(htype, match_records, ycoord)    
        self._get_total_amount(records, ycoord)                
        
    
    def _create_section(self, htype: str, match_rec: list | tuple, ycoord: int) -> int:
        """
        Create a section for a particular htype. 
        """
        Field(cwidget=self.centralwidget, position=(10, ycoord),
              dimensions=(400, 30), texto=f"<u> {htype} </u>", bold=True, 
              pointsize=18, weight=75)
        sep = 40 # Separator of widgets
        if htype == "Card":
            for m_rec in match_rec:
                Field(cwidget=self.centralwidget, position=(10, ycoord + sep),
                          dimensions=(300, 50), texto=m_rec[1])
                InputLine(cwidget=self.centralwidget, position=(10, ycoord + 2*sep), 
                              texto=f"{str(m_rec[-1])} €", readonly=True)
                ycoord += 2*sep
        elif htype == "Cash":
            # If this holding type was registered, then there is only 1 record within
            # the matching records.
            record = match_rec[0]
            InputLine(cwidget=self.centralwidget, position=(10, ycoord + sep),
                      texto=f"{str(record[-1])} €", readonly=True)
            ycoord += sep
        return ycoord + 2*sep


    def _get_total_amount(self, records: list | tuple, ycoord):
        """
        Calculate the accumulative sum of the amounts of 
        the registered htypes  
        """
        Field(cwidget=self.centralwidget, position=(10, ycoord),
              dimensions=(300, 50), texto="TOTAL:", bold=True, 
              pointsize=20, weight=75)
        if len(records) != 0:
            text = reduce(lambda a1, a2: a1 + a2, [r[-1] for r in records])
        else:
            text = 0
        InputLine(cwidget=self.centralwidget, position=(112, ycoord + 5), 
                  texto=f"{text} €", readonly=True)
        # Adjust the position of the buttons to add or remove a htype
        self.add_htype.move(10, ycoord + 90), self.rm_htype.move(200, ycoord + 90)



class HoldingType(object):
    """
    Special window to register a new holding type
    """


    def setupUi(self, MainWindow: QMainWindow):
        # Set the db connection
        self.db_conn = DB_conn(dbname="budgetplanner")

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
                                self.save_htype, hide=True)
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
        record = (
            self.htype_cb.currentText(),
            self.input_inst.text() if len(self.input_inst.text()) != 0 else None,
            self.input_amount.text(),
            datetime.now().date().strftime("%Y-%m-%d")
                  )
        self.db_conn.execute(sql_command="INSERT INTO financial_holdings (holding_type, institution, amount, last_updated) \
                                          VALUES (%s, %s, %s, %s)",
                            parameters=record)
    

    def _clear_fields(self):
        """
        Clear all the fields once the new holding type is stored
        """
        self.input_inst.clear()
        self.input_amount.clear()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = MoneyDistribution()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
